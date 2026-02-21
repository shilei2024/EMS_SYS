"""
订单 OCR 处理核心模块
集成 PaddleOCR 进行文本提取，使用 LLM 进行结构化解析
"""
import asyncio
import json
import logging
import os
import tempfile
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import aiohttp
from pydantic import BaseModel, Field

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OCRSourceType(str, Enum):
    """OCR 源类型"""
    IMAGE = "image"  # 图片文件
    PDF = "pdf"      # PDF 文件
    EMAIL = "email"  # 邮件附件
    API = "api"      # API 传输


class OCRConfidenceLevel(str, Enum):
    """OCR 置信度等级"""
    HIGH = "high"      # > 0.9
    MEDIUM = "medium"  # 0.7-0.9
    LOW = "low"       # < 0.7


@dataclass
class OCRResult:
    """OCR 处理结果"""
    raw_text: str
    structured_data: Dict[str, Any]
    confidence: float
    confidence_level: OCRConfidenceLevel
    processing_time_ms: float
    lines: List[Dict[str, Any]] = field(default_factory=list)
    blocks: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class OrderLineItem:
    """订单行项目"""
    line_number: int
    mpn: Optional[str] = None  # 制造商零件号
    manufacturer: Optional[str] = None
    description: Optional[str] = None
    quantity: int = 0
    unit_price: float = 0.0
    total_price: float = 0.0
    ocr_confidence: float = 0.0
    matched_component_id: Optional[str] = None
    validation_status: str = "pending"  # pending, verified, corrected, needs_review


class StructuredOrder(BaseModel):
    """结构化订单数据"""
    order_number: Optional[str] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_address: Optional[str] = None
    order_date: Optional[str] = None
    delivery_date: Optional[str] = None
    total_amount: Optional[float] = None
    currency: str = "CNY"
    line_items: List[OrderLineItem] = Field(default_factory=list)
    notes: Optional[str] = None


