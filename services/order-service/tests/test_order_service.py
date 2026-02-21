"""
订单服务测试模块
"""
import pytest
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from app.models.order import Order, OrderItem, OrderStatus, OrderPriority, ReviewStatus
from app.ocr.processor import OCRProcessor, OCRResult, OCRConfidenceLevel
from app.services.order.processor import OrderProcessor
from app.services.workflow import WorkflowEngine, WorkflowAction


# ==================== Order 模型测试 ====================

class TestOrderModel:
    """订单模型测试"""

    def test_create_order(self):
        """测试创建订单"""
        order = Order(
            id="test-order-1",
            order_number="PO-20260221-001",
            customer_name="Test Customer",
            customer_email="test@example.com",
            status=OrderStatus.PENDING,
            priority=OrderPriority.NORMAL
        )

        assert order.id == "test-order-1"
        assert order.order_number == "PO-20260221-001"
        assert order.customer_name == "Test Customer"
        assert order.status == OrderStatus.PENDING
        assert order.priority == OrderPriority.NORMAL
        assert order.currency == "CNY"
        assert order.items == []

    def test_order_with_items(self):
        """测试带行项目的订单"""
        order = Order(
            id="test-order-2",
            order_number="PO-20260221-002",
            customer_name="Test Customer",
            status=OrderStatus.PENDING,
            items=[
                OrderItem(
                    id="item-1",
                    order_id="test-order-2",
                    line_number=1,
                    mpn="STM32F407VGT6",
                    manufacturer="STMicroelectronics",
                    description="ARM Cortex-M4 MCU",
                    quantity=1000,
                    unit_price=5.20,
                    total_price=5200.00
                )
            ]
        )

        assert len(order.items) == 1
        assert order.items[0].mpn == "STM32F407VGT6"
        assert order.items[0].quantity == 1000
        assert order.items[0].total_price == 5200.00


# ==================== OrderStatus 枚举测试 ====================

class TestOrderStatus:
    """订单状态测试"""

    def test_order_status_values(self):
        """测试订单状态值"""
        assert OrderStatus.PENDING.value == "pending"
        assert OrderStatus.PROCESSING.value == "processing"
        assert OrderStatus.REVIEW_NEEDED.value == "review_needed"
        assert OrderStatus.APPROVED.value == "approved"
        assert OrderStatus.REJECTED.value == "rejected"
        assert OrderStatus.COMPLETED.value == "completed"
        assert OrderStatus.CANCELLED.value == "cancelled"


# ==================== WorkflowEngine 测试 ====================

class TestWorkflowEngine:
    """工作流引擎测试"""

    @pytest.mark.asyncio
    async def test_approve_order(self):
        """测试审核通过订单"""
        engine = WorkflowEngine()
        order = Order(
            id="test-order-3",
            order_number="PO-20260221-003",
            customer_name="Test Customer",
            status=OrderStatus.REVIEW_NEEDED
        )

        result = await engine.execute(order, WorkflowAction.APPROVE)

        assert result.success is True
        assert result.to_status == OrderStatus.APPROVED
        assert order.status == OrderStatus.APPROVED

    @pytest.mark.asyncio
    async def test_reject_order(self):
        """测试拒绝订单"""
        engine = WorkflowEngine()
        order = Order(
            id="test-order-4",
            order_number="PO-20260221-004",
            customer_name="Test Customer",
            status=OrderStatus.REVIEW_NEEDED
        )

        result = await engine.execute(order, WorkflowAction.REJECT, {"review_notes": "测试拒绝"})

        assert result.success is True
        assert result.to_status == OrderStatus.REJECTED
        assert order.status == OrderStatus.REJECTED
        assert order.review_notes == "测试拒绝"

    @pytest.mark.asyncio
    async def test_invalid_transition(self):
        """测试无效状态转换"""
        engine = WorkflowEngine()
        order = Order(
            id="test-order-5",
            order_number="PO-20260221-005",
            customer_name="Test Customer",
            status=OrderStatus.APPROVED
        )

        # 已审核的订单不能再次审核
        result = await engine.execute(order, WorkflowAction.APPROVE)

        assert result.success is False
        assert order.status == OrderStatus.APPROVED  # 状态不变

    @pytest.mark.asyncio
    async def test_cancel_order(self):
        """测试取消订单"""
        engine = WorkflowEngine()
        order = Order(
            id="test-order-6",
            order_number="PO-20260221-006",
            customer_name="Test Customer",
            status=OrderStatus.PENDING
        )

        result = await engine.execute(order, WorkflowAction.CANCEL)

        assert result.success is True
        assert result.to_status == OrderStatus.CANCELLED
        assert order.status == OrderStatus.CANCELLED


