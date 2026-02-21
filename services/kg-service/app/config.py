"""
知识图谱服务配置
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
    app_name: str = "Knowledge Graph Service"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"

    # ==================== 服务配置 ====================
    host: str = "0.0.0.0"
    port: int = 8005
    workers: int = 1

    # ==================== Neo4j 配置 ====================
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"
    neo4j_max_connections: int = 50
    neo4j_connection_timeout: int = 30

    # ==================== 认证配置 ====================
    auth_service_url: str = "http://auth-service:8001"
    jwt_public_key: Optional[str] = None

    # ==================== LLM 配置 ====================
    llm_gateway_endpoint: str = "http://model-gateway:8000"
    llm_model: str = "gpt-4"

    # ==================== 日志配置 ====================
    log_level: str = "INFO"
    log_format: str = "json"

    # ==================== 限流配置 ====================
    rate_limit_per_minute: int = 200
    rate_limit_burst: int = 50

    # ==================== 搜索配置 ====================
    search_default_limit: int = 20
    search_max_limit: int = 100
    substitute_max_results: int = 10


# 全局配置实例
settings = Settings()


def get_settings() -> Settings:
    """获取配置实例"""
    return settings
