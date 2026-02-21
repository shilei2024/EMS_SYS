import request from '../utils/request'

// 财务相关类型
export interface Expense {
  id: string
  user_id: string
  type: 'travel' | 'office' | 'communication' | 'training' | 'entertainment' | 'other'
  amount: number
  currency: string
  description: string
  status: 'pending' | 'approved' | 'rejected' | 'paid'
  receipt_url?: string
  approved_by?: string
  approved_at?: string
  payment_at?: string
  notes?: string
  created_at: string
  updated_at: string
}

export interface Salary {
  id: string
  user_id: string
  type: 'base' | 'performance' | 'bonus' | 'commission' | 'allowance'
  amount: number
  currency: string
  month: string
  reason?: string
  status: 'pending' | 'approved' | 'paid'
  paid_by?: string
  paid_at?: string
  notes?: string
  created_at: string
  updated_at: string
}

export interface Reconciliation {
  id: string
  order_id: string
  customer_id: string
  customer_name: string
  amount: number
  currency: string
  period: string
  status: 'pending' | 'confirmed' | 'disputed'
  confirmed_by?: string
  confirmed_at?: string
  dispute_reason?: string
  notes?: string
  attachment_url?: string
  created_at: string
  updated_at: string
}

/**
 * 获取报销列表
 */
export function getExpenses(params?: {
  page?: number
  page_size?: number
  status?: string
  user_id?: string
  type?: string
}) {
  return request({
    url: '/api/v1/finance/expenses',
    method: 'get',
    params
  })
}

/**
 * 获取报销详情
 */
export function getExpense(id: string) {
  return request({
    url: `/api/v1/finance/expenses/${id}`,
    method: 'get'
  })
}

/**
 * 创建报销
 */
export function createExpense(data: {
  type: string
  amount: number
  currency?: string
  description: string
  receipt_url?: string
}) {
  return request({
    url: '/api/v1/finance/expenses',
    method: 'post',
    data
  })
}

/**
 * 更新报销
 */
export function updateExpense(id: string, data: Partial<Expense>) {
  return request({
    url: `/api/v1/finance/expenses/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除报销
 */
export function deleteExpense(id: string) {
  return request({
    url: `/api/v1/finance/expenses/${id}`,
    method: 'delete'
  })
}

/**
 * 审批报销
 */
export function approveExpense(id: string, notes?: string) {
  return request({
    url: `/api/v1/finance/expenses/${id}/approve`,
    method: 'post',
    data: { notes }
  })
}

/**
 * 拒绝报销
 */
export function rejectExpense(id: string, notes?: string) {
  return request({
    url: `/api/v1/finance/expenses/${id}/reject`,
    method: 'post',
    data: { notes }
  })
}

/**
 * 获取工资列表
 */
export function getSalaries(params?: {
  page?: number
  page_size?: number
  user_id?: string
  type?: string
  month?: string
}) {
  return request({
    url: '/api/v1/finance/salaries',
    method: 'get',
    params
  })
}

/**
 * 获取工资详情
 */
export function getSalary(id: string) {
  return request({
    url: `/api/v1/finance/salaries/${id}`,
    method: 'get'
  })
}

/**
 * 创建工资记录
 */
export function createSalary(data: {
  user_id: string
  type: string
  amount: number
  currency?: string
  month: string
  reason?: string
}) {
  return request({
    url: '/api/v1/finance/salaries',
    method: 'post',
    data
  })
}

/**
 * 更新工资记录
 */
export function updateSalary(id: string, data: Partial<Salary>) {
  return request({
    url: `/api/v1/finance/salaries/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除工资记录
 */
export function deleteSalary(id: string) {
  return request({
    url: `/api/v1/finance/salaries/${id}`,
    method: 'delete'
  })
}

/**
 * 获取对账列表
 */
export function getReconciliations(params?: {
  page?: number
  page_size?: number
  customer_id?: string
  status?: string
  period?: string
}) {
  return request({
    url: '/api/v1/finance/reconciliations',
    method: 'get',
    params
  })
}

/**
 * 获取对账详情
 */
export function getReconciliation(id: string) {
  return request({
    url: `/api/v1/finance/reconciliations/${id}`,
    method: 'get'
  })
}

/**
 * 创建对账记录
 */
export function createReconciliation(data: {
  order_id: string
  customer_id: string
  customer_name: string
  amount: number
  currency?: string
  period: string
  attachment_url?: string
}) {
  return request({
    url: '/api/v1/finance/reconciliations',
    method: 'post',
    data
  })
}

/**
 * 确认对账
 */
export function confirmReconciliation(id: string, notes?: string) {
  return request({
    url: `/api/v1/finance/reconciliations/${id}/confirm`,
    method: 'post',
    data: { notes }
  })
}
