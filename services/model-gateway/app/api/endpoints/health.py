"""
健康检查端点
"""
import asyncio
from datetime import datetime

from fastapi import APIRouter, HTTPException, status

from app.core.gateway import get_gateway

router = APIRouter()


@router.get("/")
async def health_check():
    """
    整体健康检查

    Returns:
        健康状态
    """
    gateway = get_gateway()
    health_status = gateway.get_health_status()

    # 检查是否有健康的提供商
    has_healthy_provider = any(
        status["is_healthy"] for status in health_status.values()
    )

    # 计算总体指标
    total_providers = len(health_status)
    healthy_providers = sum(1 for s in health_status.values() if s["is_healthy"])
    health_ratio = healthy_providers / total_providers if total_providers > 0 else 0

    status_code = status.HTTP_200_OK if has_healthy_provider else status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": "healthy" if has_healthy_provider else "unhealthy",
        "has_healthy_provider": has_healthy_provider,
        "total_providers": total_providers,
        "healthy_providers": healthy_providers,
        "health_ratio": health_ratio,
        "providers": health_status,
        "timestamp": datetime.utcnow().isoformat(),
        "event_loop_time": asyncio.get_event_loop().time()
    }


@router.get("/detailed")
async def detailed_health_check():
    """
    详细健康检查

    Returns:
        详细的健康状态信息
    """
    gateway = get_gateway()
    health_status = gateway.get_health_status()

    detailed_status = {}

    for provider_name, status_info in health_status.items():
        # 计算健康持续时间
        if status_info["last_check"]:
            try:
                last_check = datetime.fromisoformat(status_info["last_check"])
                uptime_seconds = (datetime.utcnow() - last_check).total_seconds()
            except (ValueError, TypeError):
                uptime_seconds = None
        else:
            uptime_seconds = None

        detailed_status[provider_name] = {
            "is_healthy": status_info["is_healthy"],
            "last_check": status_info["last_check"],
            "uptime_seconds": uptime_seconds,
            "response_time_ms": status_info["response_time_ms"],
            "error_message": status_info["error_message"],
            "config": status_info["config"],
            "recommendation": _get_health_recommendation(status_info)
        }

    # 总体评估
    all_healthy = all(s["is_healthy"] for s in detailed_status.values())
    any_healthy = any(s["is_healthy"] for s in detailed_status.values())

    overall_status = "healthy" if all_healthy else "degraded" if any_healthy else "unhealthy"

    return {
        "overall_status": overall_status,
        "all_providers_healthy": all_healthy,
        "any_provider_healthy": any_healthy,
        "providers": detailed_status,
        "recommendations": _get_overall_recommendations(detailed_status),
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/providers/{provider_name}")
async def provider_health_check(provider_name: str):
    """
    特定提供商健康检查

    Args:
        provider_name: 提供商名称

    Returns:
        提供商健康状态
    """
    gateway = get_gateway()
    health_status = gateway.get_health_status()

    if provider_name not in health_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"提供商 '{provider_name}' 不存在"
        )

    provider_status = health_status[provider_name]

    return {
        "provider_name": provider_name,
        "is_healthy": provider_status["is_healthy"],
        "last_check": provider_status["last_check"],
        "response_time_ms": provider_status["response_time_ms"],
        "error_message": provider_status["error_message"],
        "config": provider_status["config"],
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/force-check")
async def force_health_check():
    """
    强制立即执行健康检查

    Returns:
        健康检查结果
    """
    gateway = get_gateway()

    try:
        await gateway._check_all_providers_health()
        health_status = gateway.get_health_status()

        return {
            "action": "force_health_check",
            "success": True,
            "timestamp": datetime.utcnow().isoformat(),
            "results": health_status
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"健康检查失败: {str(e)}"
        )


def _get_health_recommendation(status_info: dict) -> str:
    """获取健康状态建议"""
    if status_info["is_healthy"]:
        if status_info["response_time_ms"] and status_info["response_time_ms"] > 1000:
            return "响应时间较慢，建议监控"
        return "运行正常"
    else:
        error_msg = status_info["error_message"] or "未知错误"
        return f"服务异常: {error_msg}，建议检查配置和网络连接"


def _get_overall_recommendations(detailed_status: dict) -> list:
    """获取总体建议"""
    recommendations = []

    unhealthy_count = sum(1 for s in detailed_status.values() if not s["is_healthy"])
    slow_count = sum(1 for s in detailed_status.values() if s["is_healthy"] and s.get("response_time_ms", 0) > 1000)

    if unhealthy_count > 0:
        unhealthy_names = [name for name, s in detailed_status.items() if not s["is_healthy"]]
        recommendations.append(f"有 {unhealthy_count} 个提供商异常: {', '.join(unhealthy_names)}")

    if slow_count > 0:
        slow_names = [name for name, s in detailed_status.items() if s["is_healthy"] and s.get("response_time_ms", 0) > 1000]
        recommendations.append(f"有 {slow_count} 个提供商响应较慢: {', '.join(slow_names)}")

    if not recommendations:
        recommendations.append("所有提供商运行正常")

    # 检查优先级配置
    healthy_providers = [name for name, s in detailed_status.items() if s["is_healthy"]]
    if len(healthy_providers) > 1:
        priorities = []
        for name in healthy_providers:
            priority = detailed_status[name]["config"].get("priority", 999)
            priorities.append((priority, name))

        priorities.sort()
        if priorities[0][0] != 1:
            recommendations.append(f"最高优先级提供商是 '{priorities[0][1]}' (优先级: {priorities[0][0]})，建议检查优先级配置")

    return recommendations