# ==================== OCR Processor 测试 ====================

class TestOCRProcessor:
    """OCR 处理器测试"""

    def test_confidence_level_calculation(self):
        """测试置信度等级计算"""
        processor = OCRProcessor()

        # 模拟置信度等级计算
        assert processor._get_confidence_level(0.95) == OCRConfidenceLevel.HIGH
        assert processor._get_confidence_level(0.85) == OCRConfidenceLevel.MEDIUM
        assert processor._get_confidence_level(0.50) == OCRConfidenceLevel.LOW

    def test_mock_ocr_text_generation(self):
        """测试模拟 OCR 文本生成"""
        processor = OCRProcessor()
        mock_text = processor._generate_mock_ocr_text()

        assert "采购订单" in mock_text
        assert "订单号:" in mock_text
        assert "STM32" in mock_text

    def test_default_structure_creation(self):
        """测试默认结构创建"""
        processor = OCRProcessor()
        raw_text = "测试文本"
        result = processor._create_default_structure(raw_text)

        assert result["order_number"] is None
        assert result["customer_name"] is None
        assert result["line_items"] == []
        assert "error" in result


# ==================== Order Processor 测试 ====================

class TestOrderProcessorService:
    """订单处理服务测试"""

    @pytest.mark.asyncio
    async def test_validate_order_success(self):
        """测试订单验证 - 成功情况"""
        processor = OrderProcessor()
        order = Order(
            id="test-order-7",
            order_number="PO-20260221-007",
            customer_name="Test Customer",
            total_amount=1000.00,
            status=OrderStatus.PENDING,
            items=[
                OrderItem(
                    id="item-1",
                    order_id="test-order-7",
                    line_number=1,
                    mpn="STM32F407VGT6",
                    quantity=100,
                    unit_price=10.0,
                    total_price=1000.0
                )
            ]
        )

        result = await processor.validate_order(order)

        assert result["valid"] is True
        assert len(result["errors"]) == 0

    @pytest.mark.asyncio
    async def test_validate_order_missing_customer(self):
        """测试订单验证 - 缺少客户名称"""
        processor = OrderProcessor()
        order = Order(
            id="test-order-8",
            order_number="PO-20260221-008",
            customer_name=None,  # 缺少客户名称
            status=OrderStatus.PENDING
        )

        result = await processor.validate_order(order)

        assert result["valid"] is False
        assert "缺少客户名称" in result["errors"]

    @pytest.mark.asyncio
    async def test_validate_order_no_items(self):
        """测试订单验证 - 没有行项目"""
        processor = OrderProcessor()
        order = Order(
            id="test-order-9",
            order_number="PO-20260221-009",
            customer_name="Test Customer",
            status=OrderStatus.PENDING,
            items=[]
        )

        result = await processor.validate_order(order)

        assert result["valid"] is False
        assert "订单没有行项目" in result["errors"]

    @pytest.mark.asyncio
    async def test_calculate_order_totals(self):
        """测试订单金额计算"""
        processor = OrderProcessor()
        order = Order(
            id="test-order-10",
            order_number="PO-20260221-010",
            customer_name="Test Customer",
            status=OrderStatus.PENDING,
            items=[
                OrderItem(
                    id="item-1",
                    order_id="test-order-10",
                    line_number=1,
                    quantity=100,
                    unit_price=10.0,
                    total_price=0  # 需要计算
                ),
                OrderItem(
                    id="item-2",
                    order_id="test-order-10",
                    line_number=2,
                    quantity=50,
                    unit_price=20.0,
                    total_price=1000.0
                )
            ]
        )

        result = await processor.calculate_order_totals(order)

        assert result.items[0].total_price == 1000.0  # 100 * 10
        assert result.items[1].total_price == 1000.0  # 保持不变
        assert result.total_amount == 2000.0


