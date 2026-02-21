"""
知识图谱构建模块
"""
import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

from neo4j import GraphDatabase, AsyncGraphDatabase
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ==================== 数据模型 ====================

class Component(BaseModel):
    """电子元器件组件"""
    mpn: str = Field(..., description="制造商零件号")
    manufacturer: str = Field(..., description="制造商")
    description: Optional[str] = None
    category: Optional[str] = None
    package: Optional[str] = None
    lifecycle_status: Optional[str] = None
    datalink: Optional[str] = None
    image_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Parameter(BaseModel):
    """元器件参数"""
    name: str = Field(..., description="参数名称")
    value: str = Field(..., description="参数值")
    unit: Optional[str] = None
    min_value: Optional[str] = None
    max_value: Optional[str] = None
    category: Optional[str] = None


class ComponentRelation(BaseModel):
    """元器件关系"""
    source_mpn: str
    target_mpn: str
    relation_type: str = Field(..., description="关系类型: CAN_SUBSTITUTE, CAN_REPLACE, SIMILAR_TO")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    description: Optional[str] = None
    source: str = Field(default="manual", description="来源: manual, ai_inference")


@dataclass
class SearchResult:
    """搜索结果"""
    component: Component
    score: float
    matched_fields: List[str] = field(default_factory=list)


# ==================== 知识图谱构建器 ====================

