"""
订单数据模型
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class OrderStatus(str, Enum):
    """订单状态"""
    PENDING = "pending"              # 待处理
    PROCESSING = "processing"        # 处理中
    REVIEW_NEEDED = "review_needed"  # 需要审核
    APPROVED = "approved"            # 已审核通过
    REJECTED = "rejected"            # 已拒绝
    COMPLETED = "completed"          # 已完成
    CANCELLED = "cancelled"          # 已取消


class OrderPriority(str, Enum):
    """订单优先级"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class ReviewStatus(str, Enum):
    """行项目审核状态"""
    PENDING = "pending"           # 待审核
    VERIFIED = "verified"         # 已验证
    CORRECTED = "corrected"      # 已修正
    NEEDS_REVIEW = "needs_review" # 需要审核


class OrderItem(BaseModel):
    """订单行项目"""
    id: str
    order_id: str
    line_number: int
    mpn: Optional[str] = None
    manufacturer: Optional[str] = None
    description: Optional[str] = None
    quantity: int = 0
    unit_price: float = 0.0
    total_price: float = 0.0
    ocr_confidence: float = 0.0
    review_status: ReviewStatus = ReviewStatus.PENDING
    review_notes: Optional[str] = None
    matched_component_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Order(BaseModel):
    """订单主表"""
    id: str
    order_number: str
    source_id: Optional[int] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_address: Optional[str] = None
    total_amount: Optional[float] = None
    currency: str = "CNY"
    status: OrderStatus = OrderStatus.PENDING
    priority: OrderPriority = OrderPriority.NORMAL
    ocr_confidence: Optional[float] = None
    ocr_raw_text: Optional[str] = None
    ocr_structured_data: Optional[dict] = None
    review_notes: Optional[str] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    items: List[OrderItem] = Field(default_factory=list)


class OrderFilter(BaseModel):
    """订单过滤条件"""
    status: Optional[OrderStatus] = None
    priority: Optional[OrderPriority] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    has_ocr_confidence_below: Optional[float] = None
