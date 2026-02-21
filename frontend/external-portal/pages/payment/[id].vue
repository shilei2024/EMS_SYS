<template>
  <div class="payment-page">
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
          <NuxtLink to="/cart" class="btn btn-outline">购物车</NuxtLink>
          <NuxtLink to="/orders" class="btn btn-primary">我的订单</NuxtLink>
        </div>
      </div>
    </header>

    <!-- 主内容 -->
    <main class="main-content">
      <div class="container">
        <div class="payment-layout">
          <!-- 左侧：支付信息 -->
          <div class="payment-info">
            <h1 class="page-title">订单支付</h1>

            <!-- 订单摘要 -->
            <div class="order-summary-card">
              <div class="summary-row">
                <span class="label">订单编号：</span>
                <span class="value">{{ order?.order_number }}</span>
              </div>
              <div class="summary-row">
                <span class="label">商品名称：</span>
                <span class="value">{{ order?.items[0]?.product_name }} 等{{ order?.items.length }}件商品</span>
              </div>
              <div class="summary-row">
                <span class="label">订单金额：</span>
                <span class="value amount">¥{{ order?.total_amount.toFixed(2) }}</span>
              </div>
            </div>

            <!-- 支付方式 -->
            <div class="payment-methods">
              <h2 class="section-title">选择支付方式</h2>

              <!-- 支付宝 -->
              <div
                class="payment-option"
                :class="{ selected: selectedMethod === 'alipay' }"
                @click="selectedMethod = 'alipay'"
              >
                <div class="payment-radio">
                  <el-radio v-model="selectedMethod" value="alipay" />
                </div>
                <div class="payment-content">
                  <div class="payment-icon alipay">
                    <span>💳</span>
                  </div>
                  <div class="payment-name">
                    <h3>支付宝</h3>
                    <p>推荐使用</p>
                  </div>
                </div>
              </div>

              <!-- 微信支付 -->
              <div
                class="payment-option"
                :class="{ selected: selectedMethod === 'wechat' }"
                @click="selectedMethod = 'wechat'"
              >
                <div class="payment-radio">
                  <el-radio v-model="selectedMethod" value="wechat" />
                </div>
                <div class="payment-content">
                  <div class="payment-icon wechat">
                    <span>📱</span>
                  </div>
                  <div class="payment-name">
                    <h3>微信支付</h3>
                    <p>扫码支付</p>
                  </div>
                </div>
              </div>

              <!-- 银行转账 -->
              <div
                class="payment-option"
                :class="{ selected: selectedMethod === 'bank' }"
                @click="selectedMethod = 'bank'"
              >
                <div class="payment-radio">
                  <el-radio v-model="selectedMethod" value="bank" />
                </div>
                <div class="payment-content">
                  <div class="payment-icon bank">
                    <span>🏦</span>
                  </div>
                  <div class="payment-name">
                    <h3>银行转账</h3>
                    <p>对公转账</p>
                  </div>
                </div>
                <div v-if="selectedMethod === 'bank'" class="bank-info">
                  <p><strong>账户名称：</strong>元器件商城有限公司</p>
                  <p><strong>开户银行：</strong>中国银行深圳分行</p>
                  <p><strong>银行账号：</strong>1234 5678 9012 3456</p>
                </div>
              </div>
            </div>
          </div>

          <!-- 右侧：支付金额 -->
          <div class="payment-sidebar">
            <div class="payment-card">
              <div class="card-header">
                <h2>支付金额</h2>
              </div>
              <div class="card-body">
                <div class="total-amount">
                  <span class="label">应付总额</span>
                  <div class="amount">
                    <span class="symbol">¥</span>
                    <span class="value">{{ totalAmount.toFixed(2) }}</span>
                  </div>
                </div>

                <div class="detail-list">
                  <div class="detail-item">
                    <span>商品总额</span>
                    <span>¥{{ order?.total_amount.toFixed(2) }}</span>
                  </div>
                  <div class="detail-item">
                    <span>运费</span>
                    <span>¥{{ order?.shipping_fee?.toFixed(2) || '0.00' }}</span>
                  </div>
                  <div v-if="order?.discount_amount" class="detail-item discount">
                    <span>优惠</span>
                    <span>-¥{{ order.discount_amount.toFixed(2) }}</span>
                  </div>
                </div>

                <el-button
                  type="primary"
                  size="large"
                  class="pay-btn"
                  :loading="paying"
                  @click="handlePay"
                >
                  {{ paying ? '支付中...' : `立即支付 ¥${totalAmount.toFixed(2)}` }}
                </el-button>

                <p class="pay-tip">
                  <el-icon><InfoFilled /></el-icon>
                  支付完成后将跳转至支付结果页
                </p>
              </div>
            </div>

            <!-- 支付说明 -->
            <div class="payment-tips">
              <h3>支付说明</h3>
              <ul>
                <li>支付宝和微信支付支持扫码支付和快捷支付</li>
                <li>银行转账请备注订单号，到账后自动发货</li>
                <li>支付遇到问题请联系客服：400-xxx-xxxx</li>
              </ul>
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

    <!-- 支付二维码弹窗 -->
    <el-dialog
      v-model="qrDialogVisible"
      title="扫码支付"
      width="400px"
      :close-on-click-modal="false"
    >
      <div class="qr-content">
        <div class="qr-code">
          <img :src="qrCodeUrl" alt="支付二维码" />
        </div>
        <p class="qr-tip">请使用{{ selectedMethod === 'alipay' ? '支付宝' : '微信' }}扫码支付</p>
        <p class="qr-amount">支付金额：¥{{ totalAmount.toFixed(2) }}</p>
      </div>
      <div class="qr-status">
        <el-icon class="is-loading" :size="20"><Loading /></el-icon>
        <span>等待支付...</span>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { InfoFilled, Loading } from '@element-plus/icons-vue'
