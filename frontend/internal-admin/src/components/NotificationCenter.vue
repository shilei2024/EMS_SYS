<template>
  <div class="notification-center">
    <el-badge :value="unreadCount" :hidden="unreadCount === 0" class="notification-badge">
      <el-button text :icon="Bell" @click="toggleDropdown">
        <span class="bell-icon" :class="{ 'bell-animate': hasNewMessage }"></span>
      </el-button>
    </el-badge>

    <el-dropdown
      ref="dropdownRef"
      trigger="click"
      popper-class="notification-dropdown"
      :hide-on-click="false"
    >
      <template #dropdown>
        <div class="notification-panel">
          <div class="panel-header">
            <span class="title">通知中心</span>
            <div class="actions">
              <el-button text size="small" @click="markAllAsRead">全部已读</el-button>
              <el-button text size="small" @click="clearAll">清空</el-button>
            </div>
          </div>

          <div class="panel-body">
            <el-empty v-if="notifications.length === 0" description="暂无通知" :image-size="80" />
            <div v-else class="notification-list">
              <div
                v-for="item in notifications"
                :key="item.id"
                class="notification-item"
                :class="{ unread: !item.read }"
                @click="handleNotificationClick(item)"
              >
                <div class="item-icon" :class="getTypeClass(item.type)">
                  <el-icon :size="20">
                    <component :is="getTypeIcon(item.type)" />
                  </el-icon>
                </div>
                <div class="item-content">
                  <div class="item-title">{{ item.title }}</div>
                  <div class="item-message">{{ item.message }}</div>
                  <div class="item-time">{{ formatTime(item.timestamp) }}</div>
                </div>
              </div>
            </div>
          </div>

          <div class="panel-footer" v-if="notifications.length > 0">
            <el-button text size="small" @click="loadMore">查看更多</el-button>
          </div>
        </div>
      </template>
    </el-dropdown>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Bell, Document, Warning } from '@element-plus/icons-vue'
import { ElDropdown } from 'element-plus'
import { wsService, MessageType, WSMessage, getWebSocketUrl } from '../utils/websocket'

interface Notification {
  id: string
  type: MessageType
  title: string
  message: string
  timestamp: string
  read: boolean
  data?: any
}

const dropdownRef = ref<InstanceType<typeof ElDropdown>>()
const notifications = ref<Notification[]>([])
const unreadCount = computed(() => notifications.value.filter(n => !n.read).length)
const hasNewMessage = ref(false)

// 获取消息类型对应的图标
function getTypeIcon(type: MessageType) {
  const map: Record<MessageType, any> = {
    [MessageType.ORDER_STATUS_CHANGED]: Document,
    [MessageType.INVENTORY_ALERT]: Warning,
    [MessageType.SYSTEM_NOTIFICATION]: Warning
  }
  return map[type] || Warning
}

// 获取消息类型对应的样式
function getTypeClass(type: MessageType): string {
  const map: Record<MessageType, string> = {
    [MessageType.ORDER_STATUS_CHANGED]: 'order-icon',
    [MessageType.INVENTORY_ALERT]: 'alert-icon',
    [MessageType.SYSTEM_NOTIFICATION]: 'info-icon'
  }
  return map[type] || 'info-icon'
}

// 切换下拉菜单
function toggleDropdown() {
  dropdownRef.value?.handleCommand()
}

// 处理通知点击
function handleNotificationClick(item: Notification) {
  item.read = true

  // 根据通知类型执行不同操作
  if (item.type === MessageType.ORDER_STATUS_CHANGED && item.data?.order_id) {
    // 跳转到订单详情
    console.log('跳转到订单详情:', item.data.order_id)
  } else if (item.type === MessageType.INVENTORY_ALERT && item.data?.mpn) {
    // 跳转到库存管理
    console.log('跳转到库存管理:', item.data.mpn)
  }
}

// 标记全部已读
function markAllAsRead() {
  notifications.value.forEach(n => n.read = true)
}

// 清空全部
function clearAll() {
  notifications.value = []
}

// 加载更多
function loadMore() {
  // TODO: 实现分页加载历史通知
  console.log('加载更多通知')
}

// 格式化时间
function formatTime(timestamp: string): string {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`

  return date.toLocaleDateString('zh-CN')
}

// 处理 WebSocket 消息
function handleWSMessage(message: WSMessage) {
  hasNewMessage.value = true

  const titleMap: Record<MessageType, string> = {
    [MessageType.ORDER_STATUS_CHANGED]: '订单状态变更',
    [MessageType.INVENTORY_ALERT]: '库存预警',
    [MessageType.SYSTEM_NOTIFICATION]: '系统通知'
  }

  const notification: Notification = {
    id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
    type: message.type,
    title: titleMap[message.type] || '通知',
    message: message.message || message.data?.message || '收到新消息',
    timestamp: message.timestamp,
    read: false,
    data: message.data
  }

  notifications.value.unshift(notification)

  // 限制通知数量
  if (notifications.value.length > 50) {
    notifications.value.pop()
  }
}

// WebSocket 状态变化处理
function handleWSStatusChange(status: string) {
  console.log('WebSocket 状态变化:', status)
}

onMounted(() => {
  // 连接 WebSocket
  const wsUrl = getWebSocketUrl()
  wsService.setUrl(wsUrl)
  wsService.connect()

  // 订阅消息
  const unsubscribe = wsService.subscribe(handleWSMessage)

  // 监听状态变化
  window.addEventListener('ws-status-change', handleWSStatusChange)

  onUnmounted(() => {
    unsubscribe()
    window.removeEventListener('ws-status-change', handleWSStatusChange)
  })
})
</script>

<style scoped>
.notification-center {
  display: inline-block;
}

.notification-badge {
  margin-right: 16px;
}

.bell-icon {
  font-size: 20px;
  transition: transform 0.3s;
}

.bell-animate {
  animation: bell-shake 0.5s ease-in-out;
}

@keyframes bell-shake {
  0%, 100% { transform: rotate(0deg); }
  25% { transform: rotate(-15deg); }
  50% { transform: rotate(15deg); }
  75% { transform: rotate(-15deg); }
}

.notification-panel {
  width: 400px;
  max-height: 500px;
  display: flex;
  flex-direction: column;
}

.panel-header {
  padding: 16px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-header .title {
  font-size: 16px;
  font-weight: 600;
}

.panel-body {
  flex: 1;
  overflow-y: auto;
  max-height: 400px;
}

.notification-list {
  padding: 8px 0;
}

.notification-item {
  display: flex;
  padding: 12px 16px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.notification-item:hover {
  background-color: #f5f7fa;
}

.notification-item.unread {
  background-color: #ecf5ff;
}

.item-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  flex-shrink: 0;
}

.order-icon {
  background-color: #e6f7ff;
  color: #1890ff;
}

.alert-icon {
  background-color: #fff7e6;
  color: #fa8c16;
}

.info-icon {
  background-color: #f6ffed;
  color: #52c41a;
}

.item-content {
  flex: 1;
  overflow: hidden;
}

.item-title {
  font-size: 14px;
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
}

.item-message {
  font-size: 13px;
  color: #666;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-time {
  font-size: 12px;
  color: #999;
}

.panel-footer {
  padding: 12px 16px;
  border-top: 1px solid #eee;
  text-align: center;
}
</style>