# ==================== 集成测试 ====================

class TestOrderIntegration:
    """订单集成测试"""

    @pytest.mark.asyncio
    async def test_full_order_workflow(self):
        """测试完整订单工作流"""
        # 1. 创建订单
        order = Order(
            id="integration-test-1",
            order_number="PO-20260221-INT001",
            customer_name="Integration Test Customer",
            customer_email="integration@test.com",
            status=OrderStatus.PENDING,
            priority=OrderPriority.HIGH
        )

        # 2. 验证订单
        processor = OrderProcessor()
        validation = await processor.validate_order(order)
        assert validation["valid"] is False  # 没有行项目

        # 3. 添加行项目
        order.items.append(
            OrderItem(
                id="int-item-1",
                order_id="integration-test-1",
                line_number=1,
                mpn="TEST-MPN-001",
                manufacturer="Test Manufacturer",
                quantity=100,
                unit_price=5.0,
                total_price=500.0
            )
        )

        # 4. 重新验证
        validation = await processor.validate_order(order)
        assert validation["valid"] is True

        # 5. 计算总额
        order = await processor.calculate_order_totals(order)
        assert order.total_amount == 500.0

        # 6. 执行工作流 - 提交订单
        engine = WorkflowEngine()
        result = await engine.execute(order, WorkflowAction.SUBMIT)
        assert result.success is True
        assert order.status == OrderStatus.PROCESSING

        # 7. 模拟 OCR 处理完成，需要审核
        order.ocr_confidence = 0.65  # 低于自动审核阈值
        result = await engine.execute(order, WorkflowAction.NEEDS_REVIEW)
        assert result.success is True
        assert order.status == OrderStatus.REVIEW_NEEDED

        # 8. 人工审核通过
        result = await engine.execute(order, WorkflowAction.APPROVE, {"review_notes": "审核通过"})
        assert result.success is True
        assert order.status == OrderStatus.APPROVED
        assert order.review_notes == "审核通过"


# ==================== 性能测试 ====================

class TestPerformance:
    """性能测试"""

    def test_order_creation_performance(self):
        """测试订单创建性能"""
        import time

        start = time.time()

        orders = []
        for i in range(1000):
            order = Order(
                id=f"perf-test-{i}",
                order_number=f"PO-PERF-{i:06d}",
                customer_name=f"Customer {i}",
                status=OrderStatus.PENDING
            )
            orders.append(order)

        elapsed = time.time() - start

        assert len(orders) == 1000
        assert elapsed < 1.0  # 应该在 1 秒内完成

    def test_large_order_items(self):
        """测试大订单性能（大量行项目）"""
        import time

        items = []
        for i in range(100):
            items.append(
                OrderItem(
                    id=f"item-{i}",
                    order_id="large-order",
                    line_number=i + 1,
                    mpn=f"MPN-{i:06d}",
                    manufacturer=f"Manufacturer {i}",
                    quantity=100,
                    unit_price=10.0,
                    total_price=1000.0
                )
            )

        start = time.time()

        order = Order(
            id="large-order",
            order_number="PO-LARGE-001",
            customer_name="Large Order Customer",
            status=OrderStatus.PENDING,
            items=items
        )

        elapsed = time.time() - start

        assert len(order.items) == 100
        assert elapsed < 0.5  # 应该在 0.5 秒内完成


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