import { api, type Order } from '~/utils/api'

const route = useRoute()
const router = useRouter()

// 状态
const order = ref<Order | null>(null)
const loading = ref(true)
const paying = ref(false)
const selectedMethod = ref<'alipay' | 'wechat' | 'bank'>('alipay')
const qrDialogVisible = ref(false)
const qrCodeUrl = ref('')
const checkPaymentTimer = ref<NodeJS.Timeout | null>(null)

// 计算属性
const totalAmount = computed(() => {
  if (!order.value) return 0
  return order.value.total_amount + (order.value.shipping_fee || 0) - (order.value.discount_amount || 0)
})

// 获取订单信息
async function loadOrder() {
  loading.value = true
  try {
    const orderId = route.params.id as string
    const response = await api.getOrder(orderId)
    order.value = response.data
  } catch (error: any) {
    console.error('获取订单失败:', error)
    // 使用模拟数据
    order.value = {
      id: route.params.id as string,
      order_number: 'ORD-20260221-001',
      customer_name: '测试用户',
      total_amount: 1258.00,
      status: 'pending',
      created_at: new Date().toISOString(),
      payment_method: 'alipay',
      shipping_fee: 10,
      discount_amount: 0,
      items: [
        { id: '1', product_id: '1', product_name: 'STM32F407VGT6', mpn: 'STM32F407VGT6', quantity: 10, unit_price: 25.00, total_price: 250.00 },
        { id: '2', product_id: '2', product_name: 'ESP32-WROOM-32', mpn: 'ESP32-WROOM-32', quantity: 20, unit_price: 18.00, total_price: 360.00 }
      ]
    } as Order
  } finally {
    loading.value = false
  }
}

// 处理支付
async function handlePay() {
  if (!order.value) return

  paying.value = true

  try {
    if (selectedMethod.value === 'alipay' || selectedMethod.value === 'wechat') {
      // 生成支付二维码
      qrCodeUrl.value = `https://api.example.com/payment/qr?order_id=${order.value.id}&method=${selectedMethod.value}`
      qrDialogVisible.value = true

      // 轮询检查支付状态
      checkPaymentTimer.value = setInterval(() => {
        checkPaymentStatus()
      }, 3000)
    } else if (selectedMethod.value === 'bank') {
      // 银行转账，提交订单等待支付
      await submitBankPayment()
    }
  } catch (error: any) {
    console.error('支付失败:', error)
    alert('支付失败，请重试')
    paying.value = false
  }
}

// 检查支付状态
async function checkPaymentStatus() {
  if (!order.value) return

  try {
    const response = await api.getOrder(order.value.id)
    if (response.data.status !== 'pending') {
      // 支付成功
      if (checkPaymentTimer.value) {
        clearInterval(checkPaymentTimer.value)
      }
      qrDialogVisible.value = false
      router.push(`/payment/success?order_id=${order.value.id}`)
    }
  } catch (error: any) {
    console.error('检查支付状态失败:', error)
  }
}

