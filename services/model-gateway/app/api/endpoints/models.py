"""
模型管理端点
"""
from typing import Dict, Any, List

from fastapi import APIRouter, HTTPException, status

from app.core.gateway import get_gateway
from app.config import settings

router = APIRouter()


@router.get("/")
async def list_models(enabled_only: bool = True):
    """
    获取模型列表

    Args:
        enabled_only: 是否只返回启用的模型

    Returns:
        模型列表
    """
    gateway = get_gateway()
    all_models = gateway.get_available_models()

    if enabled_only:
        models = [m for m in all_models if m.get("is_enabled", True)]
    else:
        models = all_models

    return {
        "count": len(models),
        "models": models
    }


@router.get("/{model_name}")
async def get_model_details(model_name: str):
    """
    获取模型详情

    Args:
        model_name: 模型名称

    Returns:
        模型详情
    """
    gateway = get_gateway()
    all_models = gateway.get_available_models()

    for model in all_models:
        if model["name"] == model_name:
            return model

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"模型 '{model_name}' 不存在"
    )


@router.post("/{model_name}/enable")
async def enable_model(model_name: str):
    """
    启用模型

    Args:
        model_name: 模型名称

    Returns:
        操作结果
    """
    # TODO: 实现模型启用逻辑，更新数据库配置
    return {
        "model_name": model_name,
        "action": "enable",
        "success": True,
        "message": f"模型 '{model_name}' 已启用"
    }


@router.post("/{model_name}/disable")
async def disable_model(model_name: str):
    """
    禁用模型

    Args:
        model_name: 模型名称

    Returns:
        操作结果
    """
    # TODO: 实现模型禁用逻辑，更新数据库配置
    return {
        "model_name": model_name,
        "action": "disable",
        "success": True,
        "message": f"模型 '{model_name}' 已禁用"
    }


@router.get("/providers")
async def list_providers():
    """
    获取提供商列表及其健康状态

    Returns:
        提供商列表
    """
    gateway = get_gateway()
    health_status = gateway.get_health_status()

    providers = []
    for name, status_info in health_status.items():
        providers.append({
            "name": name,
            "is_healthy": status_info["is_healthy"],
            "last_check": status_info["last_check"],
            "response_time_ms": status_info["response_time_ms"],
            "error_message": status_info["error_message"],
            "provider_type": status_info["config"]["provider_type"],
            "priority": status_info["config"]["priority"],
            "is_enabled": status_info["config"]["is_enabled"]
        })

    return {
        "count": len(providers),
        "providers": providers
    }


@router.post("/providers/{provider_name}/health-check")
async def trigger_health_check(provider_name: str):
    """
    手动触发健康检查

    Args:
        provider_name: 提供商名称

    Returns:
        健康检查结果
    """
    gateway = get_gateway()
    providers = list(gateway.providers.values())

    for provider in providers:
        if provider.config.name == provider_name:
            is_healthy = await provider.health_check()

            return {
                "provider_name": provider_name,
                "is_healthy": is_healthy,
                "error_message": provider.health.error_message,
                "response_time_ms": provider.health.response_time_ms,
                "last_check": provider.health.last_check.isoformat() if provider.health.last_check else None
            }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"提供商 '{provider_name}' 不存在"
    )


@router.get("/config/defaults")
async def get_default_configs():
    """
    获取默认配置

    Returns:
        默认配置
    """
    return {
        "default_models": settings.default_models,
        "local_models": settings.local_models,
        "health_check_interval": settings.health_check_interval,
        "fallback_retry_count": settings.fallback_retry_count
    }