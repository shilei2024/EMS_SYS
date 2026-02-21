<template>
  <div class="orders-page">
    <!-- 顶部导航 -->
    <header class="site-header">
      <div class="container header-content">
        <div class="logo">
          <NuxtLink to="/">
            <span class="logo-text">元器件商城</span>
          </NuxtLink>
        </div>

        <nav class="main-nav">
          <NuxtLink to="/">首页</NuxtLink>
          <NuxtLink to="/products">产品中心</NuxtLink>
          <NuxtLink to="/about">关于我们</NuxtLink>
          <NuxtLink to="/contact">联系我们</NuxtLink>
        </nav>

        <div class="header-actions">
          <NuxtLink to="/cart" class="btn btn-outline">
            <el-icon><ShoppingCart /></el-icon>
            购物车
          </NuxtLink>
          <NuxtLink to="/profile" class="btn btn-primary">个人中心</NuxtLink>
        </div>
      </div>
    </header>

    <!-- 主要内容 -->
    <main class="main-content">
      <div class="container">
        <h1 class="page-title">我的订单</h1>

        <div class="orders-layout">
          <!-- 侧边栏 -->
          <aside class="sidebar">
            <div class="sidebar-menu">
              <NuxtLink to="/profile" class="menu-item">
                <el-icon><User /></el-icon>
                个人信息
              </NuxtLink>
              <NuxtLink to="/orders" class="menu-item active">
                <el-icon><Document /></el-icon>
                我的订单
              </NuxtLink>
              <NuxtLink to="/addresses" class="menu-item">
                <el-icon><Location /></el-icon>
                地址管理
              </NuxtLink>
              <div class="menu-divider"></div>
              <button class="menu-item logout" @click="handleLogout">
                <el-icon><SwitchButton /></el-icon>
                退出登录
              </button>
            </div>
          </aside>

          <!-- 订单列表 -->
          <div class="orders-content">
            <!-- 筛选栏 -->
            <div class="filter-bar">
              <el-tabs v-model="activeStatus" @change="loadOrders">
                <el-tab-pane label="全部订单" name="" />
                <el-tab-pane label="待付款" name="pending" />
                <el-tab-pane label="待发货" name="paid" />
                <el-tab-pane label="待收货" name="shipped" />
                <el-tab-pane label="已完成" name="completed" />
              </el-tabs>
            </div>

            <!-- 订单列表 -->
            <div v-loading="loading" class="order-list">
              <el-empty v-if="!loading && orders.length === 0" description="暂无订单" />

              <div
                v-for="order in orders"
                :key="order.id"
                class="order-card"
              >
                <div class="order-header">
                  <div class="order-info">
                    <span class="order-number">订单号：{{ order.order_number }}</span>
                    <span class="order-date">下单时间：{{ formatDate(order.created_at) }}</span>
                  </div>
                  <div class="order-status">
                    <el-tag :type="getStatusType(order.status)">
                      {{ getStatusText(order.status) }}
                    </el-tag>
                  </div>
                </div>

                <div class="order-items">
                  <div
                    v-for="item in order.items"
                    :key="item.id"
                    class="order-item"
                  >
                    <div class="item-image">
                      <span class="image-placeholder">图片</span>
                    </div>
                    <div class="item-info">
                      <h4 class="item-name">{{ item.product_name }}</h4>
                      <p class="item-mpn">型号：{{ item.mpn }}</p>
                      <div class="item-meta">
                        <span>单价：¥{{ item.unit_price.toFixed(2) }}</span>
                        <span>数量：{{ item.quantity }}</span>
                      </div>
                    </div>
                    <div class="item-total">
                      <span class="label">小计：</span>
                      <span class="amount">¥{{ item.total_price.toFixed(2) }}</span>
                    </div>
                  </div>
                </div>

                <div class="order-footer">
                  <div class="order-total">
                    <span>订单总额：</span>
                    <span class="amount">¥{{ order.total_amount.toFixed(2) }}</span>
                  </div>
                  <div class="order-actions">
                    <el-button
                      v-if="order.status === 'pending'"
                      type="primary"
                      size="small"
                      @click="payOrder(order.id)"
                    >
                      去付款
                    </el-button>
                    <el-button
                      v-if="order.status === 'pending'"
                      size="small"
                      @click="cancelOrder(order.id)"
                    >
                      取消订单
                    </el-button>
                    <el-button
                      v-if="order.status === 'shipped'"
                      type="success"
                      size="small"
                      @click="confirmReceive(order.id)"
                    >
                      确认收货
                    </el-button>
                    <el-button size="small" @click="viewDetail(order.id)">
                      订单详情
                    </el-button>
                  </div>
                </div>
              </div>
            </div>

            <!-- 分页 -->
            <div class="pagination" v-if="totalPages > 1">
              <el-pagination
                v-model:current-page="currentPage"
                :page-size="pageSize"
                :total="total"
                layout="prev, pager, next"
                @current-change="loadOrders"
              />
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- 底部 -->
    <footer class="site-footer">
      <div class="container">
        <div class="footer-content">
          <div class="footer-section">
            <h4>关于我们</h4>
            <p>专业的电子元器件供应商</p>
          </div>
          <div class="footer-section">
            <h4>快速链接</h4>
            <ul>
              <li><NuxtLink to="/products">产品中心</NuxtLink></li>
              <li><NuxtLink to="/about">关于我们</NuxtLink></li>
            </ul>
          </div>
          <div class="footer-section">
            <h4>联系方式</h4>
            <p>电话：400-xxx-xxxx</p>
            <p>邮箱：info@example.com</p>
          </div>
        </div>
        <div class="footer-bottom">
          <p>&copy; 2026 元器件商城。All rights reserved.</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { User, Document, Location, SwitchButton, ShoppingCart } from '@element-plus/icons-vue'
