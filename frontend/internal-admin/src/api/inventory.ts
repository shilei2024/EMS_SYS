import request from '../utils/request'

// 库存相关类型
export interface InventoryItem {
  id: string
  mpn: string
  manufacturer: string
  description?: string
  category?: string
  warehouse_location?: string
  quantity: number
  safety_stock: number
  reorder_point: number
  unit_cost: number
  currency: string
  last_count_date?: string
  last_purchase_date?: string
  supplier_id?: string
  notes?: string
  created_at: string
  updated_at: string
}

export interface InventoryAlert {
  id: string
  inventory_id: string
  alert_type: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  message: string
  current_quantity?: number
  threshold_quantity?: number
  status: 'active' | 'acknowledged' | 'resolved'
  acknowledged_by?: string
  acknowledged_at?: string
  created_at: string
}

export interface InventoryAdjustment {
  id: string
  inventory_id: string
  adjustment_type: 'in' | 'out' | 'adjustment' | 'correction'
  quantity_change: number
  quantity_before: number
  quantity_after: number
  reason: string
  reference_type?: string
  reference_id?: string
  created_by: string
  created_at: string
}

export interface DemandForecast {
  id: string
  inventory_id: string
  forecast_date: string
  predicted_demand: number
  confidence_level?: number
  actual_demand?: number
  accuracy?: number
  model_version?: string
  created_at: string
}

/**
 * 获取库存列表
 */
export function getInventoryList(params?: {
  page?: number
  page_size?: number
  mpn?: string
  manufacturer?: string
  category?: string
  warehouse_location?: string
}) {
  return request({
    url: '/api/v1/inventory',
    method: 'get',
    params
  })
}

/**
 * 获取库存详情
 */
export function getInventory(id: string) {
  return request({
    url: `/api/v1/inventory/${id}`,
    method: 'get'
  })
}

/**
 * 创建库存
 */
export function createInventory(data: Partial<InventoryItem>) {
  return request({
    url: '/api/v1/inventory',
    method: 'post',
    data
  })
}

/**
 * 更新库存
 */
export function updateInventory(id: string, data: Partial<InventoryItem>) {
  return request({
    url: `/api/v1/inventory/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除库存
 */
export function deleteInventory(id: string) {
  return request({
    url: `/api/v1/inventory/${id}`,
    method: 'delete'
  })
}

/**
 * 库存调整
 */
export function adjustInventory(data: {
  inventory_id: string
  adjustment_type: string
  quantity_change: number
  reason: string
}) {
  return request({
    url: '/api/v1/inventory/adjust',
    method: 'post',
    data
  })
}

/**
 * 获取预警列表
 */
export function getAlerts(params?: {
  status?: string
  severity?: string
  page?: number
  page_size?: number
}) {
  return request({
    url: '/api/v1/inventory/alerts',
    method: 'get',
    params
  })
}

// 别名，用于 Dashboard 导入
export const getInventoryAlerts = getAlerts

/**
 * 确认预警
 */
export function acknowledgeAlert(id: string) {
  return request({
    url: `/api/v1/inventory/alerts/${id}/acknowledge`,
    method: 'post'
  })
}

/**
 * 获取需求预测
 */
export function getForecast(params?: {
  inventory_id?: string
  start_date?: string
  end_date?: string
}) {
  return request({
    url: '/api/v1/forecast',
    method: 'get',
    params
  })
}

/**
 * 生成预测
 */
export function generateForecast(data: {
  inventory_ids: string[]
  forecast_days: number
}) {
  return request({
    url: '/api/v1/forecast/generate',
    method: 'post',
    data
  })
}
