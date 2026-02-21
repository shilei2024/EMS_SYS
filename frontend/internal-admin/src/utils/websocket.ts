import { ElMessage } from 'element-plus'

// WebSocket 消息类型
export enum MessageType {
  ORDER_STATUS_CHANGED = 'order_status_changed',
  INVENTORY_ALERT = 'inventory_alert',
  SYSTEM_NOTIFICATION = 'system_notification'
}

// WebSocket 消息接口
export interface WSMessage {
  type: MessageType
  data: any
  timestamp: string
  message?: string
}

// WebSocket 连接状态
export enum WSStatus {
  CONNECTING = 'connecting',
  CONNECTED = 'connected',
  DISCONNECTED = 'disconnected',
  RECONNECTING = 'reconnecting'
}

// 回调函数类型
export type MessageCallback = (message: WSMessage) => void

class WebSocketService {
  private ws: WebSocket | null = null
  private url: string = ''
  private status: WSStatus = WSStatus.DISCONNECTED
  private callbacks: MessageCallback[] = []
  private reconnectTimer: number | null = null
  private heartbeatTimer: number | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5

  // 设置 WebSocket URL
  setUrl(url: string) {
    this.url = url
  }

  // 连接 WebSocket
  connect() {
    if (!this.url) {
      console.error('WebSocket URL 未设置')
      return
    }

    if (this.ws && (this.ws.readyState === WebSocket.CONNECTING || this.ws.readyState === WebSocket.OPEN)) {
      return
    }

    this.setStatus(WSStatus.CONNECTING)
    this.ws = new WebSocket(this.url)

    this.ws.onopen = () => {
      console.log('WebSocket 连接成功')
      this.setStatus(WSStatus.CONNECTED)
      this.reconnectAttempts = 0
      this.startHeartbeat()
      ElMessage.success('实时通知已连接')
    }

    this.ws.onmessage = (event) => {
      try {
        const message: WSMessage = JSON.parse(event.data)
        console.log('收到 WebSocket 消息:', message)
        this.notifyCallbacks(message)
        this.showMessageNotification(message)
      } catch (error) {
        console.error('解析 WebSocket 消息失败:', error)
      }
    }

    this.ws.onclose = () => {
      console.log('WebSocket 连接关闭')
      this.setStatus(WSStatus.DISCONNECTED)
      this.stopHeartbeat()
      this.attemptReconnect()
    }

    this.ws.onerror = (error) => {
      console.error('WebSocket 错误:', error)
      ElMessage.error('实时通知连接失败')
    }
  }

  // 断开连接
  disconnect() {
    this.stopHeartbeat()
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.setStatus(WSStatus.DISCONNECTED)
  }

  // 发送消息
  send(data: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    } else {
      console.warn('WebSocket 未连接，无法发送消息')
    }
  }

  // 订阅消息
  subscribe(callback: MessageCallback) {
    this.callbacks.push(callback)
    return () => {
      this.callbacks = this.callbacks.filter(cb => cb !== callback)
    }
  }

  // 设置状态
  private setStatus(status: WSStatus) {
    this.status = status
    // 触发状态变化事件
    window.dispatchEvent(new CustomEvent('ws-status-change', { detail: status }))
  }

  // 获取状态
  getStatus(): WSStatus {
    return this.status
  }

  // 尝试重连
  private attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('WebSocket 重连次数已达上限')
      ElMessage.error('实时通知连接失败，请刷新页面重试')
      return
    }

    this.setStatus(WSStatus.RECONNECTING)
    this.reconnectAttempts++
    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000)
    console.log(`WebSocket 将在 ${delay}ms 后重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)

    this.reconnectTimer = window.setTimeout(() => {
      this.connect()
    }, delay)
  }

  // 通知所有回调
  private notifyCallbacks(message: WSMessage) {
    this.callbacks.forEach(callback => {
      try {
        callback(message)
      } catch (error) {
        console.error('WebSocket 回调执行失败:', error)
      }
    })
  }

  // 显示消息通知
  private showMessageNotification(message: WSMessage) {
    const notifications: Record<MessageType, { title: string; type: string }> = {
      [MessageType.ORDER_STATUS_CHANGED]: { title: '订单状态变更', type: 'info' },
      [MessageType.INVENTORY_ALERT]: { title: '库存预警', type: 'warning' },
      [MessageType.SYSTEM_NOTIFICATION]: { title: '系统通知', type: 'info' }
    }

    const config = notifications[message.type] || { title: '通知', type: 'info' }

    ElMessage({
      message: message.message || message.data?.message || '收到新消息',
      type: config.type as any,
      duration: 5000
    })
  }

  // 启动心跳
  private startHeartbeat() {
    this.heartbeatTimer = window.setInterval(() => {
      this.send({ type: 'ping', timestamp: new Date().toISOString() })
    }, 30000)
  }

  // 停止心跳
  private stopHeartbeat() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer)
      this.heartbeatTimer = null
    }
  }
}

// 导出单例
export const wsService = new WebSocketService()

// 辅助函数：获取 WebSocket URL
export function getWebSocketUrl(): string {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const host = import.meta.env.VITE_WS_HOST || window.location.host || 'localhost:80'
  return `${protocol}//${host}/api/v1/ws`
}