class OCRProcessor:
    """OCR 处理器主类"""

    def __init__(self, paddleocr_endpoint: str = "http://localhost:8866",
                 llm_gateway_endpoint: str = "http://model-gateway:8000"):
        """
        初始化 OCR 处理器

        Args:
            paddleocr_endpoint: PaddleOCR 服务端点
            llm_gateway_endpoint: LLM 网关端点
        """
        self.paddleocr_endpoint = paddleocr_endpoint
        self.llm_gateway_endpoint = llm_gateway_endpoint
        self.session: Optional[aiohttp.ClientSession] = None
        # 是否允许使用模拟数据（仅开发环境）
        self.allow_mock_data = os.getenv("ALLOW_MOCK_OCR_DATA", "false").lower() == "true"

    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        if self.session:
            await self.session.close()

    async def process_image(self, image_data: bytes, source_type: OCRSourceType = OCRSourceType.IMAGE) -> OCRResult:
        """
        处理图片文件

        Args:
            image_data: 图片二进制数据
            source_type: 源类型

        Returns:
            OCR 处理结果
        """
        start_time = asyncio.get_event_loop().time()

        try:
            # 1. 使用 PaddleOCR 提取文本
            raw_text = await self._extract_text_with_paddleocr(image_data, source_type)

            # 2. 使用 LLM 进行结构化解析
            structured_data = await self._structure_with_llm(raw_text)

            # 3. 计算置信度
            confidence = await self._calculate_confidence(raw_text, structured_data)

            # 4. 提取订单行项目
            line_items = await self._extract_line_items(structured_data)

            processing_time_ms = (asyncio.get_event_loop().time() - start_time) * 1000

            return OCRResult(
                raw_text=raw_text,
                structured_data=structured_data,
                confidence=confidence,
                confidence_level=self._get_confidence_level(confidence),
                processing_time_ms=processing_time_ms,
                lines=[],
                blocks=[]
            )

        except Exception as e:
            logger.error(f"OCR 处理失败：{str(e)}")
            raise

    async def process_pdf(self, pdf_data: bytes) -> List[OCRResult]:
        """
        处理 PDF 文件

        Args:
            pdf_data: PDF 二进制数据

        Returns:
            OCR 处理结果列表（每页一个结果）
        """
        # TODO: 实现 PDF 分页处理
        return [await self.process_image(pdf_data, OCRSourceType.PDF)]

    async def _extract_text_with_paddleocr(self, image_data: bytes, source_type: OCRSourceType) -> str:
        """
        使用 PaddleOCR 提取文本

        Args:
            image_data: 图片二进制数据
            source_type: 源类型

        Returns:
            提取的文本

        Raises:
            RuntimeError: PaddleOCR 服务不可用且不允许模拟数据
        """
        if not self.session:
            raise RuntimeError("Session not initialized")

        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            tmp_file.write(image_data)
            tmp_path = tmp_file.name

        try:
            try:
                form_data = aiohttp.FormData()
                form_data.add_field('image', image_data, filename='order_image.png')
                form_data.add_field('source_type', source_type.value)

                async with self.session.post(
                    f"{self.paddleocr_endpoint}/predict",
                    data=form_data,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        text = result.get('text', '')
                        if not text or len(text.strip()) == 0:
                            logger.error("PaddleOCR 返回空结果")
                            if self.allow_mock_data:
                                logger.warning("使用模拟数据（仅开发环境）")
                                return self._generate_mock_ocr_text()
                            raise RuntimeError("PaddleOCR 返回空结果")
                        return text
                    else:
                        logger.error(f"PaddleOCR 服务返回错误：{response.status}")
                        if self.allow_mock_data:
                            logger.warning("使用模拟数据（仅开发环境）")
                            return self._generate_mock_ocr_text()
                        raise RuntimeError(f"PaddleOCR 服务返回错误：{response.status}")

            except aiohttp.ClientError as e:
                logger.error(f"PaddleOCR 服务调用失败：{str(e)}")
                if self.allow_mock_data:
                    logger.warning("使用模拟数据（仅开发环境）")
                    return self._generate_mock_ocr_text()
                raise RuntimeError(f"PaddleOCR 服务调用失败：{str(e)}")

        finally:
            Path(tmp_path).unlink(missing_ok=True)

    async def _structure_with_llm(self, raw_text: str) -> Dict[str, Any]:
        """
        使用 LLM 进行结构化解析

        Args:
            raw_text: OCR 提取的原始文本

        Returns:
            结构化数据
        """
        if not self.session:
            raise RuntimeError("Session not initialized")

        prompt = f"""
        请从以下订单文本中提取结构化信息。这是一个电子元器件采购订单。

        订单文本：
        {raw_text}

        请提取以下信息：
        1. 订单号 (order_number)
        2. 客户信息 (customer_name, customer_email, customer_phone, customer_address)
        3. 订单日期 (order_date)
        4. 交货日期 (delivery_date)
        5. 订单行项目 (line_items)，每行包含：
           - 行号 (line_number)
           - 制造商零件号 (mpn)
           - 制造商 (manufacturer)
           - 描述 (description)
           - 数量 (quantity)
           - 单价 (unit_price)
           - 总价 (total_price)

        请以 JSON 格式返回。
        """

        try:
            headers = {"Content-Type": "application/json"}
            payload = {
                "messages": [
                    {"role": "system", "content": "你是一个电子元器件订单处理专家。"},
                    {"role": "user", "content": prompt}
                ],
                "model": "gpt-4",
                "temperature": 0.1,
                "max_tokens": 2000
            }

            async with self.session.post(
                f"{self.llm_gateway_endpoint}/api/v1/chat/completion",
                json=payload,
                headers=headers,
                timeout=60
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    content = result.get('content', '{}')

                    try:
                        json_start = content.find('{')
                        json_end = content.rfind('}') + 1
                        if json_start >= 0 and json_end > json_start:
                            json_str = content[json_start:json_end]
                            structured_data = json.loads(json_str)
                        else:
                            structured_data = json.loads(content)
                        return structured_data

                    except json.JSONDecodeError as e:
                        logger.error(f"JSON 解析失败：{str(e)}")
                        return self._create_default_structure(raw_text)
                else:
                    logger.error(f"LLM 调用失败：{response.status}")
                    return self._create_default_structure(raw_text)

        except Exception as e:
            logger.error(f"LLM 结构化处理失败：{str(e)}")
            return self._create_default_structure(raw_text)

    async def _calculate_confidence(self, raw_text: str, structured_data: Dict[str, Any]) -> float:
        """计算 OCR 置信度"""
        confidence = 0.5

        if len(raw_text.strip()) > 50:
            confidence += 0.1

        if structured_data.get('order_number'):
            confidence += 0.15

        if structured_data.get('customer_name') or structured_data.get('customer_email'):
            confidence += 0.1

        line_items = structured_data.get('line_items', [])
        if line_items and len(line_items) > 0:
            confidence += 0.15

        if line_items:
            complete_items = 0
            for item in line_items:
                if item.get('mpn') or item.get('description'):
                    complete_items += 1
            if complete_items > 0:
                confidence += 0.1 * (complete_items / len(line_items))

        return min(confidence, 1.0)

    async def _extract_line_items(self, structured_data: Dict[str, Any]) -> List[OrderLineItem]:
        """从结构化数据中提取订单行项目"""
        line_items = []
        raw_items = structured_data.get('line_items', [])

        for idx, item_data in enumerate(raw_items):
            try:
                line_item = OrderLineItem(
                    line_number=item_data.get('line_number', idx + 1),
                    mpn=item_data.get('mpn'),
                    manufacturer=item_data.get('manufacturer'),
                    description=item_data.get('description'),
                    quantity=item_data.get('quantity', 0),
                    unit_price=item_data.get('unit_price', 0.0),
                    total_price=item_data.get('total_price', 0.0),
                    ocr_confidence=structured_data.get('confidence', 0.7)
                )

                if line_item.quantity > 0 and (line_item.mpn or line_item.description):
                    line_items.append(line_item)

            except Exception as e:
                logger.error(f"解析行项目失败：{str(e)}")
                continue

        return line_items

    def _get_confidence_level(self, confidence: float) -> OCRConfidenceLevel:
        """根据置信度分数获取等级"""
        if confidence >= 0.9:
            return OCRConfidenceLevel.HIGH
        elif confidence >= 0.7:
            return OCRConfidenceLevel.MEDIUM
        else:
            return OCRConfidenceLevel.LOW

    def _generate_mock_ocr_text(self) -> str:
        """生成模拟 OCR 文本（用于开发和测试）"""
        return """
        采购订单
        订单号：PO-2026-0215-001
        客户：华为技术有限公司
        客户邮箱：procurement@huawei.com
        客户电话：+86-755-28780808

        订单日期：2026-02-15
        交货日期：2026-03-01

        行号 | 制造商零件号 | 制造商 | 描述 | 数量 | 单价 (USD) | 总价 (USD)
        1    | STM32F407VGT6 | STMicroelectronics | ARM Cortex-M4 MCU | 1000 | 5.20 | 5200.00
        2    | ATMEGA328P-PU | Microchip | 8-bit AVR Microcontroller | 2000 | 2.80 | 5600.00

        订单总额：USD 16,800.00
        """

    def _create_default_structure(self, raw_text: str) -> Dict[str, Any]:
        """创建默认的结构化数据"""
        return {
            "order_number": None,
            "customer_name": None,
            "customer_email": None,
            "customer_phone": None,
            "order_date": None,
            "delivery_date": None,
            "total_amount": None,
            "currency": "CNY",
            "line_items": [],
            "error": "结构化解析失败"
        }

    async def validate_order_structure(self, structured_data: Dict[str, Any]) -> Dict[str, Any]:
        """验证订单结构完整性"""
        validation_errors = []
        warnings = []

        required_fields = ['order_number', 'customer_name', 'line_items']
        for field in required_fields:
            if not structured_data.get(field):
                validation_errors.append(f"缺少必要字段：{field}")

        order_number = structured_data.get('order_number')
        if order_number and len(str(order_number).strip()) < 3:
            warnings.append("订单号可能格式不正确")

        line_items = structured_data.get('line_items', [])
        if not line_items:
            validation_errors.append("订单没有行项目")

        is_valid = len(validation_errors) == 0
        return {
            "is_valid": is_valid,
            "validation_errors": validation_errors,
            "warnings": warnings,
            "line_item_count": len(line_items),
            "required_fields_present": all(field in structured_data for field in required_fields)
        }


async def create_ocr_processor() -> OCRProcessor:
    """创建 OCR 处理器实例"""
    processor = OCRProcessor()
    await processor.__aenter__()
    return processor
