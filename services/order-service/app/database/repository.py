"""
订单仓储实现
"""
import logging
from datetime import datetime
from typing import List, Optional
from decimal import Decimal

import asyncpg
from pydantic import Field

from app.database.connection import get_db_connection
from app.models.order import Order, OrderItem, OrderStatus, OrderPriority, ReviewStatus

logger = logging.getLogger(__name__)


class OrderRepository:
    """订单仓储类"""

    async def create(self, order: Order) -> Order:
        """
        创建订单

        Args:
            order: 订单对象

        Returns:
            创建的订单
        """
        async with get_db_connection() as conn:
            try:
                # 开启事务
                async with conn.transaction():
                    # 插入主表
                    await conn.execute(
                        """
                        INSERT INTO orders (
                            id, order_number, source_id, customer_name, customer_email,
                            customer_phone, customer_address, total_amount, currency,
                            status, priority, ocr_confidence, ocr_raw_text,
                            ocr_structured_data, review_notes, reviewed_by, reviewed_at,
                            notes, created_at, updated_at
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20)
                        """,
                        order.id,
                        order.order_number,
                        order.source_id,
                        order.customer_name,
                        order.customer_email,
                        order.customer_phone,
                        order.customer_address,
                        order.total_amount,
                        order.currency,
                        order.status.value,
                        order.priority.value if order.priority else None,
                        order.ocr_confidence,
                        order.ocr_raw_text,
                        order.ocr_structured_data,
                        order.review_notes,
                        order.reviewed_by,
                        order.reviewed_at,
                        order.notes,
                        order.created_at,
                        order.updated_at
                    )

                    # 插入行项目
                    for item in order.items:
                        await conn.execute(
                            """
                            INSERT INTO order_items (
                                id, order_id, line_number, mpn, manufacturer,
                                description, quantity, unit_price, total_price,
                                ocr_confidence, review_status, review_notes,
                                matched_component_id, created_at, updated_at
                            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
                            """,
                            item.id,
                            order.id,
                            item.line_number,
                            item.mpn,
                            item.manufacturer,
                            item.description,
                            item.quantity,
                            item.unit_price,
                            item.total_price,
                            item.ocr_confidence,
                            item.review_status.value,
                            item.review_notes,
                            item.matched_component_id,
                            item.created_at,
                            item.updated_at
                        )

                logger.info(f"订单创建成功：{order.order_number}")
                return order

            except Exception as e:
                logger.error(f"创建订单失败：{str(e)}")
                raise

    async def get(self, order_id: str) -> Optional[Order]:
        """
        获取订单

        Args:
            order_id: 订单 ID

        Returns:
            订单对象，不存在返回 None
        """
        async with get_db_connection() as conn:
            try:
                # 获取主表数据
                row = await conn.fetchrow(
                    "SELECT * FROM orders WHERE id = $1", order_id
                )

                if not row:
                    return None

                # 获取行项目
                items_rows = await conn.fetch(
                    "SELECT * FROM order_items WHERE order_id = $1 ORDER BY line_number",
                    order_id
                )

                items = [self._row_to_order_item(row) for row in items_rows]

                return self._row_to_order(row, items)

            except Exception as e:
                logger.error(f"获取订单失败：{str(e)}")
                raise

    async def update(self, order: Order) -> Order:
        """
        更新订单

        Args:
            order: 订单对象

        Returns:
            更新后的订单
        """
        async with get_db_connection() as conn:
            try:
                async with conn.transaction():
                    # 更新主表
                    await conn.execute(
                        """
                        UPDATE orders SET
                            order_number = $2,
                            source_id = $3,
                            customer_name = $4,
                            customer_email = $5,
                            customer_phone = $6,
                            customer_address = $7,
                            total_amount = $8,
                            currency = $9,
                            status = $10,
                            priority = $11,
                            ocr_confidence = $12,
                            ocr_raw_text = $13,
                            ocr_structured_data = $14,
                            review_notes = $15,
                            reviewed_by = $16,
                            reviewed_at = $17,
                            notes = $18,
                            updated_at = $19
                        WHERE id = $1
                        """,
                        order.id,
                        order.order_number,
                        order.source_id,
                        order.customer_name,
                        order.customer_email,
                        order.customer_phone,
                        order.customer_address,
                        order.total_amount,
                        order.currency,
                        order.status.value,
                        order.priority.value if order.priority else None,
                        order.ocr_confidence,
                        order.ocr_raw_text,
                        order.ocr_structured_data,
                        order.review_notes,
                        order.reviewed_by,
                        order.reviewed_at,
                        order.notes,
                        datetime.utcnow()
                    )

                    # 更新行项目
                    for item in order.items:
                        await conn.execute(
                            """
                            UPDATE order_items SET
                                line_number = $3,
                                mpn = $4,
                                manufacturer = $5,
                                description = $6,
                                quantity = $7,
                                unit_price = $8,
                                total_price = $9,
                                ocr_confidence = $10,
                                review_status = $11,
                                review_notes = $12,
                                matched_component_id = $13,
                                updated_at = $14
                            WHERE id = $1 AND order_id = $2
                            """,
                            item.id,
                            order.id,
                            item.line_number,
                            item.mpn,
                            item.manufacturer,
                            item.description,
                            item.quantity,
                            item.unit_price,
                            item.total_price,
                            item.ocr_confidence,
                            item.review_status.value,
                            item.review_notes,
                            item.matched_component_id,
                            datetime.utcnow()
                        )

                logger.info(f"订单更新成功：{order.order_number}")
                return order

            except Exception as e:
                logger.error(f"更新订单失败：{str(e)}")
                raise

    async def delete(self, order_id: str) -> bool:
        """
        删除订单

        Args:
            order_id: 订单 ID

        Returns:
            是否删除成功
        """
        async with get_db_connection() as conn:
            try:
                # 先删除子表（外键级联删除也可以，但这里显式处理）
                await conn.execute(
                    "DELETE FROM order_items WHERE order_id = $1", order_id
                )

                # 删除主表
                result = await conn.execute(
                    "DELETE FROM orders WHERE id = $1", order_id
                )

                deleted = result == "DELETE 1"
                if deleted:
                    logger.info(f"订单删除成功：{order_id}")
                else:
                    logger.warning(f"订单不存在：{order_id}")

                return deleted

            except Exception as e:
                logger.error(f"删除订单失败：{str(e)}")
                raise

    async def list(
        self,
        status: Optional[OrderStatus] = None,
        customer_name: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 20
    ) -> List[Order]:
        """
        获取订单列表

        Args:
            status: 状态过滤
            customer_name: 客户名称过滤
            start_date: 开始日期
            end_date: 结束日期
            page: 页码
            page_size: 每页数量

        Returns:
            订单列表
        """
        async with get_db_connection() as conn:
            try:
                # 构建查询条件
                conditions = ["1=1"]
                params = []
                param_index = 1

                if status:
                    conditions.append(f"status = ${param_index}")
                    params.append(status.value)
                    param_index += 1

                if customer_name:
                    conditions.append(f"customer_name ILIKE ${param_index}")
                    params.append(f"%{customer_name}%")
                    param_index += 1

                if start_date:
                    conditions.append(f"created_at >= ${param_index}")
                    params.append(start_date)
                    param_index += 1

                if end_date:
                    conditions.append(f"created_at <= ${param_index}")
                    params.append(end_date)
                    param_index += 1

                where_clause = " AND ".join(conditions)

                # 分页
                offset = (page - 1) * page_size

                # 查询主表
                query = f"""
                    SELECT * FROM orders
                    WHERE {where_clause}
                    ORDER BY created_at DESC
                    LIMIT ${param_index} OFFSET ${param_index + 1}
                """
                params.extend([page_size, offset])

                rows = await conn.fetch(query, *params)

                orders = []
                for row in rows:
                    # 获取行项目
                    items_rows = await conn.fetch(
                        "SELECT * FROM order_items WHERE order_id = $1 ORDER BY line_number",
                        row["id"]
                    )
                    items = [self._row_to_order_item(r) for r in items_rows]
                    orders.append(self._row_to_order(row, items))

                return orders

            except Exception as e:
                logger.error(f"获取订单列表失败：{str(e)}")
                raise

    async def count(
        self,
        status: Optional[OrderStatus] = None,
        customer_name: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> int:
        """
        统计订单数量

        Args:
            status: 状态过滤
            customer_name: 客户名称过滤
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            订单数量
        """
        async with get_db_connection() as conn:
            try:
                # 构建查询条件
                conditions = ["1=1"]
                params = []
                param_index = 1

                if status:
                    conditions.append(f"status = ${param_index}")
                    params.append(status.value)
                    param_index += 1

                if customer_name:
                    conditions.append(f"customer_name ILIKE ${param_index}")
                    params.append(f"%{customer_name}%")
                    param_index += 1

                if start_date:
                    conditions.append(f"created_at >= ${param_index}")
                    params.append(start_date)
                    param_index += 1

                if end_date:
                    conditions.append(f"created_at <= ${param_index}")
                    params.append(end_date)
                    param_index += 1

                where_clause = " AND ".join(conditions)

                query = f"SELECT COUNT(*) FROM orders WHERE {where_clause}"
                result = await conn.fetchval(query, *params)

                return result or 0

            except Exception as e:
                logger.error(f"统计订单数量失败：{str(e)}")
                raise

    async def get_by_order_number(self, order_number: str) -> Optional[Order]:
        """
        根据订单号获取订单

        Args:
            order_number: 订单号

        Returns:
            订单对象
        """
        async with get_db_connection() as conn:
            try:
                row = await conn.fetchrow(
                    "SELECT * FROM orders WHERE order_number = $1", order_number
                )

                if not row:
                    return None

                items_rows = await conn.fetch(
                    "SELECT * FROM order_items WHERE order_id = $1 ORDER BY line_number",
                    row["id"]
                )

                items = [self._row_to_order_item(r) for r in items_rows]
                return self._row_to_order(row, items)

            except Exception as e:
                logger.error(f"根据订单号获取订单失败：{str(e)}")
                raise

    def _row_to_order(self, row: asyncpg.Record, items: List[OrderItem]) -> Order:
        """将数据库行转换为订单对象"""
        return Order(
            id=row["id"],
            order_number=row["order_number"],
            source_id=row["source_id"],
            customer_name=row["customer_name"],
            customer_email=row["customer_email"],
            customer_phone=row["customer_phone"],
            customer_address=row["customer_address"],
            total_amount=float(row["total_amount"]) if row["total_amount"] else None,
            currency=row["currency"],
            status=OrderStatus(row["status"]),
            priority=OrderPriority(row["priority"]) if row["priority"] else OrderPriority.NORMAL,
            ocr_confidence=float(row["ocr_confidence"]) if row["ocr_confidence"] else None,
            ocr_raw_text=row["ocr_raw_text"],
            ocr_structured_data=row["ocr_structured_data"],
            review_notes=row["review_notes"],
            reviewed_by=row["reviewed_by"],
            reviewed_at=row["reviewed_at"],
            notes=row["notes"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            items=items
        )

    def _row_to_order_item(self, row: asyncpg.Record) -> OrderItem:
        """将数据库行转换为订单行项目对象"""
        return OrderItem(
            id=row["id"],
            order_id=row["order_id"],
            line_number=row["line_number"],
            mpn=row["mpn"],
            manufacturer=row["manufacturer"],
            description=row["description"],
            quantity=row["quantity"],
            unit_price=float(row["unit_price"]) if row["unit_price"] else 0.0,
            total_price=float(row["total_price"]) if row["total_price"] else 0.0,
            ocr_confidence=float(row["ocr_confidence"]) if row["ocr_confidence"] else 0.0,
            review_status=ReviewStatus(row["review_status"]),
            review_notes=row["review_notes"],
            matched_component_id=row["matched_component_id"],
            created_at=row["created_at"],
            updated_at=row["updated_at"]
        )


# 仓储实例
_order_repository: Optional[OrderRepository] = None


def get_order_repository() -> OrderRepository:
    """获取订单仓储实例"""
    global _order_repository
    if _order_repository is None:
        _order_repository = OrderRepository()
    return _order_repository
