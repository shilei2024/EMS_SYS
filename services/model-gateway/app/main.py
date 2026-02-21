"""
模型网关 FastAPI 应用入口
"""
import asyncio
from contextlib import asynccontextmanager
from typing import Dict, Any

import uvicorn
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.core.gateway import (
    ChatMessage, ChatRequest, ChatResponse,
    get_gateway, initialize_gateway
)
from app.api import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化模型网关
    print("🚀 初始化模型网关...")

    # 验证关键配置
    if settings.debug:
        print("⚠️  运行在调试模式，安全检查放宽")
    else:
        # 生产环境验证API密钥
        all_models = settings.default_models + settings.local_models
        for model in all_models:
            if model.get("is_enabled", False) and model.get("api_key"):
                if len(model["api_key"]) < 20:
                    print(f"⚠️  警告: 模型 {model.get('name')} 的API密钥过短")
                # 检查是否是默认值或空值
                if model["api_key"] in ["", "sk-", "your-api-key-here"]:
                    print(f"❌ 错误: 模型 {model.get('name')} 的API密钥未正确配置")
                    raise ValueError(f"模型 {model.get('name')} 的API密钥未正确配置")

    all_models = settings.default_models + settings.local_models
    await initialize_gateway(all_models)
    print("✅ 模型网关初始化完成")

    yield

    # 关闭时清理资源
    print("🛑 关闭模型网关...")
    gateway = get_gateway()
    await gateway.stop_health_check()
    print("✅ 模型网关已关闭")


# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="电子元器件代理商增值系统 - 模型网关服务",
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含API路由
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """根端点"""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    gateway = get_gateway()
    health_status = gateway.get_health_status()

    # 检查是否有健康的提供商
    has_healthy_provider = any(
        status["is_healthy"] for status in health_status.values()
    )

    status_code = status.HTTP_200_OK if has_healthy_provider else status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "healthy" if has_healthy_provider else "unhealthy",
            "has_healthy_provider": has_healthy_provider,
            "providers": health_status,
            "timestamp": asyncio.get_event_loop().time()
        }
    )


@app.get("/models")
async def list_models():
    """获取可用模型列表"""
    gateway = get_gateway()
    models = gateway.get_available_models()
    return {"models": models}


@app.post("/chat", response_model=ChatResponse)
async def chat_completion(request: ChatRequest):
    """聊天补全接口"""
    gateway = get_gateway()

    try:
        response = await gateway.chat_with_fallback(request)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"所有模型都失败了: {str(e)}"
        )


@app.get("/metrics")
async def get_metrics():
    """获取网关指标"""
    gateway = get_gateway()
    health_status = gateway.get_health_status()

    # 计算总体指标
    total_providers = len(health_status)
    healthy_providers = sum(1 for s in health_status.values() if s["is_healthy"])

    metrics = {
        "total_providers": total_providers,
        "healthy_providers": healthy_providers,
        "health_ratio": f"{healthy_providers}/{total_providers}",
        "providers": health_status
    }

    return metrics


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if settings.debug else "warning"
    )