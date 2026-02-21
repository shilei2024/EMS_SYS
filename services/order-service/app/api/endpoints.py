"""
订单 API 端点
"""
import asyncio
import io
import logging
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from PIL import Image
import magic

from app.models.order import Order, OrderItem, OrderStatus, OrderPriority, ReviewStatus
from app.services.order.processor import OrderProcessor
from app.services.workflow import WorkflowEngine, WorkflowAction, WorkflowResult
from app.database.repository import get_order_repository

logger = logging.getLogger(__name__)

router = APIRouter()
order_repository = get_order_repository()
workflow_engine = WorkflowEngine()


# ==================== 文件验证 ====================

def validate_file_upload(file: UploadFile, max_size: int = 10 * 1024 * 1024) -> tuple[bytes, str]:
    """
    验证上传的文件

    Args:
        file: 上传的文件对象
        max_size: 最大文件大小（字节），默认 10MB

    Returns:
        (file_contents, validated_content_type)

    Raises:
        HTTPException: 文件验证失败
    """
    # 允许的文件扩展名
    allowed_extensions = {'.pdf', '.png', '.jpg', '.jpeg'}
    # 允许的 MIME 类型
    allowed_mime_types = {
        'application/pdf': '.pdf',
        'image/png': '.png',
        'image/jpeg': '.jpg',
    }

    # 检查文件扩展名
    filename = file.filename or ""
    ext = '.' + filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型：{ext}，支持：{', '.join(allowed_extensions)}"
        )

    # 读取文件内容
    contents = file.file.read()

    # 检查文件大小
    if len(contents) > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"文件过大：{len(contents) / 1024 / 1024:.1f}MB，最大支持{max_size / 1024 / 1024}MB"
        )

    # 使用 python-magic 验证实际 MIME 类型（通过文件内容）
    actual_mime = magic.from_buffer(contents, mime=True)
    if actual_mime not in allowed_mime_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的文件内容：MIME 类型 {actual_mime} 不被支持"
        )

    # 验证文件扩展名与 MIME 类型是否匹配
    expected_ext = allowed_mime_types[actual_mime]
    if ext != expected_ext:
        logger.warning(f"文件扩展名 ({ext}) 与 MIME 类型 ({actual_mime}) 不匹配")

    # 额外验证：如果是图片，使用 PIL 验证
    if actual_mime.startswith('image/'):
        try:
            img = Image.open(io.BytesIO(contents))
            img.verify()  # 验证图片完整性
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"图片文件损坏或格式无效：{str(e)}"
            )

    return contents, actual_mime


# ==================== 请求模型 ====================

class OrderCreateRequest(BaseModel):
    """创建订单请求"""
    customer_name: str = Field(..., min_length=1, max_length=200)
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_address: Optional[str] = None
    notes: Optional[str] = None
    priority: str = "normal"


class OrderUpdateRequest(BaseModel):
    """更新订单请求"""
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_address: Optional[str] = None
    notes: Optional[str] = None
    priority: Optional[str] = None


class OrderReviewRequest(BaseModel):
    """订单审核请求"""
    action: str = Field(..., description="审核操作：approve, reject, needs_review")
    review_notes: Optional[str] = None


class LineItemUpdateRequest(BaseModel):
    """更新订单行项目请求"""
    mpn: Optional[str] = None
    manufacturer: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[int] = Field(None, gt=0)
    unit_price: Optional[float] = Field(None, ge=0)
    review_status: Optional[str] = None
    review_notes: Optional[str] = None


# ==================== 响应模型 ====================

class OCRProcessResponse(BaseModel):
    """OCR 处理响应"""
    order_id: str
    status: str
    ocr_confidence: float
    message: str
    requires_manual_review: bool = False


class OrderListResponse(BaseModel):
    """订单列表响应"""
    total: int
    page: int
    page_size: int
    orders: List[Order]


# ==================== 订单 API 端点 ====================

