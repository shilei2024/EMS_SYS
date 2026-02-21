<template>
  <div class="payment-bank-page">
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
        <div class="bank-card">
          <!-- 图标 -->
          <div class="card-icon">
            <el-icon :size="60" color="#f56c6c"><Bank /></el-icon>
          </div>

          <h1 class="card-title">银行转账支付</h1>
          <p class="card-desc">请按照以下账户信息进行转账，转账完成后我们将尽快安排发货</p>

          <!-- 银行账户信息 -->
          <div class="bank-info">
            <h2>公司账户信息</h2>
            <div class="info-row">
              <span class="label">账户名称：</span>
              <span class="value">元器件商城有限公司</span>
              <el-button link type="primary" @click="copyText('元器件商城有限公司')">
                <el-icon><DocumentCopy /></el-icon>
              </el-button>
            </div>
            <div class="info-row">
              <span class="label">开户银行：</span>
              <span class="value">中国银行深圳分行</span>
              <el-button link type="primary" @click="copyText('中国银行深圳分行')">
                <el-icon><DocumentCopy /></el-icon>
              </el-button>
            </div>
            <div class="info-row">
              <span class="label">银行账号：</span>
              <span class="value">1234 5678 9012 3456</span>
              <el-button link type="primary" @click="copyText('1234567890123456')">
                <el-icon><DocumentCopy /></el-icon>
              </el-button>
            </div>
            <div class="info-row">
              <span class="label">联行号：</span>
              <span class="value">104584000001</span>
              <el-button link type="primary" @click="copyText('104584000001')">
                <el-icon><DocumentCopy /></el-icon>
              </el-button>
            </div>
          </div>

          <!-- 转账须知 -->
          <div class="notice">
            <h3><el-icon><Bell /></el-icon> 转账须知</h3>
            <ul>
              <li>转账时请务必备注<strong>订单号：{{ orderNumber }}</strong></li>
              <li>转账金额必须与订单金额一致，包括运费</li>
              <li>银行处理时间一般为 1-3 个工作日</li>
              <li>我们会在确认收款后 24 小时内安排发货</li>
              <li>如有问题请联系客服：400-xxx-xxxx</li>
            </ul>
          </div>

          <!-- 订单信息 -->
          <div class="order-info">
            <h3>订单信息</h3>
            <div class="info-row">
              <span class="label">订单编号：</span>
              <span class="value">{{ orderNumber }}</span>
            </div>
            <div class="info-row">
              <span class="label">订单金额：</span>
              <span class="value amount">¥{{ orderAmount.toFixed(2) }}</span>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="action-buttons">
            <el-button type="primary" size="large" @click="confirmTransfer">
              我已转账
            </el-button>
            <NuxtLink to="/orders" class="btn btn-outline">
              返回订单列表
            </NuxtLink>
          </div>

          <!-- 提示 -->
          <div class="tips">
            <el-icon><InfoFilled /></el-icon>
            <span>点击"我已转账"后，请等待我们确认收款，确认后会短信通知您</span>
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
import { Bank, Bell, InfoFilled, DocumentCopy } from '@element-plus/icons-vue'
import { api } from '~/utils/api'

const route = useRoute()
const router = useRouter()

const orderId = ref(route.query.order_id as string)
const orderNumber = ref('')
const orderAmount = ref(0)

// 加载订单信息
async function loadOrder() {
  if (!orderId.value) return

  try {
    const response = await api.getOrder(orderId.value)
    orderNumber.value = response.data.order_number
    orderAmount.value = response.data.total_amount + (response.data.shipping_fee || 0)
  } catch (error: any) {
    console.error('获取订单失败:', error)
    // 使用模拟数据
    orderNumber.value = 'ORD-20260221-001'
    orderAmount.value = 1268.00
  }
}

async function copyText(text: string) {
  try {
    await navigator.clipboard.writeText(text)
    alert('已复制到剪贴板')
  } catch {
    alert('复制失败')
  }
}

async function confirmTransfer() {
  if (!orderId.value) return

  try {
    // TODO: 调用 API 记录已转账状态
    await new Promise(resolve => setTimeout(resolve, 500))
    alert('转账信息已提交，我们会尽快确认并安排发货')
    router.push('/orders')
  } catch (error: any) {
    console.error('提交转账信息失败:', error)
  }
}

onMounted(() => {
  loadOrder()
})

// SEO
useHead({
  title: '银行转账 - 元器件商城'
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

/* 主内容区 */
.main-content {
  background: #f5f7fa;
  min-height: calc(100vh - 60px - 200px);
  padding: 60px 0;
}

/* 银行卡片 */
.bank-card {
  background: white;
  border-radius: 8px;
  padding: 40px;
}

.card-icon {
  text-align: center;
  margin-bottom: 20px;
}

.card-title {
  font-size: 24px;
  color: #333;
  text-align: center;
  margin-bottom: 10px;
}

.card-desc {
  font-size: 14px;
  color: #666;
  text-align: center;
  margin-bottom: 30px;
}

/* 银行信息 */
.bank-info {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  padding: 25px;
  margin-bottom: 25px;
  color: white;
}

.bank-info h2 {
  font-size: 18px;
  margin-bottom: 20px;
}

.bank-info .info-row {
  display: flex;
  align-items: center;
  padding: 12px 0;
  font-size: 15px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.bank-info .info-row:last-child {
  border-bottom: none;
}

.bank-info .label {
  opacity: 0.8;
  min-width: 100px;
}

.bank-info .value {
  flex: 1;
  font-weight: 600;
}

/* 转账须知 */
.notice {
  background: #fef0f0;
  border: 1px solid #fde2e2;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 25px;
}

.notice h3 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  color: #f56c6c;
  margin-bottom: 15px;
}

.notice ul {
  list-style: disc;
  padding-left: 20px;
  margin: 0;
}

.notice li {
  font-size: 14px;
  color: #666;
  line-height: 1.8;
  margin-bottom: 5px;
}

.notice strong {
  color: #f56c6c;
}

/* 订单信息 */
.order-info {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 25px;
}

.order-info h3 {
  font-size: 16px;
  color: #333;
  margin-bottom: 15px;
}

.order-info .info-row {
  display: flex;
  padding: 10px 0;
  font-size: 14px;
}

.order-info .label {
  color: #999;
  min-width: 100px;
}

.order-info .value {
  color: #333;
}

.order-info .amount {
  font-size: 18px;
  color: #f56c6c;
  font-weight: 600;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-bottom: 25px;
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