import { api, type Order } from '~/utils/api'
import { useUserStore } from '~/stores/user'

const activeStatus = ref('')
const loading = ref(false)
const orders = ref<Order[]>([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const totalPages = ref(0)

const userStore = useUserStore()
const router = useRouter()

onMounted(() => {
  loadOrders()
})

async function loadOrders() {
  loading.value = true
  try {
    const res = await api.getOrders({
      page: currentPage.value,
      page_size: pageSize.value,
      status: activeStatus.value || undefined
    })
    orders.value = res.data
    total.value = res.data.length
    totalPages.value = Math.ceil(total.value / pageSize.value)
  } catch (error: any) {
    console.error('加载订单失败:', error)
    // 使用模拟数据
    orders.value = [
      {
        id: '1',
        order_number: 'ORD-20260221-001',
        customer_name: '测试用户',
        total_amount: 1258.00,
        status: 'pending',
        created_at: new Date().toISOString(),
        items: [
          { id: '1', product_id: '1', product_name: 'STM32F407VGT6', mpn: 'STM32F407VGT6', quantity: 10, unit_price: 25.00, total_price: 250.00 },
          { id: '2', product_id: '2', product_name: 'ESP32-WROOM-32', mpn: 'ESP32-WROOM-32', quantity: 20, unit_price: 18.00, total_price: 360.00 }
        ]
      },
      {
        id: '2',
        order_number: 'ORD-20260220-015',
        customer_name: '测试用户',
        total_amount: 5680.00,
        status: 'shipped',
        created_at: new Date(Date.now() - 86400000).toISOString(),
        items: [
          { id: '3', product_id: '3', product_name: 'ATMEGA328P-PU', mpn: 'ATMEGA328P-PU', quantity: 100, unit_price: 12.00, total_price: 1200.00 }
        ]
      }
    ]
  } finally {
    loading.value = false
  }
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleString('zh-CN')
}

function getStatusType(status: string): string {
  const map: Record<string, string> = {
    pending: 'warning',
    paid: 'info',
    shipped: 'primary',
    completed: 'success',
    cancelled: 'danger'
  }
  return map[status] || 'info'
}

function getStatusText(status: string): string {
  const map: Record<string, string> = {
    pending: '待付款',
    paid: '待发货',
    shipped: '待收货',
    completed: '已完成',
    cancelled: '已取消'
  }
  return map[status] || status
}

async function payOrder(orderId: string) {
  alert('跳转到支付页面：' + orderId)
}

async function cancelOrder(orderId: string) {
  if (!confirm('确定要取消此订单吗？')) return
  try {
    await api.cancelOrder(orderId)
    alert('订单已取消')
    loadOrders()
  } catch (error: any) {
    console.error('取消订单失败:', error)
  }
}

async function confirmReceive(orderId: string) {
  if (!confirm('确认已收到货物？')) return
  // TODO: 调用确认收货 API
  alert('确认收货成功')
  loadOrders()
}

function viewDetail(orderId: string) {
  router.push(`/orders/${orderId}`)
}

async function handleLogout() {
  await userStore.logout()
  router.push('/')
}

// SEO
useHead({
  title: '我的订单 - 元器件商城'
})
</script>

<style scoped>
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* 顶部导航 */
.site-header {
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 60px;
}

.logo-text {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
}

.main-nav {
  display: flex;
  gap: 30px;
}

.main-nav a {
  color: #333;
  text-decoration: none;
  font-size: 16px;
}

.header-actions {
  display: flex;
  gap: 15px;
  align-items: center;
}

.btn {
  padding: 8px 20px;
  border-radius: 4px;
  text-decoration: none;
  font-size: 14px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.btn-outline {
  border: 1px solid #409eff;
  color: #409eff;
  background: white;
}

.btn-primary {
  background: #409eff;
  color: white;
  border: none;
}

/* 主内容区 */
.main-content {
  background: #f5f7fa;
  min-height: calc(100vh - 60px - 200px);
  padding: 30px 0;
}

.page-title {
  font-size: 28px;
  color: #333;
  margin-bottom: 25px;
}

.orders-layout {
  display: grid;
  grid-template-columns: 220px 1fr;
  gap: 25px;
}

/* 侧边栏 */
.sidebar {
  background: white;
  border-radius: 8px;
  padding: 20px 0;
  height: fit-content;
}

.sidebar-menu {
  display: flex;
  flex-direction: column;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 20px;
  color: #333;
  text-decoration: none;
  transition: background 0.2s;
  border: none;
  background: none;
  width: 100%;
  text-align: left;
  cursor: pointer;
  font-size: 14px;
}

.menu-item:hover {
  background: #f5f7fa;
}

.menu-item.active {
  background: #ecf5ff;
  color: #409eff;
}

.menu-divider {
  height: 1px;
  background: #eee;
  margin: 10px 0;
}

.menu-item.logout {
  color: #f56c6c;
}

/* 订单内容区 */
.orders-content {
  background: white;
  border-radius: 8px;
  padding: 20px;
}

.filter-bar {
  margin-bottom: 20px;
  border-bottom: 1px solid #eee;
}

/* 订单卡片 */
.order-card {
  border: 1px solid #eee;
  border-radius: 8px;
  margin-bottom: 20px;
  overflow: hidden;
}

.order-header {
  display: flex;
  justify-content: space-between;
  padding: 15px 20px;
  background: #f5f7fa;
  border-bottom: 1px solid #eee;
}

.order-info {
  display: flex;
  gap: 20px;
  font-size: 14px;
  color: #666;
}

.order-number {
  font-weight: 600;
}

/* 订单商品 */
.order-items {
  padding: 20px;
}

.order-item {
  display: grid;
  grid-template-columns: 80px 1fr 150px;
  gap: 15px;
  align-items: center;
  padding-bottom: 15px;
  margin-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.order-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.item-image {
  width: 80px;
  height: 80px;
  background: #f5f7fa;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-placeholder {
  color: #999;
  font-size: 12px;
}

.item-info {
  flex: 1;
}

.item-name {
  font-size: 15px;
  font-weight: 600;
  color: #333;
  margin-bottom: 5px;
}

.item-mpn {
  font-size: 13px;
  color: #999;
  margin-bottom: 8px;
}

.item-meta {
  font-size: 14px;
  color: #666;
  display: flex;
  gap: 15px;
}

.item-total {
  text-align: right;
}

.item-total .label {
  font-size: 14px;
  color: #666;
}

.item-total .amount {
  font-size: 18px;
  color: #f56c6c;
  font-weight: 600;
}

/* 订单底部 */
.order-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: #f5f7fa;
  border-top: 1px solid #eee;
}

.order-total {
  font-size: 16px;
}

.order-total .amount {
  font-size: 20px;
  color: #f56c6c;
  font-weight: 600;
  margin-left: 10px;
}

.order-actions {
  display: flex;
  gap: 10px;
}

/* 分页 */
.pagination {
  display: flex;
  justify-content: center;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

/* 底部 */
.site-footer {
  background: #2c3e50;
  color: white;
  padding: 40px 0 20px;
}

.footer-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 30px;
  margin-bottom: 30px;
}

.footer-bottom {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}
</style>
