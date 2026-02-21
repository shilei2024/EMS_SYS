import request from '../utils/request'

export interface Order {
  id: string
  order_number: string
  customer_name: string
  customer_email?: string
  customer_phone?: string
  customer_address?: string
  total_amount?: number
  currency: string
  status: string
  priority: string
  ocr_confidence?: number
  items?: OrderItem[]
  created_at: string
  updated_at: string
}

export interface OrderItem {
  id: string
  order_id: string
  line_number: number
  mpn?: string
  manufacturer?: string
  description?: string
  quantity: number
  unit_price: number
  total_price: number
  ocr_confidence: number
  review_status: string
}

export interface OrderListResponse {
  total: number
  page: number
  page_size: number
  orders: Order[]
}

export interface OrderStats {
  total_orders: number
  pending_orders: number
  processing_orders: number
  approved_orders: number
  rejected_orders: number
  completed_orders: number
  today_orders: number
  week_orders: number
  month_orders: number
}

export function getOrders(params?: any): Promise<OrderListResponse> {
  return request({
    url: '/api/v1/orders',
    method: 'get',
    params
  })
}

export function getOrder(id: string): Promise<Order> {
  return request({
    url: `/api/v1/orders/${id}`,
    method: 'get'
  })
}

export function createOrder(data: Partial<Order>): Promise<{ id: string }> {
  return request({
    url: '/api/v1/orders',
    method: 'post',
    data
  })
}

export function updateOrder(id: string, data: Partial<Order>): Promise<Order> {
  return request({
    url: `/api/v1/orders/${id}`,
    method: 'put',
    data
  })
}

export function deleteOrder(id: string): Promise<void> {
  return request({
    url: `/api/v1/orders/${id}`,
    method: 'delete'
  })
}

export function reviewOrder(id: string, action: string, reviewNotes?: string): Promise<Order> {
  return request({
    url: `/api/v1/orders/${id}/review`,
    method: 'post',
    data: { action, review_notes: reviewNotes }
  })
}

export function uploadOrderFile(file: File, autoApproveThreshold?: number): Promise<{ order_id: string; status: string; ocr_confidence: number; requires_manual_review: boolean }> {
  const formData = new FormData()
  formData.append('file', file)
  if (autoApproveThreshold) {
    formData.append('auto_approve_threshold', autoApproveThreshold.toString())
  }

  return request({
    url: '/api/v1/orders/ocr',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export function getOrderStats(): Promise<OrderStats> {
  return request({
    url: '/api/v1/orders/stats/summary',
    method: 'get'
  })
}

export function batchApproveOrders(orderIds: string[]): Promise<{ success: boolean; approved_count: number; order_ids: string[] }> {
  return request({
    url: '/api/v1/orders/batch/approve',
    method: 'post',
    data: orderIds
  })
}

export function batchRejectOrders(orderIds: string[], reason: string): Promise<{ success: boolean; rejected_count: number; order_ids: string[]; reason: string }> {
  return request({
    url: '/api/v1/orders/batch/reject',
    method: 'post',
    data: { order_ids: orderIds, reason }
  })
}

export function exportOrders(format?: string, statusFilter?: string, startDate?: string, endDate?: string): Promise<{ download_url: string; expires_at: string }> {
  return request({
    url: '/api/v1/orders/export',
    method: 'get',
    params: { format, status_filter: statusFilter, start_date: startDate, end_date: endDate }
  })
}

export function getOrderTrend(days: number = 30): Promise<{ days: number; data: Array<{ date: string; count: number }> }> {
  return request({
    url: '/api/v1/orders/stats/trend',
    method: 'get',
    params: { days }
  })
}

// 别名用于 Dashboard
export { getOrders as getRecentOrders }
