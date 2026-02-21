"""
模型网关API路由
"""
from fastapi import APIRouter

from app.api.endpoints import chat, models, health

router = APIRouter()

# 包含各个端点模块
router.include_router(chat.router, prefix="/chat", tags=["聊天"])
router.include_router(models.router, prefix="/models", tags=["模型管理"])
router.include_router(health.router, prefix="/health", tags=["健康检查"])