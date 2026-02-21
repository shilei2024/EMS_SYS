import { describe, it, expect, vi, beforeEach } from 'vitest'
import {
  getOrders,
  getOrder,
  createOrder,
  updateOrder,
  deleteOrder,
  reviewOrder,
  getOrderStats,
  getOrderTrend
} from './order'
import request from './request'

// Mock request module
vi.mock('./request', () => ({
  default: vi.fn()
}))

describe('Order API', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getOrders', () => {
    it('should call GET /api/v1/orders with params', async () => {
      const mockResponse = {
        total: 100,
        page: 1,
        page_size: 20,
        orders: []
      }
      vi.mocked(request).mockResolvedValue(mockResponse)

      const result = await getOrders({ page: 1, page_size: 20, status: 'pending' })

      expect(request).toHaveBeenCalledWith({
        url: '/api/v1/orders',
        method: 'get',
        params: { page: 1, page_size: 20, status: 'pending' }
      })
      expect(result).toEqual(mockResponse)
    })
  })

  describe('getOrder', () => {
    it('should call GET /api/v1/orders/:id', async () => {
      const mockOrder = {
        id: 'ORD-001',
        order_number: 'PO-20260221-001',
        customer_name: 'Test Customer',
        status: 'pending'
      }
      vi.mocked(request).mockResolvedValue(mockOrder)

      const result = await getOrder('ORD-001')

      expect(request).toHaveBeenCalledWith({
        url: '/api/v1/orders/ORD-001',
        method: 'get'
      })
      expect(result).toEqual(mockOrder)
    })
  })

  describe('createOrder', () => {
    it('should call POST /api/v1/orders with data', async () => {
      const mockOrder = {
        id: 'ORD-001',
        order_number: 'PO-20260221-001',
        customer_name: 'Test Customer'
      }
      vi.mocked(request).mockResolvedValue(mockOrder)

      const result = await createOrder({
        order_number: 'PO-20260221-001',
        customer_name: 'Test Customer',
        currency: 'CNY',
        status: 'pending'
      })

      expect(request).toHaveBeenCalledWith({
        url: '/api/v1/orders',
        method: 'post',
        data: {
          order_number: 'PO-20260221-001',
          customer_name: 'Test Customer',
          currency: 'CNY',
          status: 'pending'
        }
      })
      expect(result).toEqual(mockOrder)
    })
  })

  describe('updateOrder', () => {
    it('should call PUT /api/v1/orders/:id with data', async () => {
      const mockOrder = {
        id: 'ORD-001',
        status: 'approved'
      }
      vi.mocked(request).mockResolvedValue(mockOrder)

      const result = await updateOrder('ORD-001', { status: 'approved' })

      expect(request).toHaveBeenCalledWith({
        url: '/api/v1/orders/ORD-001',
        method: 'put',
        data: { status: 'approved' }
      })
      expect(result).toEqual(mockOrder)
    })
  })

  describe('deleteOrder', () => {
    it('should call DELETE /api/v1/orders/:id', async () => {
      vi.mocked(request).mockResolvedValue(undefined)

      await deleteOrder('ORD-001')

      expect(request).toHaveBeenCalledWith({
        url: '/api/v1/orders/ORD-001',
        method: 'delete'
      })
    })
  })

  describe('reviewOrder', () => {
    it('should call POST /api/v1/orders/:id/review with action', async () => {
      const mockResponse = {
        id: 'ORD-001',
        status: 'approved'
      }
      vi.mocked(request).mockResolvedValue(mockResponse)

      const result = await reviewOrder('ORD-001', 'approve', '审批通过')

      expect(request).toHaveBeenCalledWith({
        url: '/api/v1/orders/ORD-001/review',
        method: 'post',
        data: { action: 'approve', review_notes: '审批通过' }
      })
      expect(result).toEqual(mockResponse)
    })
  })

  describe('getOrderStats', () => {
    it('should call GET /api/v1/orders/stats/summary', async () => {
      const mockStats = {
        total_orders: 1000,
        pending_orders: 50,
        approved_orders: 800
      }
      vi.mocked(request).mockResolvedValue(mockStats)

      const result = await getOrderStats()

      expect(request).toHaveBeenCalledWith({
        url: '/api/v1/orders/stats/summary',
        method: 'get'
      })
      expect(result).toEqual(mockStats)
    })
  })

  describe('getOrderTrend', () => {
    it('should call GET /api/v1/orders/stats/trend with days param', async () => {
      const mockTrend = {
        days: 30,
        data: [
          { date: '2026-01-01', count: 10 },
          { date: '2026-01-02', count: 15 }
        ]
      }
      vi.mocked(request).mockResolvedValue(mockTrend)

      const result = await getOrderTrend(30)

      expect(request).toHaveBeenCalledWith({
        url: '/api/v1/orders/stats/trend',
        method: 'get',
        params: { days: 30 }
      })
      expect(result).toEqual(mockTrend)
    })

    it('should default to 30 days', async () => {
      vi.mocked(request).mockResolvedValue({ days: 30, data: [] })

      await getOrderTrend()

      expect(request).toHaveBeenCalledWith({
        url: '/api/v1/orders/stats/trend',
        method: 'get',
        params: { days: 30 }
      })
    })
  })
})
