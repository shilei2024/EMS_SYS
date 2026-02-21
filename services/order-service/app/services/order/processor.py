"""
订单处理服务
"""
import logging
from typing import Any, Dict, List, Optional

from app.ocr.processor import OCRProcessor, OCRResult
from app.models.order import Order, OrderItem, OrderStatus

logger = logging.getLogger(__name__)


class OrderProcessor:
    """订单处理器"""

    def __init__(self):
        self.ocr_processor = OCRProcessor()

    async def process_image(self, image_data: bytes) -> OCRResult:
        """处理图片订单"""
        return await self.ocr_processor.process_image(image_data)

    async def process_pdf(self, pdf_data: bytes) -> OCRResult:
        """处理PDF订单"""
        return await self.ocr_processor.process_pdf(pdf_data)

    async def validate_order(self, order: Order) -> Dict[str, Any]:
        """验证订单数据"""
        errors = []
        warnings = []

        # 验证客户信息
        if not order.customer_name:
            errors.append("缺少客户名称")

        # 验证订单金额
        if order.total_amount and order.total_amount < 0:
            errors.append("订单金额不能为负数")

        # 验证行项目
        if not order.items or len(order.items) == 0:
            errors.append("订单没有行项目")

        # 验证行项目数据
        for item in order.items:
            if item.quantity <= 0:
                errors.append(f"行项目 {item.line_number}: 数量必须大于0")

            if not item.mpn and not item.description:
                warnings.append(f"行项目 {item.line_number}: 缺少MPN和描述")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

    async def calculate_order_totals(self, order: Order) -> Order:
        """计算订单金额"""
        total = 0.0

        for item in order.items:
            # 如果没有单独的总价，根据数量和单价计算
            if item.total_price == 0 and item.quantity > 0 and item.unit_price > 0:
                item.total_price = item.quantity * item.unit_price

            total += item.total_price

        order.total_amount = total

        # 如果行项目有多个币种，这里需要处理（简化处理）

        return order


class OrderRepository:
    """订单仓储接口"""

    async def create(self, order: Order) -> Order:
        """创建订单"""
        raise NotImplementedError()

    async def get(self, order_id: str) -> Optional[Order]:
        """获取订单"""
        raise NotImplementedError()

    async def update(self, order: Order) -> Order:
        """更新订单"""
        raise NotImplementedError()

    async def delete(self, order_id: str) -> bool:
        """删除订单"""
        raise NotImplementedError()

    async def list(
        self,
        status: Optional[OrderStatus] = None,
        customer_name: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> List[Order]:
        """列出订单"""
        raise NotImplementedError()

    async def count(self, status: Optional[OrderStatus] = None) -> int:
        """统计订单数量"""
        raise NotImplementedError()
