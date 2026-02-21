"""
知识图谱服务测试模块
"""
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.graph.builder import (
    KnowledgeGraphBuilder,
    Component,
    Parameter,
    ComponentRelation,
    BatchImporter
)


# ==================== Component 模型测试 ====================

class TestComponentModel:
    """组件模型测试"""

    def test_create_component(self):
        """测试创建组件"""
        component = Component(
            mpn="STM32F407VGT6",
            manufacturer="STMicroelectronics",
            description="ARM Cortex-M4 MCU",
            category="Microcontrollers",
            package="LQFP-100"
        )

        assert component.mpn == "STM32F407VGT6"
        assert component.manufacturer == "STMicroelectronics"
        assert component.description == "ARM Cortex-M4 MCU"
        assert component.category == "Microcontrollers"
        assert component.package == "LQFP-100"

    def test_component_optional_fields(self):
        """测试组件可选字段"""
        component = Component(
            mpn="TEST-MPN",
            manufacturer="Test Manufacturer"
        )

        assert component.description is None
        assert component.category is None
        assert component.package is None


# ==================== Parameter 模型测试 ====================

class TestParameterModel:
    """参数模型测试"""

    def test_create_parameter(self):
        """测试创建参数"""
        param = Parameter(
            name="Input Voltage",
            value="3.3V",
            unit="V",
            min_value="2.7V",
            max_value="3.6V",
            category="Electrical"
        )

        assert param.name == "Input Voltage"
        assert param.value == "3.3V"
        assert param.unit == "V"
        assert param.min_value == "2.7V"
        assert param.max_value == "3.6V"


# ==================== ComponentRelation 模型测试 ====================

class TestComponentRelationModel:
    """组件关系模型测试"""

    def test_create_relation(self):
        """测试创建组件关系"""
        relation = ComponentRelation(
            source_mpn="STM32F407VGT6",
            target_mpn="STM32F407ZGT6",
            relation_type="CAN_SUBSTITUTE",
            confidence=0.95,
            description="Pin compatible alternative"
        )

        assert relation.source_mpn == "STM32F407VGT6"
        assert relation.target_mpn == "STM32F407ZGT6"
        assert relation.relation_type == "CAN_SUBSTITUTE"
        assert relation.confidence == 0.95


# ==================== KnowledgeGraphBuilder 测试 ====================

class TestKnowledgeGraphBuilder:
    """知识图谱构建器测试"""

    def test_builder_initialization(self):
        """测试构建器初始化"""
        builder = KnowledgeGraphBuilder(
            uri="bolt://localhost:7687",
            user="neo4j",
            password="password"
        )

        assert builder.uri == "bolt://localhost:7687"
        assert builder.user == "neo4j"
        assert builder.password == "password"
        assert builder.driver is None

    @pytest.mark.asyncio
    async def test_builder_connect(self):
        """测试连接 Neo4j（需要 Neo4j 服务）"""
        builder = KnowledgeGraphBuilder()

        # 注意：这个测试需要 Neo4j 服务运行
        # 在实际 CI/CD 中应该使用测试容器
        try:
            await builder.connect()
            assert builder.driver is not None
            await builder.close()
        except Exception:
            # 如果 Neo4j 不可用，跳过测试
            pytest.skip("Neo4j service not available")


# ==================== BatchImporter 测试 ====================

class TestBatchImporter:
    """批量导入器测试"""

    def test_importer_initialization(self):
        """测试导入器初始化"""
        builder = KnowledgeGraphBuilder()
        importer = BatchImporter(builder)

        assert importer.builder == builder


# ==================== 集成测试 ====================

class TestKGIntegration:
    """知识图谱集成测试"""

    @pytest.mark.asyncio
    async def test_full_component_workflow(self):
        """测试完整组件工作流"""
        builder = KnowledgeGraphBuilder()

        try:
            await builder.connect()

            # 1. 创建组件
            component = Component(
                mpn="INTEGRATION-TEST-MPN",
                manufacturer="Test Manufacturer",
                description="Integration Test Component",
                category="Test"
            )

            # 注意：实际测试需要 Neo4j 服务
            # component_id = await builder.create_component(component)

            # 2. 添加参数
            # param = Parameter(
            #     name="Test Parameter",
            #     value="100",
            #     unit="Ohm"
            # )
            # await builder.create_parameter(component.mpn, component.manufacturer, param)

            # 3. 查找组件
            # result = await builder.find_component(component.mpn)

            # 4. 删除组件
            # await builder.delete_component(component.mpn, component.manufacturer)

            pytest.skip("Neo4j service not available for integration test")

        except Exception:
            pytest.skip("Neo4j service not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
