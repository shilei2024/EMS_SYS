"""
模型网关配置
"""
import os
from typing import List, Dict, Any

from pydantic import BaseSettings


class Settings(BaseSettings):
    """应用设置"""

    # 应用配置
    app_name: str = "电子元器件代理商增值系统 - 模型网关"
    app_version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

    # 服务器配置
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))

    # 数据库配置
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@localhost:5432/component_agent"
    )

    # Redis配置
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # 安全配置
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

    # CORS配置
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
    ]

    # 模型网关配置
    health_check_interval: int = int(os.getenv("HEALTH_CHECK_INTERVAL", "60"))
    fallback_retry_count: int = int(os.getenv("FALLBACK_RETRY_COUNT", "3"))

    # 默认模型配置
    default_models: List[Dict[str, Any]] = [
        {
            "name": "gpt-4",
            "display_name": "GPT-4",
            "provider_type": "openai",
            "api_base": "https://api.openai.com/v1",
            "api_key": os.getenv("OPENAI_API_KEY", ""),
            "context_length": 8192,
            "max_tokens": 4096,
            "temperature": 0.7,
            "capabilities": ["chat", "completion"],
            "priority": 1,
            "is_enabled": True,
            "cost_per_token": 0.03 / 1000  # 假设每千token $0.03
        },
        {
            "name": "gpt-3.5-turbo",
            "display_name": "GPT-3.5 Turbo",
            "provider_type": "openai",
            "api_base": "https://api.openai.com/v1",
            "api_key": os.getenv("OPENAI_API_KEY", ""),
            "context_length": 4096,
            "max_tokens": 2048,
            "temperature": 0.7,
            "capabilities": ["chat", "completion"],
            "priority": 2,
            "is_enabled": True,
            "cost_per_token": 0.002 / 1000  # 假设每千token $0.002
        },
        {
            "name": "claude-3-haiku-20240307",
            "display_name": "Claude 3 Haiku",
            "provider_type": "anthropic",
            "api_base": "https://api.anthropic.com",
            "api_key": os.getenv("ANTHROPIC_API_KEY", ""),
            "context_length": 200000,
            "max_tokens": 4096,
            "temperature": 0.7,
            "capabilities": ["chat", "completion"],
            "priority": 3,
            "is_enabled": True,
            "cost_per_token": 0.001 / 1000  # 假设每千token $0.001
        }
    ]

    # 本地模型配置（如果需要）
    local_models: List[Dict[str, Any]] = [
        {
            "name": "llama-2-7b",
            "display_name": "Llama 2 7B",
            "provider_type": "local",
            "api_base": "http://localhost:8001",
            "api_key": "",
            "context_length": 4096,
            "max_tokens": 2048,
            "temperature": 0.7,
            "capabilities": ["chat", "completion"],
            "priority": 99,  # 最低优先级，作为兜底
            "is_enabled": False,  # 默认禁用，需要手动启用
            "cost_per_token": 0.0
        }
    ]

    class Config:
        env_file = ".env"
        case_sensitive = False


# 全局设置实例
settings = Settings()