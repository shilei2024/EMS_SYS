"""
数据库连接管理
"""
import asyncpg
import logging
from typing import Optional
from contextlib import asynccontextmanager

from app.config import settings

logger = logging.getLogger(__name__)

# 全局连接池
_db_pool: Optional[asyncpg.Pool] = None


async def get_db_pool() -> asyncpg.Pool:
    """
    获取数据库连接池

    Returns:
        数据库连接池
    """
    global _db_pool

    if _db_pool is None:
        try:
            _db_pool = await asyncpg.create_pool(
                dsn=settings.database_url,
                min_size=5,
                max_size=settings.database_pool_size,
                max_inactive_connection_lifetime=300.0,
                max_queries=50000,
                timeout=settings.database_pool_timeout,
            )
            logger.info("数据库连接池创建成功")
        except Exception as e:
            logger.error(f"创建数据库连接池失败：{str(e)}")
            raise

    return _db_pool


async def close_db_pool() -> None:
    """关闭数据库连接池"""
    global _db_pool

    if _db_pool:
        await _db_pool.close()
        _db_pool = None
        logger.info("数据库连接池已关闭")


async def get_connection() -> asyncpg.Connection:
    """
    获取数据库连接

    Returns:
        数据库连接
    """
    pool = await get_db_pool()
    return await pool.acquire()


async def release_connection(connection: asyncpg.Connection) -> None:
    """
    释放数据库连接

    Args:
        connection: 要释放的连接
    """
    pool = await get_db_pool()
    await pool.release(connection)


@asynccontextmanager
async def get_db_connection():
    """
    数据库连接上下文管理器

    Yields:
        数据库连接
    """
    conn = await get_connection()
    try:
        yield conn
    finally:
        await release_connection(conn)


async def init_db() -> None:
    """
    初始化数据库表结构
    """
    conn = await get_connection()
    try:
        # 创建订单表
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id UUID PRIMARY KEY,
                order_number VARCHAR(100) NOT NULL UNIQUE,
                source_id INTEGER,
                customer_name VARCHAR(200),
                customer_email VARCHAR(200),
                customer_phone VARCHAR(50),
                customer_address TEXT,
                total_amount DECIMAL(12, 2),
                currency VARCHAR(10) DEFAULT 'CNY',
                status VARCHAR(50) DEFAULT 'pending',
                priority VARCHAR(50) DEFAULT 'normal',
                ocr_confidence DECIMAL(5, 4),
                ocr_raw_text TEXT,
                ocr_structured_data JSONB,
                review_notes TEXT,
                reviewed_by UUID,
                reviewed_at TIMESTAMP,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        logger.info("订单表创建成功")

        # 创建订单行项目表
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id UUID PRIMARY KEY,
                order_id UUID REFERENCES orders(id) ON DELETE CASCADE,
                line_number INTEGER NOT NULL,
                mpn VARCHAR(200),
                manufacturer VARCHAR(200),
                description TEXT,
                quantity INTEGER DEFAULT 0,
                unit_price DECIMAL(12, 4) DEFAULT 0,
                total_price DECIMAL(12, 2) DEFAULT 0,
                ocr_confidence DECIMAL(5, 4),
                review_status VARCHAR(50) DEFAULT 'pending',
                review_notes TEXT,
                matched_component_id UUID,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(order_id, line_number)
            )
        """)
        logger.info("订单行项目表创建成功")

        # 创建索引
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_name)
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at)
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id)
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_order_items_mpns ON order_items USING gin(mpn gin_trgm_ops)
        """)
        logger.info("索引创建成功")

    except Exception as e:
        logger.error(f"初始化数据库失败：{str(e)}")
        raise
    finally:
        await release_connection(conn)