// 提交银行转账
async function submitBankPayment() {
  if (!order.value) return

  try {
    // TODO: 调用 API 提交银行转账记录
    await new Promise(resolve => setTimeout(resolve, 1000))
    router.push(`/payment/bank?order_id=${order.value.id}`)
  } catch (error: any) {
    console.error('提交银行转账失败:', error)
  } finally {
    paying.value = false
  }
}

// 生命周期
onMounted(() => {
  loadOrder()
})

onUnmounted(() => {
  if (checkPaymentTimer.value) {
    clearInterval(checkPaymentTimer.value)
  }
})

// SEO
useHead({
  title: '订单支付 - 元器件商城'
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

.payment-layout {
  display: grid;
  grid-template-columns: 1fr 380px;
  gap: 25px;
}

/* 左侧支付信息 */
.payment-info {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-title {
  font-size: 28px;
  color: #333;
  margin: 0;
}

.order-summary-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  font-size: 14px;
}

.summary-row .label {
  color: #666;
}

.summary-row .value {
  color: #333;
}

.summary-row .amount {
  font-weight: 600;
  color: #f56c6c;
}

/* 支付方式 */
.payment-methods {
  background: white;
  border-radius: 8px;
  padding: 20px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 20px;
}

.payment-option {
  border: 2px solid #eee;
  border-radius: 8px;
  margin-bottom: 15px;
  cursor: pointer;
  transition: all 0.2s;
}

.payment-option:hover {
  border-color: #409eff;
}

.payment-option.selected {
  border-color: #409eff;
  background: #ecf5ff;
}

.payment-option {
  padding: 15px 20px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.payment-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.payment-radio {
  display: flex;
  align-items: center;
}

.payment-icon {
  width: 50px;
  height: 50px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.payment-icon.alipay {
  background: #1677ff;
}

.payment-icon.wechat {
  background: #07c160;
}

.payment-icon.bank {
  background: #f56c6c;
}

.payment-name h3 {
  font-size: 16px;
  color: #333;
  margin: 0;
}

.payment-name p {
  font-size: 12px;
  color: #999;
  margin: 5px 0 0 0;
}

.bank-info {
  background: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
  font-size: 14px;
  color: #666;
}

.bank-info p {
  margin: 5px 0;
}

/* 右侧侧边栏 */
.payment-sidebar {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.payment-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.card-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  color: white;
}

.card-header h2 {
  font-size: 18px;
  margin: 0;
}

.card-body {
  padding: 25px;
}

.total-amount {
  text-align: center;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.total-amount .label {
  display: block;
  font-size: 14px;
  color: #666;
  margin-bottom: 10px;
}

.total-amount .amount {
  display: flex;
  align-items: flex-start;
  justify-content: center;
  gap: 5px;
}

.total-amount .symbol {
  font-size: 20px;
  color: #f56c6c;
  font-weight: 600;
}

.total-amount .value {
  font-size: 36px;
  color: #f56c6c;
  font-weight: 700;
}

.detail-list {
  padding: 20px 0;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  font-size: 14px;
  color: #666;
}

.detail-item.discount {
  color: #f56c6c;
}

.pay-btn {
  width: 100%;
  height: 50px;
  font-size: 18px;
  font-weight: 600;
}

.pay-tip {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #999;
  margin: 15px 0 0 0;
  justify-content: center;
}

/* 支付说明 */
.payment-tips {
  background: white;
  border-radius: 8px;
  padding: 20px;
}

.payment-tips h3 {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 10px;
}

.payment-tips ul {
  list-style: disc;
  padding-left: 20px;
  margin: 0;
}

.payment-tips li {
  font-size: 13px;
  color: #666;
  line-height: 1.8;
  margin-bottom: 5px;
}

/* 二维码弹窗 */
.qr-content {
  text-align: center;
  padding: 20px 0;
}

.qr-code {
  margin-bottom: 15px;
}

.qr-code img {
  width: 200px;
  height: 200px;
}

.qr-tip {
  font-size: 16px;
  color: #333;
  margin-bottom: 10px;
}

.qr-amount {
  font-size: 18px;
  color: #f56c6c;
  font-weight: 600;
}

.qr-status {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #666;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 4px;
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
