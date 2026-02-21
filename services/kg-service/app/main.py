"""
知识图谱服务主入口
"""
import logging
import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.graph.builder import create_graph_builder, KnowledgeGraphBuilder
from app.api.router import router, set_graph_builder


# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


# 全局图谱构建器实例
_graph_builder: KnowledgeGraphBuilder = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    应用生命周期管理
    """
    global _graph_builder

    # 启动时执行
    logger.info("知识图谱服务启动中...")
    logger.info(f"环境：{settings.environment}")
    logger.info(f"Neo4j: {settings.neo4j_uri}")

    # 初始化 Neo4j 连接
    _graph_builder = await create_graph_builder(
        uri=settings.neo4j_uri,
        user=settings.neo4j_user,
        password=settings.neo4j_password
    )
    logger.info("Neo4j 连接初始化完成")

    # 设置路由的图谱构建器引用
    set_graph_builder(_graph_builder)

    yield

    # 关闭时执行
    logger.info("知识图谱服务关闭中...")
    await _graph_builder.close()
    logger.info("Neo4j 连接已关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="知识图谱服务 - 电子元器件型号匹配、替代料推荐、相似度搜索",
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
        "service": "kg-service",
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


# 获取图谱构建器
def get_graph_builder() -> KnowledgeGraphBuilder:
    """获取图谱构建器实例"""
    return _graph_builder


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        workers=settings.workers,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
