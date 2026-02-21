import { describe, it, expect, vi, beforeEach } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { ref } from 'vue'

// 测试用户 store
describe('User Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('should initialize with default state', async () => {
    const { useUserStore } = await import('../stores/user')
    const userStore = useUserStore()

    expect(userStore.token).toBe('')
    expect(userStore.userId).toBe('')
    expect(userStore.username).toBe('')
    expect(userStore.isLoggedIn).toBe(false)
  })

  it('should set token and user info after login', async () => {
    const { useUserStore } = await import('../stores/user')
    const userStore = useUserStore()

    const mockToken = 'test-jwt-token'
    const mockUser = {
      id: 'user-123',
      username: 'testuser',
      email: 'test@example.com',
      role: 'admin'
    }

    userStore.setToken(mockToken)
    userStore.setUserInfo(mockUser)

    expect(userStore.token).toBe(mockToken)
    expect(userStore.userId).toBe('user-123')
    expect(userStore.username).toBe('testuser')
    expect(userStore.isLoggedIn).toBe(true)
  })

  it('should clear state after logout', async () => {
    const { useUserStore } = await import('../stores/user')
    const userStore = useUserStore()

    userStore.setToken('test-token')
    userStore.setUserInfo({
      id: 'user-123',
      username: 'testuser',
      email: 'test@example.com',
      role: 'admin'
    })

    userStore.logout()

    expect(userStore.token).toBe('')
    expect(userStore.userId).toBe('')
    expect(userStore.isLoggedIn).toBe(false)
  })
})

// 测试 API 模块
describe('Order API', () => {
  it('should have correct API functions', async () => {
    const orderApi = await import('../api/order')

    expect(orderApi.getOrderList).toBeDefined()
    expect(orderApi.getOrder).toBeDefined()
    expect(orderApi.createOrder).toBeDefined()
    expect(orderApi.updateOrder).toBeDefined()
    expect(orderApi.deleteOrder).toBeDefined()
    expect(orderApi.reviewOrder).toBeDefined()
    expect(orderApi.getOrderStats).toBeDefined()
  })
})

// 测试工具函数
describe('Request Utils', () => {
  it('should export default axios instance', async () => {
    const request = await import('../utils/request')
    expect(request.default).toBeDefined()
    expect(request.default.interceptors).toBeDefined()
  })
})
