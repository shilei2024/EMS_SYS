"""
订单服务主入口
"""
import logging
import sys
import traceback
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

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


# ==================== 全局错误处理 ====================

async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """全局异常处理器"""
    # 记录详细错误信息（包括堆栈跟踪）
    logger.error(
        f"未处理的异常 - {request.method} {request.url.path}\n"
        f"异常类型：{type(exc).__name__}\n"
        f"异常信息：{str(exc)}\n"
        f"堆栈跟踪:\n{traceback.format_exc()}"
    )

    # 返回用户友好的错误消息
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "内部服务器错误",
            "message": "服务器处理请求时发生错误，请稍后重试",
            "path": request.url.path
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """请求验证异常处理器"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(x) for x in error.get("loc", [])),
            "message": error.get("msg"),
            "type": error.get("type")
        })

    logger.warning(f"请求验证失败 - {request.method} {request.url.path}: {errors}")

    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "error": "请求验证失败",
            "message": "请求参数格式不正确",
            "details": errors,
            "path": request.url.path
        }
    )


# 注册全局异常处理器
# 注意：需要在创建 app 之后，注册路由之前注册


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    应用生命周期管理
    """
    # 启动时执行
    logger.info("订单服务启动中...")
    logger.info(f"环境：{settings.environment}")
    logger.info(f"数据库：{settings.database_url[:30] if settings.database_url else '未配置'}...")

    # 验证生产环境配置
    if settings.environment == "production":
        if not settings.database_url:
            logger.error("生产环境缺少 DATABASE_URL 配置")
            raise ValueError("生产环境必须设置 DATABASE_URL")
        if not settings.redis_url:
            logger.error("生产环境缺少 REDIS_URL 配置")
            raise ValueError("生产环境必须设置 REDIS_URL")

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

# 注册全局异常处理器
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# 配置 CORS - 从配置读取，生产环境限制具体域名
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins if hasattr(settings, 'cors_origins') else [
        "http://localhost:3000",
        "http://localhost:8080",
    ],
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