class KnowledgeGraphBuilder:
    """知识图谱构建器"""

    def __init__(self, uri: str = "bolt://localhost:7687", user: str = "neo4j", password: str = "password"):
        """
        初始化知识图谱构建器

        Args:
            uri: Neo4j连接URI
            user: 用户名
            password: 密码
        """
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = None

    async def connect(self):
        """连接数据库"""
        try:
            self.driver = AsyncGraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
            await self.driver.verify_connectivity()
            logger.info("成功连接到Neo4j")
        except Exception as e:
            logger.error(f"连接Neo4j失败: {str(e)}")
            raise

    async def close(self):
        """关闭连接"""
        if self.driver:
            await self.driver.close()
            logger.info("已关闭Neo4j连接")

    async def create_component(self, component: Component) -> str:
        """
        创建组件节点

        Args:
            component: 组件数据

        Returns:
            组件ID
        """
        query = """
        MERGE (c:Component {mpn: $mpn, manufacturer: $manufacturer})
        SET c.description = $description,
            c.category = $category,
            c.package = $package,
            c.lifecycle_status = $lifecycle_status,
            c.datalink = $datalink,
            c.image_url = $image_url,
            c.updated_at = datetime()
        RETURN id(c) as component_id
        """

        async with self.driver.session() as session:
            result = await session.run(query, {
                "mpn": component.mpn,
                "manufacturer": component.manufacturer,
                "description": component.description,
                "category": component.category,
                "package": component.package,
                "lifecycle_status": component.lifecycle_status,
                "datalink": component.datalink,
                "image_url": component.image_url
            })

            record = await result.single()
            return str(record["component_id"]) if record else None

    async def create_parameter(self, mpn: str, manufacturer: str, parameter: Parameter) -> str:
        """
        创建参数节点并建立关系

        Args:
            mpn: 制造商零件号
            manufacturer: 制造商
            parameter: 参数数据

        Returns:
            参数ID
        """
        query = """
        MATCH (c:Component {mpn: $mpn, manufacturer: $manufacturer})
        MERGE (p:Parameter {name: $name, value: $value})
        SET p.unit = $unit,
            p.min_value = $min_value,
            p.max_value = $max_value,
            p.category = $category
        MERGE (c)-[:HAS_PARAMETER]->(p)
        RETURN id(p) as parameter_id
        """

        async with self.driver.session() as session:
            result = await session.run(query, {
                "mpn": mpn,
                "manufacturer": manufacturer,
                "name": parameter.name,
                "value": parameter.value,
                "unit": parameter.unit,
                "min_value": parameter.min_value,
                "max_value": parameter.max_value,
                "category": parameter.category
            })

            record = await result.single()
            return str(record["parameter_id"]) if record else None

    async def create_relation(self, relation: ComponentRelation) -> bool:
        """
        创建元器件关系

        Args:
            relation: 元器件关系数据

        Returns:
            是否成功
        """
        query = """
        MATCH (c1:Component {mpn: $source_mpn})
        MATCH (c2:Component {mpn: $target_mpn})
        MERGE (c1)-[r:CAN_SUBSTITUTE {confidence: $confidence, description: $description, source: $source}]->(c2)
        RETURN id(r) as relation_id
        """

        # 根据关系类型构建不同的查询
        relation_queries = {
            "CAN_SUBSTITUTE": """
                MATCH (c1:Component {mpn: $source_mpn})
                MATCH (c2:Component {mpn: $target_mpn})
                MERGE (c1)-[r:CAN_SUBSTITUTE {confidence: $confidence, description: $description, source: $source}]->(c2)
                RETURN id(r) as relation_id
            """,
            "CAN_REPLACE": """
                MATCH (c1:Component {mpn: $source_mpn})
                MATCH (c2:Component {mpn: $target_mpn})
                MERGE (c1)-[r:CAN_REPLACE {confidence: $confidence, description: $description, source: $source}]->(c2)
                RETURN id(r) as relation_id
            """,
            "SIMILAR_TO": """
                MATCH (c1:Component {mpn: $source_mpn})
                MATCH (c2:Component {mpn: $target_mpn})
                MERGE (c1)-[r:SIMILAR_TO {confidence: $confidence, description: $description, source: $source}]->(c2)
                RETURN id(r) as relation_id
            """
        }

        query = relation_queries.get(relation.relation_type, relation_queries["CAN_SUBSTITUTE"])

        async with self.driver.session() as session:
            result = await session.run(query, {
                "source_mpn": relation.source_mpn,
                "target_mpn": relation.target_mpn,
                "confidence": relation.confidence,
                "description": relation.description,
                "source": relation.source
            })

            record = await result.single()
            return record is not None

    async def find_component(self, mpn: str, manufacturer: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        查找组件

        Args:
            mpn: 制造商零件号
            manufacturer: 制造商（可选）

        Returns:
            组件数据
        """
        if manufacturer:
            query = """
            MATCH (c:Component {mpn: $mpn, manufacturer: $manufacturer})
            OPTIONAL MATCH (c)-[:HAS_PARAMETER]->(p:Parameter)
            RETURN c, collect(p) as parameters
            """
            params = {"mpn": mpn, "manufacturer": manufacturer}
        else:
            query = """
            MATCH (c:Component {mpn: $mpn})
            OPTIONAL MATCH (c)-[:HAS_PARAMETER]->(p:Parameter)
            RETURN c, collect(p) as parameters
            """
            params = {"mpn": mpn}

        async with self.driver.session() as session:
            result = await session.run(query, params)
            record = await result.single()

            if record:
                component_data = dict(record["c"])
                parameters = [dict(p) for p in record["parameters"] if p]
                component_data["parameters"] = parameters
                return component_data

            return None

    async def find_substitutes(self, mpn: str, manufacturer: str) -> List[Dict[str, Any]]:
        """
        查找替代料

        Args:
            mpn: 制造商零件号
            manufacturer: 制造商

        Returns:
            替代料列表
        """
        query = """
        MATCH (c1:Component {mpn: $mpn, manufacturer: $manufacturer})-[r:CAN_SUBSTITUTE]->(c2:Component)
        RETURN c2, r.confidence as confidence, r.description as description
        ORDER BY confidence DESC
        """

        async with self.driver.session() as session:
            result = await session.run(query, {"mpn": mpn, "manufacturer": manufacturer})

            substitutes = []
            async for record in result:
                component = dict(record["c"])
                component["confidence"] = record["confidence"]
                component["description"] = record["description"]
                substitutes.append(component)

            return substitutes

    async def search_components(
        self,
        keyword: Optional[str] = None,
        category: Optional[str] = None,
        manufacturer: Optional[str] = None,
        package: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        搜索组件

        Args:
            keyword: 关键词
            category: 分类
            manufacturer: 制造商
            package: 封装
            limit: 返回数量限制

        Returns:
            组件列表
        """
        # 构建查询条件
        conditions = []
        params = {"limit": limit}

        if keyword:
            conditions.append("(c.description CONTAINS $keyword OR c.mpn CONTAINS $keyword OR c.category CONTAINS $keyword)")
            params["keyword"] = keyword

        if category:
            conditions.append("c.category = $category")
            params["category"] = category

        if manufacturer:
            conditions.append("c.manufacturer = $manufacturer")
            params["manufacturer"] = manufacturer

        if package:
            conditions.append("c.package = $package")
            params["package"] = package

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        query = f"""
        MATCH (c:Component)
        WHERE {where_clause}
        RETURN c
        LIMIT $limit
        """

        async with self.driver.session() as session:
            result = await session.run(query, params)

            components = []
            async for record in result:
                components.append(dict(record["c"]))

            return components

    async def get_component_parameters(self, mpn: str, manufacturer: str) -> List[Dict[str, Any]]:
        """
        获取组件参数

        Args:
            mpn: 制造商零件号
            manufacturer: 制造商

        Returns:
            参数列表
        """
        query = """
        MATCH (c:Component {mpn: $mpn, manufacturer: $manufacturer})-[:HAS_PARAMETER]->(p:Parameter)
        RETURN p
        """

        async with self.driver.session() as session:
            result = await session.run(query, {"mpn": mpn, "manufacturer": manufacturer})

            parameters = []
            async for record in result:
                parameters.append(dict(record["p"]))

            return parameters

    async def delete_component(self, mpn: str, manufacturer: str) -> bool:
        """
        删除组件

        Args:
            mpn: 制造商零件号
            manufacturer: 制造商

        Returns:
            是否成功
        """
        query = """
        MATCH (c:Component {mpn: $mpn, manufacturer: $manufacturer})
        DETACH DELETE c
        """

        async with self.driver.session() as session:
            await session.run(query, {"mpn": mpn, "manufacturer": manufacturer})
            return True

    async def get_statistics(self) -> Dict[str, Any]:
        """获取图谱统计信息"""
        queries = {
            "total_components": "MATCH (c:Component) RETURN count(c) as count",
            "total_parameters": "MATCH (p:Parameter) RETURN count(p) as count",
            "total_relations": "MATCH ()-[r:CAN_SUBSTITUTE|CAN_REPLACE|SIMILAR_TO]->() RETURN count(r) as count",
            "categories": "MATCH (c:Component) RETURN c.category as category, count(c) as count ORDER BY count DESC",
            "manufacturers": "MATCH (c:Component) RETURN c.manufacturer as manufacturer, count(c) as count ORDER BY count DESC LIMIT 10"
        }

        stats = {}

        async with self.driver.session() as session:
            for key, query in queries.items():
                result = await session.run(query)

                if key in ["categories", "manufacturers"]:
                    items = []
                    async for record in result:
                        items.append(dict(record))
                    stats[key] = items
                else:
                    record = await result.single()
                    stats[key] = record["count"] if record else 0

        return stats


# ==================== 批量操作 ====================

class BatchImporter:
    """批量导入器"""

    def __init__(self, builder: KnowledgeGraphBuilder):
        self.builder = builder

    async def import_components(self, components: List[Component], batch_size: int = 100) -> Dict[str, int]:
        """
        批量导入组件

        Args:
            components: 组件列表
            batch_size: 批处理大小

        Returns:
            导入统计
        """
        success_count = 0
        error_count = 0

        for i in range(0, len(components), batch_size):
            batch = components[i:i + batch_size]

            tasks = []
            for component in batch:
                task = self._import_component_safe(component)
                tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                if isinstance(result, Exception):
                    error_count += 1
                    logger.error(f"导入组件失败: {str(result)}")
                else:
                    success_count += 1

        return {
            "total": len(components),
            "success": success_count,
            "error": error_count
        }

    async def _import_component_safe(self, component: Component) -> str:
        """安全导入组件"""
        try:
            return await self.builder.create_component(component)
        except Exception as e:
            raise e

    async def import_from_csv(self, file_path: str, batch_size: int = 100) -> Dict[str, int]:
        """
        从CSV文件导入

        Args:
            file_path: CSV文件路径
            batch_size: 批处理大小

        Returns:
            导入统计
        """
        # TODO: 实现CSV导入
        import csv

        components = []

        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                component = Component(
                    mpn=row['mpn'],
                    manufacturer=row['manufacturer'],
                    description=row.get('description'),
                    category=row.get('category'),
                    package=row.get('package'),
                    lifecycle_status=row.get('lifecycle_status'),
                    datalink=row.get('datalink')
                )
                components.append(component)

        return await self.import_components(components, batch_size)


# 工厂函数
async def create_graph_builder(
    uri: str = "bolt://localhost:7687",
    user: str = "neo4j",
    password: str = "password"
) -> KnowledgeGraphBuilder:
    """创建知识图谱构建器"""
    builder = KnowledgeGraphBuilder(uri, user, password)
    await builder.connect()
    return builder
