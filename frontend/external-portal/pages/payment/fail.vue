<template>
  <div class="payment-fail-page">
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
        <div class="fail-card">
          <!-- 失败图标 -->
          <div class="fail-icon">
            <el-icon :size="80" color="#f56c6c"><CircleCloseFilled /></el-icon>
          </div>

          <!-- 失败信息 -->
          <h1 class="fail-title">支付失败</h1>
          <p class="fail-desc">{{ failMessage }}</p>

          <!-- 失败原因 -->
          <div v-if="failReason" class="fail-reason">
            <h3>失败原因</h3>
            <p>{{ failReason }}</p>
          </div>

          <!-- 操作按钮 -->
          <div class="action-buttons">
            <NuxtLink :to="`/payment/${orderId}`" class="btn btn-primary">
              重新支付
            </NuxtLink>
            <NuxtLink to="/orders" class="btn btn-outline">
              查看订单
            </NuxtLink>
            <NuxtLink to="/products" class="btn btn-outline">
              继续购物
            </NuxtLink>
          </div>

          <!-- 提示信息 -->
          <div class="tips">
            <el-icon><InfoFilled /></el-icon>
            <span>如多次支付失败，请联系客服：400-xxx-xxxx</span>
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
import { CircleCloseFilled, InfoFilled } from '@element-plus/icons-vue'

const route = useRoute()

const orderId = ref(route.query.order_id as string)
const failMessage = ref('支付过程中出现错误，请稍后重试')
const failReason = ref('')

// 解析失败原因
const errorCode = route.query.error_code as string
const errorMsg = route.query.error_msg as string

if (errorCode || errorMsg) {
  failMessage.value = '支付失败'
  failReason.value = errorMsg || `错误代码：${errorCode || 'UNKNOWN'}`
}

// SEO
useHead({
  title: '支付失败 - 元器件商城'
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

/* 失败卡片 */
.fail-card {
  background: white;
  border-radius: 8px;
  padding: 60px 40px;
  text-align: center;
}

.fail-icon {
  margin-bottom: 20px;
}

.fail-title {
  font-size: 28px;
  color: #f56c6c;
  margin-bottom: 15px;
}

.fail-desc {
  font-size: 16px;
  color: #666;
  margin-bottom: 30px;
}

/* 失败原因 */
.fail-reason {
  background: #fef0f0;
  border: 1px solid #fde2e2;
  border-radius: 4px;
  padding: 20px;
  margin-bottom: 30px;
  text-align: left;
}

.fail-reason h3 {
  font-size: 14px;
  color: #f56c6c;
  margin-bottom: 10px;
}

.fail-reason p {
  font-size: 14px;
  color: #666;
  margin: 0;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  justify-content: center;
  gap: 15px;
  flex-wrap: wrap;
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
