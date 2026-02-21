import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { wsService, MessageType, WSStatus, getWebSocketUrl } from '../utils/websocket'

describe('WebSocket Service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    wsService.disconnect()
  })

  describe('getWebSocketUrl', () => {
    it('should return correct URL for http', () => {
      // Mock window.location
      const originalLocation = window.location
      Object.defineProperty(window, 'location', {
        value: { protocol: 'http:', host: 'localhost:3000' },
        writable: true
      })

      const url = getWebSocketUrl()
      expect(url).toBe('ws://localhost:3000/api/v1/ws')

      // Restore
      Object.defineProperty(window, 'location', {
        value: originalLocation,
        writable: true
      })
    })

    it('should return correct URL for https', () => {
      const originalLocation = window.location
      Object.defineProperty(window, 'location', {
        value: { protocol: 'https:', host: 'example.com' },
        writable: true
      })

      const url = getWebSocketUrl()
      expect(url).toBe('wss://example.com/api/v1/ws')

      Object.defineProperty(window, 'location', {
        value: originalLocation,
        writable: true
      })
    })

    it('should use VITE_WS_HOST if available', () => {
      const originalEnv = import.meta.env
      import.meta.env = { VITE_WS_HOST: 'ws.custom.com' }

      const url = getWebSocketUrl()
      expect(url).toContain('ws.custom.com')

      import.meta.env = originalEnv
    })
  })

  describe('WSStatus enum', () => {
    it('should have correct status values', () => {
      expect(WSStatus.CONNECTING).toBe('connecting')
      expect(WSStatus.CONNECTED).toBe('connected')
      expect(WSStatus.DISCONNECTED).toBe('disconnected')
      expect(WSStatus.RECONNECTING).toBe('reconnecting')
    })
  })

  describe('MessageType enum', () => {
    it('should have correct message types', () => {
      expect(MessageType.ORDER_STATUS_CHANGED).toBe('order_status_changed')
      expect(MessageType.INVENTORY_ALERT).toBe('inventory_alert')
      expect(MessageType.SYSTEM_NOTIFICATION).toBe('system_notification')
    })
  })

  describe('WebSocketService instance', () => {
    it('should create singleton instance', () => {
      expect(wsService).toBeDefined()
      expect(typeof wsService.connect).toBe('function')
      expect(typeof wsService.disconnect).toBe('function')
      expect(typeof wsService.subscribe).toBe('function')
      expect(typeof wsService.send).toBe('function')
    })

    it('should have initial DISCONNECTED status', () => {
      expect(wsService.getStatus()).toBe(WSStatus.DISCONNECTED)
    })
  })
})
