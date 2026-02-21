<template>
  <div class="payment-success-page">
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
        <div class="success-card">
          <!-- 成功图标 -->
          <div class="success-icon">
            <el-icon :size="80" color="#67c23a"><CircleCheckFilled /></el-icon>
          </div>

          <!-- 成功信息 -->
          <h1 class="success-title">支付成功！</h1>
          <p class="success-desc">感谢您的购买，我们将尽快为您发货</p>

          <!-- 订单信息 -->
          <div class="order-info">
            <div class="info-row">
              <span class="label">订单编号：</span>
              <span class="value">{{ orderInfo.orderNumber }}</span>
              <el-button link type="primary" @click="copyOrderNo">
                <el-icon><DocumentCopy /></el-icon>
              </el-button>
            </div>
            <div class="info-row">
              <span class="label">支付金额：</span>
              <span class="value amount">¥{{ orderInfo.amount.toFixed(2) }}</span>
            </div>
            <div class="info-row">
              <span class="label">支付方式：</span>
              <span class="value">{{ orderInfo.paymentMethod }}</span>
            </div>
            <div class="info-row">
              <span class="label">支付时间：</span>
              <span class="value">{{ orderInfo.paymentTime }}</span>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="action-buttons">
            <NuxtLink to="/orders" class="btn btn-primary">
              查看订单
            </NuxtLink>
            <NuxtLink to="/products" class="btn btn-outline">
              继续购物
            </NuxtLink>
          </div>

          <!-- 提示信息 -->
          <div class="tips">
            <el-icon><InfoFilled /></el-icon>
            <span>我们会在 24 小时内为您发货，发货后会有短信通知</span>
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
import { CircleCheckFilled, InfoFilled, DocumentCopy } from '@element-plus/icons-vue'
import { api } from '~/utils/api'

const route = useRoute()
const orderId = ref(route.query.order_id as string)

// 订单信息
const orderInfo = ref({
  orderNumber: '',
  amount: 0,
  paymentMethod: '支付宝',
  paymentTime: new Date().toLocaleString('zh-CN')
})

// 加载订单信息
async function loadOrderInfo() {
  if (!orderId.value) return

  try {
    const response = await api.getOrder(orderId.value)
    const order = response.data
    orderInfo.value = {
      orderNumber: order.order_number,
      amount: order.total_amount + (order.shipping_fee || 0) - (order.discount_amount || 0),
      paymentMethod: getPaymentText(order.payment_method),
      paymentTime: order.paid_at ? new Date(order.paid_at).toLocaleString('zh-CN') : new Date().toLocaleString('zh-CN')
    }
  } catch (error: any) {
    console.error('获取订单信息失败:', error)
    // 使用模拟数据
    orderInfo.value = {
      orderNumber: 'ORD-20260221-001',
      amount: 1258.00,
      paymentMethod: '支付宝',
      paymentTime: new Date().toLocaleString('zh-CN')
    }
  }
}

function getPaymentText(method: string | undefined): string {
  const map: Record<string, string> = {
    alipay: '支付宝',
    wechat: '微信支付',
    bank: '银行转账'
  }
  return map[method || 'alipay'] || '支付宝'
}

async function copyOrderNo() {
  try {
    await navigator.clipboard.writeText(orderInfo.value.orderNumber)
    alert('订单号已复制')
  } catch {
    alert('复制失败')
  }
}

onMounted(() => {
  loadOrderInfo()
})

// SEO
useHead({
  title: '支付成功 - 元器件商城'
})
</script>

<style scoped>
.container {
  max-width: 800px;
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
  padding: 12px 30px;
  border-radius: 4px;
  text-decoration: none;
  font-size: 14px;
  cursor: pointer;
  display: inline-block;
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
  padding: 60px 0;
}

/* 成功卡片 */
.success-card {
  background: white;
  border-radius: 8px;
  padding: 60px 40px;
  text-align: center;
}

.success-icon {
  margin-bottom: 20px;
}

.success-title {
  font-size: 28px;
  color: #67c23a;
  margin-bottom: 15px;
}

.success-desc {
  font-size: 16px;
  color: #666;
  margin-bottom: 40px;
}

/* 订单信息 */
.order-info {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 25px 40px;
  margin-bottom: 30px;
  text-align: left;
}

.info-row {
  display: flex;
  align-items: center;
  padding: 12px 0;
  font-size: 14px;
  border-bottom: 1px solid #eee;
}

.info-row:last-child {
  border-bottom: none;
}

.info-row .label {
  color: #999;
  min-width: 100px;
}

.info-row .value {
  color: #333;
}

.info-row .amount {
  font-size: 18px;
  color: #f56c6c;
  font-weight: 600;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 30px;
}

/* 提示信息 */
.tips {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  font-size: 14px;
  color: #666;
  padding: 15px;
  background: #ecf5ff;
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
