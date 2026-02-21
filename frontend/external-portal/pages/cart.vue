<template>
  <div class="cart-page">
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
          <NuxtLink to="/login" class="btn btn-outline">登录</NuxtLink>
          <NuxtLink to="/register" class="btn btn-primary">注册</NuxtLink>
        </div>
      </div>
    </header>

    <!-- 主要内容 -->
    <main class="main-content">
      <div class="container">
        <h1 class="page-title">购物车</h1>

        <div v-if="cartStore.loading" class="loading">
          <el-spinner size="large" />
          <p>加载中...</p>
        </div>

        <div v-else-if="!cartStore.hasItems" class="empty-cart">
          <el-empty description="购物车是空的">
            <NuxtLink to="/products" class="btn btn-primary">去购物</NuxtLink>
          </el-empty>
        </div>

        <div v-else class="cart-content">
          <!-- 购物车列表 -->
          <div class="cart-table">
            <div class="cart-header">
              <div class="header-row">
                <span class="col-product">商品信息</span>
                <span class="col-price">单价</span>
                <span class="col-quantity">数量</span>
                <span class="col-subtotal">小计</span>
                <span class="col-action">操作</span>
              </div>
            </div>

            <div class="cart-body">
              <div
                v-for="item in cartStore.items"
                :key="item.id"
                class="cart-item"
              >
                <div class="item-product">
                  <div class="product-image">
                    <span class="image-placeholder">图片</span>
                  </div>
                  <div class="product-info">
                    <h3 class="product-name">{{ item.product.mpn }}</h3>
                    <p class="product-desc">{{ item.product.description }}</p>
                    <p class="product-mpn">型号：{{ item.product.mpn }}</p>
                  </div>
                </div>
                <div class="item-price">¥{{ item.product.price.toFixed(2) }}</div>
                <div class="item-quantity">
                  <el-input-number
                    v-model="item.quantity"
                    :min="1"
                    :max="item.product.stock"
                    size="small"
                    @change="updateQuantity(item)"
                  />
                  <span class="stock-tip">库存：{{ item.product.stock }}</span>
                </div>
                <div class="item-subtotal">
                  ¥{{ (item.product.price * item.quantity).toFixed(2) }}
                </div>
                <div class="item-action">
                  <el-button type="danger" size="small" @click="removeItem(item.id)">删除</el-button>
                </div>
              </div>
            </div>
          </div>

          <!-- 结算栏 -->
          <div class="cart-footer">
            <div class="footer-left">
              <el-button @click="cartStore.clearCart()">清空购物车</el-button>
              <NuxtLink to="/products" class="btn btn-outline">继续购物</NuxtLink>
            </div>
            <div class="footer-right">
              <div class="order-summary">
                <div class="summary-row">
                  <span>商品总额：</span>
                  <span class="amount">¥{{ cartStore.totalPrice.toFixed(2) }}</span>
                </div>
                <div class="summary-row">
                  <span>优惠：</span>
                  <span class="amount discount">-¥0.00</span>
                </div>
                <div class="summary-row total">
                  <span>应付总额：</span>
                  <span class="amount">¥{{ cartStore.totalPrice.toFixed(2) }}</span>
                </div>
              </div>
              <el-button type="primary" size="large" @click="goToCheckout">去结算</el-button>
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
import { useCartStore } from '~/stores/cart'
import type { CartItem } from '~/utils/api'

const cartStore = useCartStore()
const router = useRouter()

onMounted(() => {
  cartStore.loadCart()
})

async function updateQuantity(item: CartItem) {
  await cartStore.updateQuantity(item.id, item.quantity)
}

async function removeItem(itemId: string) {
  await cartStore.removeFromCart(itemId)
}

function goToCheckout() {
  router.push('/checkout')
}

// SEO
useHead({
  title: '购物车 - 元器件商城'
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

.page-title {
  font-size: 28px;
  color: #333;
  margin-bottom: 25px;
}

.loading {
  text-align: center;
  padding: 60px 0;
}

.empty-cart {
  text-align: center;
  padding: 60px 0;
}

/* 购物车表格 */
.cart-content {
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.cart-table {
  border: 1px solid #eee;
}

.cart-header {
  background: #f5f7fa;
  border-bottom: 1px solid #eee;
}

.header-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1.5fr 1fr 100px;
  padding: 15px 20px;
  font-weight: 600;
  color: #333;
}

.col-product { text-align: left; }
.col-price, .col-quantity, .col-subtotal { text-align: center; }
.col-action { text-align: right; }

.cart-body {
  background: white;
}

.cart-item {
  display: grid;
  grid-template-columns: 2fr 1fr 1.5fr 1fr 100px;
  padding: 20px;
  border-bottom: 1px solid #eee;
  align-items: center;
}

.cart-item:last-child {
  border-bottom: none;
}

.item-product {
  display: flex;
  gap: 15px;
}

.product-image {
  width: 80px;
  height: 80px;
  background: #f5f7fa;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.image-placeholder {
  color: #999;
  font-size: 12px;
}

.product-info {
  flex: 1;
}

.product-name {
  font-size: 15px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.product-desc {
  font-size: 13px;
  color: #666;
  margin-bottom: 5px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-mpn {
  font-size: 12px;
  color: #999;
}

.item-price {
  text-align: center;
  font-size: 16px;
  color: #333;
}

.item-quantity {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.stock-tip {
  font-size: 12px;
  color: #999;
}

.item-subtotal {
  text-align: center;
  font-size: 18px;
  color: #f56c6c;
  font-weight: 600;
}

.item-action {
  text-align: right;
}

/* 结算栏 */
.cart-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: #f5f7fa;
  border-top: 1px solid #eee;
}

.footer-left {
  display: flex;
  gap: 15px;
}

.footer-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 15px;
}

.order-summary {
  background: white;
  padding: 15px 25px;
  border-radius: 4px;
  min-width: 250px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  font-size: 14px;
}

.summary-row .amount {
  font-weight: 600;
}

.summary-row .discount {
  color: #f56c6c;
}

.summary-row.total {
  border-top: 1px solid #eee;
  padding-top: 10px;
  margin-bottom: 0;
  font-size: 16px;
}

.summary-row.total .amount {
  font-size: 20px;
  color: #f56c6c;
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

.footer-section h4 {
  font-size: 18px;
  margin-bottom: 15px;
}

.footer-bottom {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}
</style>
