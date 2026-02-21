"""
订单服务主入口
"""
import logging
import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.endpoints import router
from app.database.connection import get_db_pool, close_db_pool


# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    应用生命周期管理
    """
    # 启动时执行
    logger.info("订单服务启动中...")
    logger.info(f"环境：{settings.environment}")
    logger.info(f"数据库：{settings.database_url[:30]}...")

    # 初始化数据库连接池
    await get_db_pool()
    logger.info("数据库连接池初始化完成")

    # 创建 OCR 临时目录
    import os
    os.makedirs(settings.ocr_temp_dir, exist_ok=True)

    yield

    # 关闭时执行
    logger.info("订单服务关闭中...")
    await close_db_pool()
    logger.info("数据库连接池已关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="订单处理服务 - 支持 OCR 识别、自动审核、工作流管理",
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router, prefix="/api/v1")


# 健康检查
@app.get("/health", tags=["Health"])
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "order-service",
        "version": settings.app_version
    }


# 根路径
@app.get("/", tags=["Root"])
async def root():
    """根路径"""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs"
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        workers=settings.workers,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