@router.post("/orders", response_model=Order, status_code=status.HTTP_201_CREATED)
async def create_order(request: OrderCreateRequest):
    """创建新订单"""
    order_id = str(uuid.uuid4())

    order = Order(
        id=order_id,
        order_number=f"PO-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}",
        customer_name=request.customer_name,
        customer_email=request.customer_email,
        customer_phone=request.customer_phone,
        customer_address=request.customer_address,
        notes=request.notes,
        priority=OrderPriority(request.priority),
        status=OrderStatus.PENDING,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    # 保存到数据库
    await order_repository.create(order)

    return order


@router.get("/orders", response_model=OrderListResponse)
async def list_orders(
    page: int = 1,
    page_size: int = 20,
    status_filter: Optional[str] = None,
    customer_name: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """获取订单列表"""
    # 查询参数验证
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 20

    # 转换状态枚举
    status_enum = None
    if status_filter:
        try:
            status_enum = OrderStatus(status_filter)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的状态值：{status_filter}"
            )

    # 转换日期
    start_dt = None
    end_dt = None
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的日期格式：{start_date}"
            )
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的日期格式：{end_date}"
            )

    # 获取订单列表和总数
    orders, total = await asyncio.gather(
        order_repository.list(
            status=status_enum,
            customer_name=customer_name,
            start_date=start_dt,
            end_date=end_dt,
            page=page,
            page_size=page_size
        ),
        order_repository.count(
            status=status_enum,
            customer_name=customer_name,
            start_date=start_dt,
            end_date=end_dt
        )
    )

    return OrderListResponse(
        total=total,
        page=page,
        page_size=page_size,
        orders=orders
    )


@router.get("/orders/{order_id}", response_model=Order)
async def get_order(order_id: str):
    """获取订单详情"""
    order = await order_repository.get(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"订单 {order_id} 不存在"
        )
    return order


@router.put("/orders/{order_id}", response_model=Order)
async def update_order(order_id: str, request: OrderUpdateRequest):
    """更新订单"""
    order = await order_repository.get(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"订单 {order_id} 不存在"
        )

    # 更新字段
    if request.customer_name is not None:
        order.customer_name = request.customer_name
    if request.customer_email is not None:
        order.customer_email = request.customer_email
    if request.customer_phone is not None:
        order.customer_phone = request.customer_phone
    if request.customer_address is not None:
        order.customer_address = request.customer_address
    if request.notes is not None:
        order.notes = request.notes
    if request.priority is not None:
        order.priority = OrderPriority(request.priority)

    order.updated_at = datetime.utcnow()

    # 保存到数据库
    await order_repository.update(order)

    return order


@router.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(order_id: str):
    """删除订单"""
    deleted = await order_repository.delete(order_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"订单 {order_id} 不存在"
        )
    return None


@router.post("/orders/{order_id}/review", response_model=Order)
async def review_order(order_id: str, request: OrderReviewRequest, background_tasks: BackgroundTasks):
    """审核订单"""
    # 验证操作
    valid_actions = ["approve", "reject", "needs_review"]
    if request.action not in valid_actions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的审核操作：{request.action}，必须是 {valid_actions}"
        )

    # 获取订单
    order = await order_repository.get(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"订单 {order_id} 不存在"
        )

    # 映射动作到枚举
    action_map = {
        "approve": WorkflowAction.APPROVE,
        "reject": WorkflowAction.REJECT,
        "needs_review": WorkflowAction.NEEDS_REVIEW
    }

    # 执行工作流
    result: WorkflowResult = await workflow_engine.execute(
        order,
        action_map[request.action],
        {"review_notes": request.review_notes}
    )

    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.message
        )

    # 保存更新后的订单
    await order_repository.update(order)

    return order


@router.post("/orders/{order_id}/items", response_model=OrderItem, status_code=status.HTTP_201_CREATED)
async def add_order_item(order_id: str, item: LineItemUpdateRequest):
    """添加订单行项目"""
    order = await order_repository.get(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"订单 {order_id} 不存在"
        )

    # 创建新行项目
    new_item = OrderItem(
        id=str(uuid.uuid4()),
        order_id=order_id,
        line_number=len(order.items) + 1,
        mpn=item.mpn,
        manufacturer=item.manufacturer,
        description=item.description,
        quantity=item.quantity or 0,
        unit_price=item.unit_price or 0.0,
        total_price=(item.quantity or 0) * (item.unit_price or 0.0),
        review_status=ReviewStatus.PENDING,
        review_notes=item.review_notes,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    order.items.append(new_item)
    order.updated_at = datetime.utcnow()

    # 保存更新
    await order_repository.update(order)

    return new_item


@router.put("/orders/{order_id}/items/{item_id}", response_model=OrderItem)
async def update_order_item(order_id: str, item_id: str, request: LineItemUpdateRequest):
    """更新订单行项目"""
    order = await order_repository.get(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"订单 {order_id} 不存在"
        )

    # 查找行项目
    target_item = None
    for item in order.items:
        if item.id == item_id:
            target_item = item
            break

    if not target_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"订单项目 {item_id} 不存在"
        )

    # 更新字段
    if request.mpn is not None:
        target_item.mpn = request.mpn
    if request.manufacturer is not None:
        target_item.manufacturer = request.manufacturer
    if request.description is not None:
        target_item.description = request.description
    if request.quantity is not None:
        target_item.quantity = request.quantity
    if request.unit_price is not None:
        target_item.unit_price = request.unit_price
        target_item.total_price = target_item.quantity * target_item.unit_price
    if request.review_status is not None:
        try:
            target_item.review_status = ReviewStatus(request.review_status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的审核状态：{request.review_status}"
            )
    if request.review_notes is not None:
        target_item.review_notes = request.review_notes

    target_item.updated_at = datetime.utcnow()
    order.updated_at = datetime.utcnow()

    # 保存更新
    await order_repository.update(order)

    return target_item


