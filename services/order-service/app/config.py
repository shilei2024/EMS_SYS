"""
订单服务配置
"""
import os
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # ==================== 应用配置 ====================
    app_name: str = "Order Service"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"  # development, staging, production

    # ==================== 服务配置 ====================
    host: str = "0.0.0.0"
    port: int = 8004
    workers: int = 1

    # ==================== 数据库配置 ====================
    database_url: str = "postgresql://postgres:postgres@localhost:5432/component_agent"
    database_pool_size: int = 10
    database_max_overflow: int = 20
    database_pool_timeout: int = 30
    database_pool_recycle: int = 3600

    # ==================== Redis 配置 ====================
    redis_url: str = "redis://localhost:6379/0"
    redis_prefix: str = "order:"

    # ==================== OCR 配置 ====================
    paddleocr_endpoint: str = "http://localhost:8866"
    ocr_temp_dir: str = "/tmp/ocr"

    # ==================== LLM 配置 ====================
    llm_gateway_endpoint: str = "http://model-gateway:8000"
    llm_model: str = "gpt-4"
    llm_temperature: float = 0.1
    llm_max_tokens: int = 2000
    llm_timeout: int = 60

    # ==================== 认证配置 ====================
    auth_service_url: str = "http://auth-service:8001"
    jwt_public_key: Optional[str] = None  # 从 auth-service 获取

    # ==================== 对象存储配置 ====================
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "orders"
    minio_use_ssl: bool = False

    # ==================== 消息队列配置 ====================
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    rabbitmq_exchange: str = "orders"

    # ==================== 日志配置 ====================
    log_level: str = "INFO"
    log_format: str = "json"  # json, text
    log_file: Optional[str] = None

    # ==================== 限流配置 ====================
    rate_limit_per_minute: int = 100
    rate_limit_burst: int = 20

    # ==================== 审核配置 ====================
    auto_approve_threshold: float = 0.9  # OCR 置信度阈值
    max_file_size_mb: int = 10  # 最大文件大小
    allowed_file_types: list = None  # 允许的文件类型

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.allowed_file_types is None:
            self.allowed_file_types = [
                "application/pdf",
                "image/png",
                "image/jpeg",
                "image/jpg"
            ]


# 全局配置实例
settings = Settings()


def get_settings() -> Settings:
    """获取配置实例"""
    return settings
