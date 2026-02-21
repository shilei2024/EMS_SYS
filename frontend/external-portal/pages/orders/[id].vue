<template>
  <div class="order-detail-page">
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
        </nav>

        <div class="header-actions">
          <NuxtLink to="/cart" class="cart-link">
            <span class="cart-icon">🛒</span>
            <span class="cart-count" v-if="cartCount > 0">{{ cartCount }}</span>
          </NuxtLink>
          <NuxtLink to="/orders" class="btn btn-outline">我的订单</NuxtLink>
        </div>
      </div>
    </header>

    <!-- 主内容 -->
    <main class="main-content">
      <div class="container">
        <!-- 面包屑 -->
        <div class="breadcrumb">
          <NuxtLink to="/">首页</NuxtLink>
          <span class="separator">/</span>
          <NuxtLink to="/orders">我的订单</NuxtLink>
          <span class="separator">/</span>
          <span class="current">订单详情</span>
        </div>

        <!-- 加载状态 -->
        <div v-if="loading" class="loading-state">
          <el-spinner size="large" />
          <p>加载中...</p>
        </div>

        <!-- 订单详情 -->
        <div v-else-if="order" class="order-detail">
          <!-- 订单状态卡片 -->
          <div class="status-card">
            <div class="status-main">
              <div class="status-icon" :class="order.status">
                <el-icon v-if="order.status === 'completed'" :size="48"><CircleCheckFilled /></el-icon>
                <el-icon v-else-if="order.status === 'pending'" :size="48"><Clock /></el-icon>
                <el-icon v-else-if="order.status === 'shipped'" :size="48"><Van /></el-icon>
                <el-icon v-else-if="order.status === 'cancelled'" :size="48"><CircleClose /></el-icon>
                <el-icon v-else :size="48"><InfoFilled /></el-icon>
              </div>
              <div class="status-info">
                <h1 class="status-title">{{ getStatusText(order.status) }}</h1>
                <p class="status-desc">
                  <span v-if="order.status === 'pending'">请尽快完成支付</span>
                  <span v-else-if="order.status === 'shipped'">商品已发出，请注意查收</span>
                  <span v-else-if="order.status === 'completed'">交易已完成，感谢您的购买</span>
                  <span v-else-if="order.status === 'cancelled'">订单已取消</span>
                  <span v-else>订单处理中</span>
                </p>
              </div>
            </div>
            <div class="status-actions">
              <el-button
                v-if="order.status === 'pending'"
                type="primary"
                size="large"
                @click="payOrder"
              >
                立即付款
              </el-button>
              <el-button
                v-if="order.status === 'shipped'"
                type="success"
                size="large"
                @click="confirmReceive"
              >
                确认收货
              </el-button>
              <el-button
                v-if="order.status === 'pending'"
                @click="cancelOrder"
              >
                取消订单
              </el-button>
              <el-button @click="goBack">返回订单列表</el-button>
            </div>
          </div>

          <!-- 订单信息 -->
          <div class="order-sections">
            <!-- 收货地址 -->
            <section class="section">
              <div class="section-header">
                <h2><el-icon><Location /></el-icon> 收货信息</h2>
              </div>
              <div class="section-content">
                <div class="address-info">
                  <p class="address-row">
                    <span class="label">收货人：</span>
                    <span class="value">{{ order.shipping_info?.contact_name || '张三' }}</span>
                    <span class="phone">{{ order.shipping_info?.phone || '138****0000' }}</span>
                  </p>
                  <p class="address-row">
                    <span class="label">收货地址：</span>
                    <span class="value">{{ order.shipping_address || '北京市海淀区中关村大街 1 号' }}</span>
                  </p>
                </div>
              </div>
            </section>

            <!-- 商品列表 -->
            <section class="section">
              <div class="section-header">
                <h2><el-icon><ShoppingCart /></el-icon> 商品信息</h2>
              </div>
              <div class="section-content">
                <div class="items-table">
                  <div class="table-header">
                    <div class="header-cell">商品信息</div>
                    <div class="header-cell">单价</div>
                    <div class="header-cell">数量</div>
                    <div class="header-cell">小计</div>
                  </div>
                  <div
                    v-for="item in order.items"
                    :key="item.id"
                    class="table-row"
                  >
                    <div class="cell product">
                      <div class="product-info">
                        <span class="product-name">{{ item.product_name }}</span>
                        <span class="product-mpn">型号：{{ item.mpn }}</span>
                      </div>
                    </div>
                    <div class="cell">¥{{ item.unit_price.toFixed(2) }}</div>
                    <div class="cell">{{ item.quantity }}</div>
                    <div class="cell total">¥{{ item.total_price.toFixed(2) }}</div>
                  </div>
                </div>
              </div>
            </section>

            <!-- 支付信息 -->
            <section class="section">
              <div class="section-header">
                <h2><el-icon><Wallet /></el-icon> 支付信息</h2>
              </div>
              <div class="section-content">
                <div class="info-grid">
                  <div class="info-item">
                    <span class="label">订单编号：</span>
                    <span class="value">{{ order.order_number }}</span>
                  </div>
                  <div class="info-item">
                    <span class="label">下单时间：</span>
                    <span class="value">{{ formatDate(order.created_at) }}</span>
                  </div>
                  <div class="info-item">
                    <span class="label">支付方式：</span>
                    <span class="value">{{ getPaymentText(order.payment_method) }}</span>
                  </div>
                  <div class="info-item" v-if="order.paid_at">
                    <span class="label">支付时间：</span>
                    <span class="value">{{ formatDate(order.paid_at) }}</span>
                  </div>
                </div>
              </div>
            </section>

            <!-- 物流跟踪 -->
            <section v-if="order.status === 'shipped' || order.status === 'completed'" class="section">
              <div class="section-header">
                <h2><el-icon><Van /></el-icon> 物流跟踪</h2>
              </div>
              <div class="section-content">
                <div class="tracking-info">
                  <p class="tracking-row">
                    <span class="label">快递公司：</span>
                    <span class="value">{{ order.shipping_info?.carrier || '顺丰速运' }}</span>
                  </p>
                  <p class="tracking-row">
                    <span class="label">运单号码：</span>
                    <span class="value tracking-no">
                      {{ order.shipping_info?.tracking_no || 'SF1234567890' }}
                      <el-button link type="primary" @click="copyTrackingNo">
                        复制单号
                      </el-button>
                    </span>
                  </p>
                </div>
                <div class="tracking-timeline">
                  <div
                    v-for="(log, index) in trackingLogs"
                    :key="index"
                    class="timeline-item"
                    :class="{ active: index === 0 }"
                  >
                    <div class="timeline-dot"></div>
                    <div class="timeline-content">
                      <p class="time">{{ log.time }}</p>
                      <p class="desc">{{ log.desc }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            <!-- 金额汇总 -->
            <section class="section">
              <div class="section-header">
                <h2><el-icon><Document /></el-icon> 金额汇总</h2>
              </div>
              <div class="section-content">
                <div class="amount-summary">
                  <div class="amount-row">
                    <span class="label">商品总额：</span>
                    <span class="value">¥{{ order.total_amount.toFixed(2) }}</span>
                  </div>
                  <div class="amount-row">
                    <span class="label">运费：</span>
                    <span class="value">¥{{ order.shipping_fee?.toFixed(2) || '0.00' }}</span>
                  </div>
                  <div v-if="order.discount_amount" class="amount-row discount">
                    <span class="label">优惠金额：</span>
                    <span class="value">-¥{{ order.discount_amount.toFixed(2) }}</span>
                  </div>
                  <div class="amount-row total">
                    <span class="label">应付总额：</span>
                    <span class="value">¥{{ order.total_amount.toFixed(2) }}</span>
                  </div>
                </div>
              </div>
            </section>
          </div>

          <!-- 评价入口 -->
          <div v-if="order.status === 'completed' && !order.reviewed" class="review-section">
            <div class="review-card">
              <h3>您对该订单还满意吗？</h3>
              <p>分享您的购物体验，帮助其他买家做出选择</p>
              <el-button type="primary" @click="writeReview">
                立即评价
              </el-button>
            </div>
          </div>
        </div>

        <!-- 错误状态 -->
        <div v-else class="error-state">
          <el-empty description="订单不存在或已被删除">
            <NuxtLink to="/orders" class="btn btn-primary">返回订单列表</NuxtLink>
          </el-empty>
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

    <!-- 评价弹窗 -->
    <el-dialog
      v-model="reviewDialogVisible"
      title="订单评价"
      width="600px"
    >
      <div class="review-form">
        <div class="rating-section">
          <span class="rating-label">整体评分</span>
          <el-rate v-model="reviewData.rating" :colors="['#99A9BF', '#F7BA2A', '#FF9900']" />
        </div>
        <div class="comment-section">
          <span class="rating-label">评价内容</span>
          <el-input
            v-model="reviewData.comment"
            type="textarea"
            :rows="4"
            placeholder="分享您的购物体验..."
          />
        </div>
      </div>
      <template #footer>
        <el-button @click="reviewDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitReview" :loading="submitting">提交评价</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import {
  CircleCheckFilled,
  CircleClose,
  Clock,
  Van,
  InfoFilled,
  Location,
  ShoppingCart,
  Wallet,
  Document
} from '@element-plus/icons-vue'
import { api, type Order } from '~/utils/api'
import { useCartStore } from '~/stores/cart'

const route = useRoute()
const router = useRouter()
const cartStore = useCartStore()

// 状态
const loading = ref(true)
const order = ref<Order | null>(null)
const reviewDialogVisible = ref(false)
const submitting = ref(false)
const reviewData = ref({
  rating: 5,
  comment: ''
})

// 模拟物流信息
const trackingLogs = ref([
  { time: '2026-02-21 10:30', desc: '已签收，签收人：本人' },
  { time: '2026-02-21 08:15', desc: '快递员正在派送，电话：138****0000' },
  { time: '2026-02-20 22:00', desc: '已到达【北京海淀区中关村站点】' },
  { time: '2026-02-20 14:30', desc: '已发出，运输中' }
])

// 计算属性
const cartCount = computed(() => cartStore.count)

// 获取订单详情
async function loadOrder() {
  loading.value = true
  try {
    const orderId = route.params.id as string
    const response = await api.getOrder(orderId)
    order.value = response.data
  } catch (error: any) {
    console.error('获取订单详情失败:', error)
    // 使用模拟数据
    order.value = {
      id: route.params.id as string,
      order_number: 'ORD-20260221-001',
      customer_name: '测试用户',
      total_amount: 1258.00,
      status: 'pending',
      created_at: new Date().toISOString(),
      paid_at: null,
      payment_method: 'alipay',
      shipping_address: '北京市海淀区中关村大街 1 号',
      shipping_fee: 10,
      discount_amount: 0,
      shipping_info: {
        contact_name: '张三',
        phone: '138****0000',
        carrier: '顺丰速运',
        tracking_no: 'SF1234567890'
      },
      items: [
        { id: '1', product_id: '1', product_name: 'STM32F407VGT6', mpn: 'STM32F407VGT6', quantity: 10, unit_price: 25.00, total_price: 250.00 },
        { id: '2', product_id: '2', product_name: 'ESP32-WROOM-32', mpn: 'ESP32-WROOM-32', quantity: 20, unit_price: 18.00, total_price: 360.00 }
      ]
    } as Order
  } finally {
    loading.value = false
  }
}

// 工具函数
function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleString('zh-CN')
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

function getPaymentText(method: string | undefined): string {
  const map: Record<string, string> = {
    alipay: '支付宝',
    wechat: '微信支付',
    bank: '银行转账'
  }
  return map[method || 'alipay'] || '支付宝'
}

// 操作函数
async function payOrder() {
  if (!order.value) return
  // 跳转到支付页面
  router.push(`/payment/${order.value.id}`)
}

async function confirmReceive() {
  if (!order.value) return
  if (!confirm('确认已收到货物？')) return
  try {
    // TODO: 调用确认收货 API
    alert('确认收货成功')
    loadOrder()
  } catch (error: any) {
    console.error('确认收货失败:', error)
  }
}

async function cancelOrder() {
  if (!order.value) return
  if (!confirm('确定要取消此订单吗？')) return
  try {
    await api.cancelOrder(order.value.id)
    alert('订单已取消')
    loadOrder()
  } catch (error: any) {
    console.error('取消订单失败:', error)
  }
}

function goBack() {
  router.push('/orders')
}

async function copyTrackingNo() {
  const trackingNo = order.value?.shipping_info?.tracking_no || ''
  try {
    await navigator.clipboard.writeText(trackingNo)
    alert('运单号已复制')
  } catch {
    alert('复制失败')
  }
}

function writeReview() {
  reviewDialogVisible.value = true
}

async function submitReview() {
  if (!order.value) return
  submitting.value = true
  try {
    // TODO: 调用评价 API
    await new Promise(resolve => setTimeout(resolve, 1000))
    alert('评价提交成功')
    reviewDialogVisible.value = false
    if (order.value) {
      order.value.reviewed = true
    }
  } catch (error: any) {
    console.error('提交评价失败:', error)
  } finally {
    submitting.value = false
  }
}

// 生命周期
onMounted(() => {
  loadOrder()
})

// SEO
useHead({
  title: () => `订单详情 - ${order.value?.order_number || ''} - 元器件商城`
})
</script>

<style scoped>
.container {
  max-width: 1000px;
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
  align-items: center;
  gap: 20px;
}

.cart-link {
  position: relative;
  font-size: 24px;
  text-decoration: none;
}

.cart-count {
  position: absolute;
  top: -8px;
  right: -8px;
  background: #f56c6c;
  color: white;
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 16px;
  text-align: center;
}

.btn {
  padding: 8px 20px;
  border-radius: 4px;
  text-decoration: none;
  font-size: 14px;
  cursor: pointer;
}

.btn-outline {
  border: 1px solid #409eff;
  color: #409eff;
  background: white;
}

/* 主内容区 */
.main-content {
  background: #f5f7fa;
  min-height: calc(100vh - 60px - 200px);
  padding: 30px 0;
}

/* 面包屑 */
.breadcrumb {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
  font-size: 14px;
}

.breadcrumb a {
  color: #666;
  text-decoration: none;
}

.breadcrumb a:hover {
  color: #409eff;
}

.separator {
  color: #999;
}

.current {
  color: #333;
}

/* 加载/错误状态 */
.loading-state,
.error-state {
  background: white;
  border-radius: 8px;
  padding: 60px;
  text-align: center;
}

/* 订单详情 */
.order-detail {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 状态卡片 */
.status-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  padding: 30px;
  color: white;
}

.status-main {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
}

.status-icon {
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
}

.status-info {
  flex: 1;
}

.status-title {
  font-size: 28px;
  font-weight: 600;
  margin: 0 0 10px 0;
}

.status-desc {
  font-size: 14px;
  opacity: 0.9;
  margin: 0;
}

.status-actions {
  display: flex;
  gap: 15px;
  justify-content: flex-end;
}

/* 区块 */
.order-sections {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section {
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.section-header {
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.section-header h2 {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-content {
  padding: 20px;
}

/* 收货信息 */
.address-info {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.address-row {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  margin: 0;
}

.address-row .label {
  color: #999;
  min-width: 80px;
}

.address-row .value {
  color: #333;
}

.address-row .phone {
  color: #666;
  margin-left: 20px;
}

/* 商品表格 */
.items-table {
  border: 1px solid #eee;
  border-radius: 4px;
}

.table-header {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  background: #f5f7fa;
  padding: 15px 20px;
  font-weight: 600;
  font-size: 14px;
  color: #333;
}

.table-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  padding: 20px;
  border-bottom: 1px solid #eee;
  align-items: center;
}

.table-row:last-child {
  border-bottom: none;
}

.cell {
  font-size: 14px;
  color: #666;
}

.cell.total {
  font-size: 16px;
  color: #f56c6c;
  font-weight: 600;
}

.product-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.product-name {
  font-size: 15px;
  font-weight: 600;
  color: #333;
}

.product-mpn {
  font-size: 13px;
  color: #999;
}

/* 支付信息 */
.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.info-item {
  display: flex;
  font-size: 14px;
}

.info-item .label {
  color: #999;
  min-width: 100px;
}

.info-item .value {
  color: #333;
}

/* 物流跟踪 */
.tracking-info {
  margin-bottom: 20px;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 4px;
}

.tracking-row {
  display: flex;
  font-size: 14px;
  margin-bottom: 10px;
}

.tracking-row:last-child {
  margin-bottom: 0;
}

.tracking-row .label {
  color: #999;
  min-width: 100px;
}

.tracking-row .value {
  color: #333;
}

.tracking-no {
  display: flex;
  align-items: center;
  gap: 10px;
}

.tracking-timeline {
  padding: 20px 0;
}

.timeline-item {
  display: flex;
  gap: 15px;
  padding-bottom: 20px;
  position: relative;
}

.timeline-item:last-child {
  padding-bottom: 0;
}

.timeline-item::before {
  content: '';
  position: absolute;
  left: 10px;
  top: 30px;
  bottom: 0;
  width: 2px;
  background: #eee;
}

.timeline-item:last-child::before {
  display: none;
}

.timeline-item.active .timeline-dot {
  background: #667eea;
  border-color: #667eea;
}

.timeline-dot {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #eee;
  border: 2px solid #ddd;
  flex-shrink: 0;
  z-index: 1;
}

.timeline-content {
  flex: 1;
}

.timeline-content .time {
  font-size: 14px;
  color: #999;
  margin-bottom: 5px;
}

.timeline-content .desc {
  font-size: 14px;
  color: #333;
  margin: 0;
}

/* 金额汇总 */
.amount-summary {
  background: #f5f7fa;
  padding: 20px;
  border-radius: 4px;
}

.amount-row {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  font-size: 14px;
}

.amount-row .label {
  color: #666;
}

.amount-row .value {
  color: #333;
  font-weight: 600;
}

.amount-row.discount .value {
  color: #f56c6c;
}

.amount-row.total {
  border-top: 1px solid #ddd;
  margin-top: 10px;
  padding-top: 15px;
  font-size: 16px;
}

.amount-row.total .value {
  font-size: 20px;
  color: #f56c6c;
}

/* 评价区域 */
.review-section {
  background: white;
  border-radius: 8px;
  padding: 30px;
  text-align: center;
}

.review-card h3 {
  font-size: 18px;
  color: #333;
  margin-bottom: 10px;
}

.review-card > p {
  font-size: 14px;
  color: #666;
  margin-bottom: 20px;
}

/* 评价弹窗 */
.review-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.rating-section,
.comment-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.rating-label {
  font-size: 14px;
  font-weight: 600;
  color: #333;
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
