"""
知识图谱 API 路由
"""
from fastapi import APIRouter, Depends, Query, Path, Body
from typing import List, Optional, Dict, Any

from app.graph.builder import (
    Component,
    Parameter,
    ComponentRelation,
    KnowledgeGraphBuilder,
    BatchImporter,
    create_graph_builder
)

router = APIRouter()


# ==================== 组件管理 ====================

@router.post("/components", summary="创建组件")
async def create_component(
    component: Component = Body(...),
    builder: KnowledgeGraphBuilder = Depends(get_graph_builder)
):
    """创建新的电子元器件组件"""
    component_id = await builder.create_component(component)
    return {
        "success": True,
        "component_id": component_id,
        "mpn": component.mpn,
        "manufacturer": component.manufacturer
    }


@router.get("/components/search", summary="搜索组件", response_model=List[Dict[str, Any]])
async def search_components(
    keyword: Optional[str] = Query(None, description="关键词"),
    category: Optional[str] = Query(None, description="分类"),
    manufacturer: Optional[str] = Query(None, description="制造商"),
    package: Optional[str] = Query(None, description="封装"),
    limit: int = Query(20, ge=1, le=100, description="返回数量限制"),
    builder: KnowledgeGraphBuilder = Depends(get_graph_builder)
):
    """搜索电子元器件组件"""
    results = await builder.search_components(
        keyword=keyword,
        category=category,
        manufacturer=manufacturer,
        package=package,
        limit=limit
    )
    return {
        "total": len(results),
        "components": results
    }


@router.get("/components/{mpn}", summary="获取组件详情")
async def get_component(
    mpn: str = Path(..., description="制造商零件号"),
    manufacturer: Optional[str] = Query(None, description="制造商"),
    builder: KnowledgeGraphBuilder = Depends(get_graph_builder)
):
    """获取电子元器件组件详情"""
    component = await builder.find_component(mpn, manufacturer)
    if not component:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="组件不存在")

    return {
        "success": True,
        "component": component
    }


@router.delete("/components/{mpn}", summary="删除组件")
async def delete_component(
    mpn: str = Path(..., description="制造商零件号"),
    manufacturer: str = Query(..., description="制造商"),
    builder: KnowledgeGraphBuilder = Depends(get_graph_builder)
):
    """删除电子元器件组件"""
    await builder.delete_component(mpn, manufacturer)
    return {
        "success": True,
        "message": f"组件 {mpn} 已删除"
    }


# ==================== 参数管理 ====================

@router.post("/components/{mpn}/parameters", summary="添加组件参数")
async def add_component_parameter(
    mpn: str = Path(..., description="制造商零件号"),
    manufacturer: str = Query(..., description="制造商"),
    parameter: Parameter = Body(...),
    builder: KnowledgeGraphBuilder = Depends(get_graph_builder)
):
    """为组件添加参数"""
    parameter_id = await builder.create_parameter(mpn, manufacturer, parameter)
    return {
        "success": True,
        "parameter_id": parameter_id,
        "parameter": parameter.dict()
    }


@router.get("/components/{mpn}/parameters", summary="获取组件参数")
async def get_component_parameters(
    mpn: str = Path(..., description="制造商零件号"),
    manufacturer: str = Query(..., description="制造商"),
    builder: KnowledgeGraphBuilder = Depends(get_graph_builder)
):
    """获取组件的所有参数"""
    parameters = await builder.get_component_parameters(mpn, manufacturer)
    return {
        "success": True,
        "total": len(parameters),
        "parameters": parameters
    }


# ==================== 替代料推荐 ====================

@router.get("/components/{mpn}/substitutes", summary="查找替代料")
async def find_substitutes(
    mpn: str = Path(..., description="制造商零件号"),
    manufacturer: str = Query(..., description="制造商"),
    builder: KnowledgeGraphBuilder = Depends(get_graph_builder)
):
    """查找可替代的元器件"""
    substitutes = await builder.find_substitutes(mpn, manufacturer)
    return {
        "success": True,
        "total": len(substitutes),
        "substitutes": substitutes
    }


# ==================== 关系管理 ====================

@router.post("/components/relations", summary="创建组件关系")
async def create_component_relation(
    relation: ComponentRelation = Body(...),
    builder: KnowledgeGraphBuilder = Depends(get_graph_builder)
):
    """创建元器件关系（替代、替换、相似）"""
    success = await builder.create_relation(relation)
    return {
        "success": success,
        "relation": relation.dict()
    }


# ==================== 批量操作 ====================

@router.post("/components/batch", summary="批量导入组件")
async def batch_import_components(
    components: List[Component] = Body(...),
    batch_size: int = Query(100, ge=10, le=500, description="批处理大小"),
    builder: KnowledgeGraphBuilder = Depends(get_graph_builder)
):
    """批量导入电子元器件组件"""
    importer = BatchImporter(builder)
    result = await importer.import_components(components, batch_size)
    return {
        "success": True,
        "result": result
    }


# ==================== 统计信息 ====================

@router.get("/stats", summary="获取图谱统计")
async def get_statistics(
    builder: KnowledgeGraphBuilder = Depends(get_graph_builder)
):
    """获取知识图谱统计信息"""
    stats = await builder.get_statistics()
    return {
        "success": True,
        "statistics": stats
    }


# ==================== 依赖注入 ====================

# 全局图谱构建器引用，由 main.py 在启动时设置
_graph_builder_ref = {"builder": None}


def set_graph_builder(builder):
    """设置图谱构建器实例（由 main.py 调用）"""
    _graph_builder_ref["builder"] = builder


def get_graph_builder() -> KnowledgeGraphBuilder:
    """获取图谱构建器实例（依赖注入）"""
    builder = _graph_builder_ref.get("builder")
    if builder is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="Graph builder not initialized")
    return builder
