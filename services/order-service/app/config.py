"""
订单服务配置
"""
import os
from typing import Optional, List

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
    # 生产环境必须通过环境变量设置
    database_url: str | None = os.environ.get("DATABASE_URL")
    # 微服务共享数据库，使用较小的连接池防止连接耗尽
    # 默认池大小：5 个连接，最大溢出：10 个连接
    database_pool_size: int = int(os.environ.get("DATABASE_POOL_SIZE", "5"))
    database_max_overflow: int = int(os.environ.get("DATABASE_MAX_OVERFLOW", "10"))
    database_pool_timeout: int = int(os.environ.get("DATABASE_POOL_TIMEOUT", "30"))
    database_pool_recycle: int = int(os.environ.get("DATABASE_POOL_RECYCLE", "3600"))

    # ==================== Redis 配置 ====================
    redis_url: str | None = os.environ.get("REDIS_URL")
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
    minio_access_key: str = os.environ.get("MINIO_ACCESS_KEY", "minioadmin")
    minio_secret_key: str = os.environ.get("MINIO_SECRET_KEY", "minioadmin")
    minio_bucket: str = "orders"
    minio_use_ssl: bool = False

    # ==================== CORS 配置 ====================
    cors_origins: List[str] = os.environ.get(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:8080"
    ).split(",")

    # ==================== 消息队列配置 ====================
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    rabbitmq_exchange: str = "orders"

    # ==================== 日志配置 ====================
    # 生产环境使用 WARNING 级别，开发环境使用 INFO
    log_level: str = os.environ.get("LOG_LEVEL", "WARNING" if os.environ.get("ENVIRONMENT") == "production" else "INFO")
    log_format: str = os.environ.get("LOG_FORMAT", "json")  # json, text
    log_file: Optional[str] = os.environ.get("LOG_FILE", None)

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

        # 生产环境验证关键配置
        if self.environment == "production":
            errors = []
            if not self.database_url:
                errors.append("DATABASE_URL environment variable is required")
            if not self.redis_url:
                errors.append("REDIS_URL environment variable is required")
            if errors:
                raise ValueError("; ".join(errors))


# 全局配置实例
settings = Settings()


def get_settings() -> Settings:
    """获取配置实例"""
    return settings
