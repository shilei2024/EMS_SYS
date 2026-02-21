import request from '../utils/request'

// 知识图谱相关类型
export interface Component {
  mpn: string
  manufacturer: string
  description?: string
  category?: string
  package?: string
  lifecycle_status?: string
  datalink?: string
  image_url?: string
  parameters?: Parameter[]
  created_at?: string
  updated_at?: string
}

export interface Parameter {
  name: string
  value: string
  unit?: string
  min_value?: string
  max_value?: string
  category?: string
}

export interface ComponentRelation {
  source_mpn: string
  target_mpn: string
  relation_type: 'CAN_SUBSTITUTE' | 'CAN_REPLACE' | 'SIMILAR_TO'
  confidence: number
  description?: string
  source?: 'manual' | 'ai_inference'
}

export interface ComponentStats {
  total_components: number
  total_parameters: number
  total_relations: number
  categories: { category: string; count: number }[]
  manufacturers: { manufacturer: string; count: number }[]
}

/**
 * 搜索组件
 */
export function searchComponents(params?: {
  keyword?: string
  category?: string
  manufacturer?: string
  package?: string
  limit?: number
}) {
  return request({
    url: '/api/v1/kg/components/search',
    method: 'get',
    params
  })
}

/**
 * 获取组件详情
 */
export function getComponent(mpn: string, manufacturer?: string) {
  return request({
    url: `/api/v1/kg/components/${encodeURIComponent(mpn)}`,
    method: 'get',
    params: { manufacturer }
  })
}

/**
 * 创建组件
 */
export function createComponent(data: Component) {
  return request({
    url: '/api/v1/kg/components',
    method: 'post',
    data
  })
}

/**
 * 更新组件
 */
export function updateComponent(mpn: string, manufacturer: string, data: Partial<Component>) {
  return request({
    url: `/api/v1/kg/components/${encodeURIComponent(mpn)}`,
    method: 'put',
    params: { manufacturer },
    data
  })
}

/**
 * 删除组件
 */
export function deleteComponent(mpn: string, manufacturer: string) {
  return request({
    url: `/api/v1/kg/components/${encodeURIComponent(mpn)}`,
    method: 'delete',
    params: { manufacturer }
  })
}

/**
 * 获取组件参数
 */
export function getComponentParameters(mpn: string, manufacturer: string) {
  return request({
    url: `/api/v1/kg/components/${encodeURIComponent(mpn)}/parameters`,
    method: 'get',
    params: { manufacturer }
  })
}

/**
 * 添加组件参数
 */
export function addComponentParameter(mpn: string, manufacturer: string, parameter: Parameter) {
  return request({
    url: `/api/v1/kg/components/${encodeURIComponent(mpn)}/parameters`,
    method: 'post',
    params: { manufacturer },
    data: parameter
  })
}

/**
 * 查找替代料
 */
export function findSubstitutes(mpn: string, manufacturer: string) {
  return request({
    url: `/api/v1/kg/components/${encodeURIComponent(mpn)}/substitutes`,
    method: 'get',
    params: { manufacturer }
  })
}

/**
 * 创建组件关系
 */
export function createRelation(data: ComponentRelation) {
  return request({
    url: '/api/v1/kg/components/relations',
    method: 'post',
    data
  })
}

/**
 * 批量导入组件
 */
export function batchImportComponents(components: Component[], batch_size?: number) {
  return request({
    url: '/api/v1/kg/components/batch',
    method: 'post',
    data: { components, batch_size }
  })
}

/**
 * 获取统计信息
 */
export function getStats() {
  return request({
    url: '/api/v1/kg/stats',
    method: 'get'
  })
}

// 别名，用于 Dashboard 导入
export const getComponents = searchComponents
