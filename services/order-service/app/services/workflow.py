"""
订单工作流引擎
实现订单状态转换和自动化处理
"""
import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from app.models.order import Order, OrderStatus

logger = logging.getLogger(__name__)


class WorkflowAction(str, Enum):
    """工作流操作"""
    SUBMIT = "submit"              # 提交订单
    APPROVE = "approve"           # 审核通过
    REJECT = "reject"              # 拒绝订单
    NEEDS_REVIEW = "needs_review" # 需要人工审核
    COMPLETE = "complete"          # 完成订单
    CANCEL = "cancel"              # 取消订单
    RETRY = "retry"               # 重试处理


class WorkflowEvent(str, Enum):
    """工作流事件"""
    ORDER_CREATED = "order_created"
    OCR_COMPLETED = "ocr_completed"
    REVIEW_COMPLETED = "review_completed"
    PAYMENT_CONFIRMED = "payment_confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"


@dataclass
class WorkflowTransition:
    """工作流状态转换"""
    from_status: OrderStatus
    to_status: OrderStatus
    action: WorkflowAction
    conditions: List[Callable] = field(default_factory=list)
    handlers: List[Callable] = field(default_factory=list)


@dataclass
class WorkflowResult:
    """工作流执行结果"""
    success: bool
    from_status: OrderStatus
    to_status: OrderStatus
    message: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class WorkflowEngine:
    """订单工作流引擎"""

    def __init__(self):
        self.transitions = self._build_transition_map()
        self.event_handlers: Dict[WorkflowEvent, List[Callable]] = {}

    def _build_transition_map(self) -> Dict[WorkflowAction, List[WorkflowTransition]]:
        """构建状态转换映射"""
        return {
            WorkflowAction.SUBMIT: [
                WorkflowTransition(
                    from_status=OrderStatus.PENDING,
                    to_status=OrderStatus.PROCESSING,
                    action=WorkflowAction.SUBMIT,
                    conditions=[],
                    handlers=[self._handle_order_submitted]
                )
            ],
            WorkflowAction.APPROVE: [
                WorkflowTransition(
                    from_status=OrderStatus.REVIEW_NEEDED,
                    to_status=OrderStatus.APPROVED,
                    action=WorkflowAction.APPROVE,
                    conditions=[],
                    handlers=[self._handle_order_approved]
                ),
                WorkflowTransition(
                    from_status=OrderStatus.PROCESSING,
                    to_status=OrderStatus.APPROVED,
                    action=WorkflowAction.APPROVE,
                    conditions=[self._check_auto_approve_conditions],
                    handlers=[self._handle_order_approved]
                )
            ],
            WorkflowAction.REJECT: [
                WorkflowTransition(
                    from_status=OrderStatus.REVIEW_NEEDED,
                    to_status=OrderStatus.REJECTED,
                    action=WorkflowAction.REJECT,
                    conditions=[],
                    handlers=[self._handle_order_rejected]
                ),
                WorkflowTransition(
                    from_status=OrderStatus.PROCESSING,
                    to_status=OrderStatus.REJECTED,
                    action=WorkflowAction.REJECT,
                    conditions=[],
                    handlers=[self._handle_order_rejected]
                )
            ],
            WorkflowAction.NEEDS_REVIEW: [
                WorkflowTransition(
                    from_status=OrderStatus.PROCESSING,
                    to_status=OrderStatus.REVIEW_NEEDED,
                    action=WorkflowAction.NEEDS_REVIEW,
                    conditions=[],
                    handlers=[self._handle_review_required]
                )
            ],
            WorkflowAction.COMPLETE: [
                WorkflowTransition(
                    from_status=OrderStatus.APPROVED,
                    to_status=OrderStatus.COMPLETED,
                    action=WorkflowAction.COMPLETE,
                    conditions=[],
                    handlers=[self._handle_order_completed]
                )
            ],
            WorkflowAction.CANCEL: [
                WorkflowTransition(
                    from_status=OrderStatus.PENDING,
                    to_status=OrderStatus.CANCELLED,
                    action=WorkflowAction.CANCEL,
                    conditions=[],
                    handlers=[self._handle_order_cancelled]
                ),
                WorkflowTransition(
                    from_status=OrderStatus.PROCESSING,
                    to_status=OrderStatus.CANCELLED,
                    action=WorkflowAction.CANCEL,
                    conditions=[],
                    handlers=[self._handle_order_cancelled]
                )
            ],
            WorkflowAction.RETRY: [
                WorkflowTransition(
                    from_status=OrderStatus.REJECTED,
                    to_status=OrderStatus.PENDING,
                    action=WorkflowAction.RETRY,
                    conditions=[],
                    handlers=[self._handle_order_retried]
                )
            ]
        }

    async def execute(
        self,
        order: Order,
        action: WorkflowAction,
        context: Optional[Dict[str, Any]] = None
    ) -> WorkflowResult:
        """
        执行工作流操作

        Args:
            order: 订单对象
            action: 工作流操作
            context: 额外的上下文数据

        Returns:
            工作流执行结果
        """
        context = context or {}

        # 查找有效的转换
        transitions = self.transitions.get(action, [])

        valid_transition = None
        for transition in transitions:
            if transition.from_status == order.status:
                # 检查条件
                conditions_met = True
                for condition in transition.conditions:
                    try:
                        if not await self._evaluate_condition(condition, order, context):
                            conditions_met = False
                            break
                    except Exception as e:
                        logger.warning(f"条件评估失败: {str(e)}")
                        conditions_met = False
                        break

                if conditions_met:
                    valid_transition = transition
                    break

        if not valid_transition:
            return WorkflowResult(
                success=False,
                from_status=order.status,
                to_status=order.status,
                message=f"无法从状态 {order.status.value} 执行操作 {action.value}",
                metadata=context
            )

        # 记录旧状态
        old_status = order.status

        # 执行前置处理器
        try:
            for handler in valid_transition.handlers:
                await self._execute_handler(handler, order, context)
        except Exception as e:
            logger.error(f"工作流处理器执行失败: {str(e)}")
            return WorkflowResult(
                success=False,
                from_status=old_status,
                to_status=order.status,
                message=f"工作流处理器执行失败: {str(e)}",
                metadata=context
            )

        # 更新订单状态
        order.status = valid_transition.to_status
        order.updated_at = datetime.utcnow()

        # 记录审核信息
        if action in [WorkflowAction.APPROVE, WorkflowAction.REJECT]:
            order.reviewed_at = datetime.utcnow()
            order.review_notes = context.get("review_notes")

        return WorkflowResult(
            success=True,
            from_status=old_status,
            to_status=valid_transition.to_status,
            message=f"订单状态从 {old_status.value} 变更为 {valid_transition.to_status.value}",
            metadata=context
        )

    async def _evaluate_condition(
        self,
        condition: Callable,
        order: Order,
        context: Dict[str, Any]
    ) -> bool:
        """评估条件"""
        try:
            if asyncio.iscoroutinefunction(condition):
                return await condition(order, context)
            return condition(order, context)
        except Exception as e:
            logger.error(f"条件评估异常: {str(e)}")
            return False

    async def _execute_handler(
        self,
        handler: Callable,
        order: Order,
        context: Dict[str, Any]
    ) -> None:
        """执行处理器"""
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(order, context)
            else:
                handler(order, context)
        except Exception as e:
            logger.error(f"处理器执行异常: {str(e)}")
            raise

    # ==================== 条件函数 ====================

    def _check_auto_approve_conditions(self, order: Order, context: Dict[str, Any]) -> bool:
        """检查是否满足自动审核条件"""
        # 检查OCR置信度
        if order.ocr_confidence and order.ocr_confidence >= 0.9:
            return True

        # 检查是否有需要审核的行项目
        for item in order.items:
            if item.review_status.value in ["pending", "needs_review"]:
                return False

        return True

    # ==================== 处理器函数 ====================

    async def _handle_order_submitted(self, order: Order, context: Dict[str, Any]) -> None:
        """处理订单提交"""
        logger.info(f"订单 {order.order_number} 已提交")

        # 触发后续处理
        # 例如：调用OCR服务
        await self._trigger_ocr_processing(order)

    async def _handle_order_approved(self, order: Order, context: Dict[str, Any]) -> None:
        """处理订单审核通过"""
        logger.info(f"订单 {order.order_number} 已审核通过")

        # 触发后续流程
        # 例如：通知客户、创建采购单等

    async def _handle_order_rejected(self, order: Order, context: Dict[str, Any]) -> None:
        """处理订单被拒绝"""
        logger.info(f"订单 {order.order_number} 已被拒绝: {context.get('review_notes')}")

        # 触发通知
        await self._notify_order_rejected(order)

    async def _handle_review_required(self, order: Order, context: Dict[str, Any]) -> None:
        """处理需要人工审核"""
        logger.info(f"订单 {order.order_number} 需要人工审核")

        # 触发审核通知
        await self._notify_review_required(order)

    async def _handle_order_completed(self, order: Order, context: Dict[str, Any]) -> None:
        """处理订单完成"""
        logger.info(f"订单 {order.order_number} 已完成")

    async def _handle_order_cancelled(self, order: Order, context: Dict[str, Any]) -> None:
        """处理订单取消"""
        logger.info(f"订单 {order.order_number} 已取消")

        # 释放库存等资源

    async def _handle_order_retried(self, order: Order, context: Dict[str, Any]) -> None:
        """处理订单重试"""
        logger.info(f"订单 {order.order_number} 已重试")

    # ==================== 辅助方法 ====================

    async def _trigger_ocr_processing(self, order: Order) -> None:
        """触发OCR处理"""
        # TODO: 实现OCR处理调用
        logger.info(f"触发订单 {order.order_number} 的OCR处理")

    async def _notify_order_rejected(self, order: Order) -> None:
        """通知订单被拒绝"""
        # TODO: 实现通知（邮件、企业微信等）
        pass

    async def _notify_review_required(self, order: Order) -> None:
        """通知需要审核"""
        # TODO: 实现审核通知
        pass

    def register_event_handler(self, event: WorkflowEvent, handler: Callable) -> None:
        """注册事件处理器"""
        if event not in self.event_handlers:
            self.event_handlers[event] = []
        self.event_handlers[event].append(handler)

    async def trigger_event(self, event: WorkflowEvent, order: Order, context: Dict[str, Any]) -> None:
        """触发事件"""
        handlers = self.event_handlers.get(event, [])
        for handler in handlers:
            try:
                await self._execute_handler(handler, order, context)
            except Exception as e:
                logger.error(f"事件处理器执行失败: {str(e)}")


# 工作流引擎单例
_workflow_engine: Optional[WorkflowEngine] = None


def get_workflow_engine() -> WorkflowEngine:
    """获取工作流引擎实例"""
    global _workflow_engine
    if _workflow_engine is None:
        _workflow_engine = WorkflowEngine()
    return _workflow_engine