@router.delete("/orders/{order_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order_item(order_id: str, item_id: str):
    """删除订单行项目"""
    order = await order_repository.get(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"订单 {order_id} 不存在"
        )

    # 查找并删除行项目
    original_count = len(order.items)
    order.items = [item for item in order.items if item.id != item_id]

    if len(order.items) == original_count:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"订单项目 {item_id} 不存在"
        )

    # 重新排序行号
    for idx, item in enumerate(order.items):
        item.line_number = idx + 1

    order.updated_at = datetime.utcnow()

    # 保存更新
    await order_repository.update(order)

    return None


# ==================== OCR 处理端点 ====================

@router.post("/orders/ocr", response_model=OCRProcessResponse)
async def process_order_ocr(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    auto_approve_threshold: float = Form(0.9)
):
    """
    通过 OCR 处理订单文件

    支持格式：PDF, PNG, JPG, JPEG
    """
    import magic
    from PIL import Image
    import io

    # 允许的文件扩展名
    allowed_extensions = {'.pdf', '.png', '.jpg', '.jpeg'}
    # 允许的 MIME 类型
    allowed_mime_types = {
        'application/pdf': '.pdf',
        'image/png': '.png',
        'image/jpeg': '.jpg',
    }

    # 检查文件扩展名
    filename = file.filename or ""
    ext = '.' + filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型：{ext}，支持：{', '.join(allowed_extensions)}"
        )

    # 读取文件内容
    contents = await file.read()

    # 验证文件大小 (最大 10MB)
    max_size = 10 * 1024 * 1024
    if len(contents) > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"文件过大：{len(contents) / 1024 / 1024:.1f}MB，最大支持 10MB"
        )

    # 使用 python-magic 验证实际 MIME 类型（通过文件内容）
    actual_mime = magic.from_buffer(contents, mime=True)
    if actual_mime not in allowed_mime_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的文件内容：MIME 类型 {actual_mime} 不被支持"
        )

    # 验证文件扩展名与 MIME 类型是否匹配
    expected_ext = allowed_mime_types[actual_mime]
    if ext != expected_ext:
        logger.warning(f"文件扩展名 ({ext}) 与 MIME 类型 ({actual_mime}) 不匹配")

    # 额外验证：如果是图片，使用 PIL 验证
    if actual_mime.startswith('image/'):
        try:
            img = Image.open(io.BytesIO(contents))
            img.verify()  # 验证图片完整性
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"图片文件损坏或格式无效：{str(e)}"
            )

    # 创建订单 ID
    order_id = str(uuid.uuid4())

    try:
        # 处理 OCR
        processor = OrderProcessor()

        # 根据实际 MIME 类型选择处理方法
        if actual_mime == "application/pdf":
            result = await processor.process_pdf(contents)
        else:
            result = await processor.process_image(contents)

        # 检查是否需要人工审核
        requires_manual_review = result.confidence < auto_approve_threshold

        # 创建订单对象
        order = Order(
            id=order_id,
            order_number=result.structured_data.get("order_number", f"OCR-{order_id[:8]}"),
            customer_name=result.structured_data.get("customer_name"),
            customer_email=result.structured_data.get("customer_email"),
            customer_phone=result.structured_data.get("customer_phone"),
            customer_address=result.structured_data.get("customer_address"),
            total_amount=result.structured_data.get("total_amount"),
            currency=result.structured_data.get("currency", "CNY"),
            status=OrderStatus.PROCESSING if requires_manual_review else OrderStatus.APPROVED,
            ocr_confidence=result.confidence,
            ocr_raw_text=result.raw_text,
            ocr_structured_data=result.structured_data,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # 添加行项目
        for item_data in result.structured_data.get("line_items", []):
            item = OrderItem(
                id=str(uuid.uuid4()),
                order_id=order_id,
                line_number=item_data.get("line_number", 1),
                mpn=item_data.get("mpn"),
                manufacturer=item_data.get("manufacturer"),
                description=item_data.get("description"),
                quantity=item_data.get("quantity", 0),
                unit_price=item_data.get("unit_price", 0.0),
                total_price=item_data.get("total_price", 0.0),
                ocr_confidence=result.confidence,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            order.items.append(item)

        # 保存到数据库
        await order_repository.create(order)

        # 如果需要人工审核，触发工作流
        if requires_manual_review and background_tasks:
            background_tasks.add_task(
                notify_reviewers,
                order_id,
                result.confidence
            )

        return OCRProcessResponse(
            order_id=order_id,
            status=order.status.value,
            ocr_confidence=result.confidence,
            message="OCR 处理成功" + ("，需要人工审核" if requires_manual_review else "，已自动通过"),
            requires_manual_review=requires_manual_review
        )

    except Exception as e:
        logger.error(f"OCR 处理失败：{str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OCR 处理失败：{str(e)}"
        )


async def notify_reviewers(order_id: str, confidence: float):
    """通知审核人员"""
    # TODO: 实现消息推送（邮件、企业微信、钉钉等）
    logger.info(f"订单 {order_id} 需要人工审核，置信度：{confidence}")


# ==================== 批量操作端点 ====================

@router.post("/orders/batch/approve")
async def batch_approve_orders(order_ids: List[str]):
    """批量审核通过订单"""
    approved_count = 0
    for order_id in order_ids:
        order = await order_repository.get(order_id)
        if order:
            order.status = OrderStatus.APPROVED
            order.updated_at = datetime.utcnow()
            await order_repository.update(order)
            approved_count += 1

    return {
        "success": True,
        "approved_count": approved_count,
        "order_ids": order_ids
    }


@router.post("/orders/batch/reject")
async def batch_reject_orders(order_ids: List[str], reason: str = ""):
    """批量拒绝订单"""
    rejected_count = 0
    for order_id in order_ids:
        order = await order_repository.get(order_id)
        if order:
            order.status = OrderStatus.REJECTED
            order.review_notes = reason
            order.updated_at = datetime.utcnow()
            await order_repository.update(order)
            rejected_count += 1

    return {
        "success": True,
        "rejected_count": rejected_count,
        "order_ids": order_ids,
        "reason": reason
    }


# ==================== 统计端点 ====================

@router.get("/orders/stats/summary")
async def get_order_stats():
    """获取订单统计信息"""
    # 获取各状态订单数量
    status_counts = {}
    for status in OrderStatus:
        count = await order_repository.count(status=status)
        status_counts[status.value] = count

    total = status_counts.get("pending", 0) + status_counts.get("processing", 0) + \
            status_counts.get("approved", 0) + status_counts.get("completed", 0)

    # 今日统计
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_count = await order_repository.count(start_date=today_start)

    # 本周统计
    from datetime import timedelta
    week_start = today_start - timedelta(days=today_start.weekday())
    week_count = await order_repository.count(start_date=week_start)

    # 本月统计
    month_start = today_start.replace(day=1)
    month_count = await order_repository.count(start_date=month_start)

    return {
        "total_orders": total,
        "pending_orders": status_counts.get("pending", 0),
        "processing_orders": status_counts.get("processing", 0),
        "approved_orders": status_counts.get("approved", 0),
        "rejected_orders": status_counts.get("rejected", 0),
        "completed_orders": status_counts.get("completed", 0),
        "today_orders": today_count,
        "week_orders": week_count,
        "month_orders": month_count,
        "avg_processing_time_seconds": 0,  # TODO: 需要额外记录处理时间
        "ocr_average_confidence": 0  # TODO: 需要计算平均置信度
    }


@router.get("/orders/stats/trend")
async def get_order_trend(days: int = 30):
    """获取订单趋势数据"""
    from datetime import timedelta

    if days < 1 or days > 365:
        days = 30

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days - 1)

    # 获取每天的订单数量
    trend_data = []
    current_date = start_date
    while current_date <= end_date:
        next_date = current_date + timedelta(days=1)
        count = await order_repository.count(
            start_date=current_date,
            end_date=next_date
        )
        trend_data.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "count": count
        })
        current_date = next_date

    return {
        "days": days,
        "data": trend_data
    }


# ==================== 导出端点 ====================

@router.get("/orders/export")
async def export_orders(
    format: str = "excel",
    status_filter: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """导出订单数据"""
    # TODO: 实现导出功能
    return {
        "download_url": "/exports/orders.xlsx",
        "expires_at": datetime.utcnow().isoformat()
    }
