<template>
  <div class="product-detail-page">
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
          <NuxtLink to="/cart" class="cart-link">
            <span class="cart-icon">🛒</span>
            <span class="cart-count" v-if="cartCount > 0">{{ cartCount }}</span>
          </NuxtLink>
          <NuxtLink v-if="isLoggedIn" to="/profile" class="btn btn-outline">个人中心</NuxtLink>
          <NuxtLink v-else to="/login" class="btn btn-outline">登录</NuxtLink>
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
          <NuxtLink to="/products">产品中心</NuxtLink>
          <span class="separator">/</span>
          <span class="current">{{ product?.mpn || '产品详情' }}</span>
        </div>

        <!-- 加载状态 -->
        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <p>加载中...</p>
        </div>

        <!-- 错误状态 -->
        <div v-else-if="error" class="error-state">
          <p>{{ error }}</p>
          <button @click="fetchProduct">重试</button>
        </div>

        <!-- 产品详情 -->
        <div v-else-if="product" class="product-detail">
          <div class="product-main">
            <!-- 左侧：图片 -->
            <div class="product-gallery">
              <div class="main-image">
                <LazyImage
                  v-if="product.image_url"
                  :src="product.image_url"
                  :alt="product.mpn"
                  height="400"
                />
                <div v-else class="image-placeholder">
                  <span>产品图片</span>
                </div>
              </div>
              <div class="thumbnail-list">
                <div class="thumbnail active">
                  <LazyImage
                    v-if="product.image_url"
                    :src="product.image_url"
                    :alt="product.mpn"
                    height="80"
                  />
                  <span v-else>主图</span>
                </div>
              </div>
            </div>

            <!-- 右侧：信息 -->
            <div class="product-info">
              <h1 class="product-title">{{ product.mpn }}</h1>
              <p class="product-description">{{ product.description }}</p>

              <div class="product-meta">
                <div class="meta-item">
                  <span class="label">制造商</span>
                  <span class="value">{{ product.manufacturer }}</span>
                </div>
                <div class="meta-item">
                  <span class="label">分类</span>
                  <span class="value">{{ getCategoryName(product.category) }}</span>
                </div>
                <div class="meta-item">
                  <span class="label">封装</span>
                  <span class="value">{{ product.package }}</span>
                </div>
              </div>

              <div class="price-stock">
                <div class="price">
                  <span class="price-label">单价</span>
                  <span class="price-value">¥{{ product.price.toFixed(2) }}</span>
                  <span class="price-unit">/ 件</span>
                </div>
                <div class="stock" :class="{ 'out-of-stock': product.stock === 0 }">
                  <span class="stock-label">库存</span>
                  <span class="stock-value">{{ product.stock }}</span>
                  <span class="stock-unit">件</span>
                  <span v-if="product.stock === 0" class="out-of-stock-tag">缺货</span>
                  <span v-else-if="product.stock < 100" class="low-stock-tag">库存紧张</span>
                </div>
              </div>

              <div class="quantity-selector">
                <span class="quantity-label">数量</span>
                <div class="quantity-control">
                  <button @click="decreaseQuantity" :disabled="quantity <= 1">-</button>
                  <input
                    type="number"
                    v-model.number="quantity"
                    :min="1"
                    :max="product.stock"
                  />
                  <button @click="increaseQuantity" :disabled="quantity >= product.stock">+</button>
                </div>
                <span class="quantity-max">最大可购买：{{ product.stock }} 件</span>
              </div>

              <div class="action-buttons">
                <button
                  class="btn-add-to-cart"
                  @click="addToCart"
                  :disabled="product.stock === 0 || addingToCart"
                >
                  <span v-if="addingToCart">添加中...</span>
                  <span v-else>加入购物车</span>
                </button>
                <button class="btn-buy-now" @click="buyNow" :disabled="product.stock === 0">
                  立即购买
                </button>
              </div>

              <div class="product-services">
                <div class="service-item">
                  <span class="service-icon">✓</span>
                  <span class="service-text">正品保证</span>
                </div>
                <div class="service-item">
                  <span class="service-icon">✓</span>
                  <span class="service-text">7 天无理由退换</span>
                </div>
                <div class="service-item">
                  <span class="service-icon">✓</span>
                  <span class="service-text">极速发货</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 产品规格 -->
          <div class="product-specifications">
            <h2 class="section-title">产品规格</h2>
            <table class="spec-table">
              <tbody>
                <tr>
                  <td class="spec-label">产品型号</td>
                  <td class="spec-value">{{ product.mpn }}</td>
                </tr>
                <tr>
                  <td class="spec-label">制造商</td>
                  <td class="spec-value">{{ product.manufacturer }}</td>
                </tr>
                <tr>
                  <td class="spec-label">描述</td>
                  <td class="spec-value">{{ product.description }}</td>
                </tr>
                <tr>
                  <td class="spec-label">分类</td>
                  <td class="spec-value">{{ getCategoryName(product.category) }}</td>
                </tr>
                <tr>
                  <td class="spec-label">封装</td>
                  <td class="spec-value">{{ product.package }}</td>
                </tr>
                <tr>
                  <td class="spec-label">价格</td>
                  <td class="spec-value">¥{{ product.price.toFixed(2) }}</td>
                </tr>
                <tr>
                  <td class="spec-label">库存</td>
                  <td class="spec-value">{{ product.stock }} 件</td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Datasheet 下载 -->
          <div v-if="product.datasheet_url" class="datasheet-section">
            <h2 class="section-title">技术文档</h2>
            <div class="datasheet-content">
              <a :href="product.datasheet_url" target="_blank" class="datasheet-link">
                <span class="datasheet-icon">📄</span>
                <span class="datasheet-text">下载 Datasheet (PDF)</span>
              </a>
            </div>
          </div>

          <!-- 相关产品 -->
          <div class="related-products">
            <h2 class="section-title">相关产品</h2>
            <div class="related-grid">
              <div
                v-for="item in relatedProducts"
                :key="item.id"
                class="related-card"
                @click="goToProduct(item.id)"
              >
                <div class="related-image">
                  <LazyImage
                    v-if="item.image_url"
                    :src="item.image_url"
                    :alt="item.mpn"
                    height="120"
                  />
                  <span v-else>图片</span>
                </div>
                <div class="related-info">
                  <h3 class="related-name">{{ item.mpn }}</h3>
                  <p class="related-desc">{{ item.description }}</p>
                  <div class="related-meta">
                    <span class="related-price">¥{{ item.price.toFixed(2) }}</span>
                    <span class="related-stock">库存：{{ item.stock }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 商品评价 -->
          <div class="product-reviews">
            <h2 class="section-title">商品评价</h2>
            <ReviewList :productId="product?.id" />
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
import type { Product } from '~/utils/api'
import { api } from '~/utils/api'
import { useCartStore } from '~/stores/cart'
import ReviewList from '~/components/ReviewList.vue'

const route = useRoute()
const router = useRouter()
const cartStore = useCartStore()

// 状态
const product = ref<Product | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)
const quantity = ref(1)
const addingToCart = ref(false)
const relatedProducts = ref<Product[]>([])

// 计算属性
const isLoggedIn = computed(() => !!localStorage.getItem('access_token'))
const cartCount = computed(() => cartStore.count)

// 分类名称映射
const categoryMap: Record<string, string> = {
  'mcu': 'MCU/处理器',
  'memory': '存储器',
  'sensor': '传感器',
  'power': '电源管理',
  'analog': '模拟器件',
  'wireless': '无线模块'
}

function getCategoryName(category: string): string {
  return categoryMap[category] || category
}

// 获取产品详情
async function fetchProduct() {
  loading.value = true
  error.value = null

  try {
    const productId = route.params.id as string
    const response = await api.getProduct(productId)
    product.value = response.data

    // 获取相关产品
    await fetchRelatedProducts(product.value.category, product.value.id)
  } catch (e) {
    console.error('获取产品详情失败:', e)
    error.value = '获取产品详情失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

// 获取相关产品
async function fetchRelatedProducts(category: string, excludeId: string) {
  try {
    const response = await api.getProducts({
      category,
      page: 1,
      page_size: 4
    })
    relatedProducts.value = response.data.products.filter(p => p.id !== excludeId)
  } catch (e) {
    console.error('获取相关产品失败:', e)
    relatedProducts.value = []
  }
}

// 数量控制
function increaseQuantity() {
  if (product.value && quantity.value < product.value.stock) {
    quantity.value++
  }
}

function decreaseQuantity() {
  if (quantity.value > 1) {
    quantity.value--
  }
}

// 加入购物车
async function addToCart() {
  if (!product.value) return

  addingToCart.value = true

  try {
    await cartStore.addItem(product.value.id, quantity.value)
    // 显示成功提示
    alert('已成功添加到购物车')
  } catch (e) {
    console.error('添加到购物车失败:', e)
    alert('添加到购物车失败，请稍后重试')
  } finally {
    addingToCart.value = false
  }
}

// 立即购买
function buyNow() {
  if (!product.value || product.value.stock === 0) return

  // 先添加到购物车，然后跳转到购物车页面
  addToCart().then(() => {
    router.push('/cart')
  })
}

// 跳转到产品详情
function goToProduct(id: string) {
  router.push(`/product/${id}`)
  // 滚动到顶部
  window.scrollTo(0, 0)
  // 重新加载产品详情
  fetchProduct()
}

// 监听路由变化
watch(() => route.params.id, () => {
  fetchProduct()
})

// 生命周期
onMounted(() => {
  fetchProduct()
})

// SEO
const productName = computed(() => product.value?.mpn || '产品详情')
useHead({
  title: () => `${productName.value} - 元器件商城`,
  meta: [
    { name: 'description', content: product.value?.description || '' }
  ]
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
  border: none;
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

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #eee;
  border-top-color: #409eff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-state p {
  color: #f56c6c;
  margin-bottom: 20px;
}

.error-state button {
  padding: 10px 30px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

/* 产品详情 */
.product-detail {
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.product-main {
  display: grid;
  grid-template-columns: 450px 1fr;
  gap: 40px;
  padding: 30px;
  border-bottom: 1px solid #eee;
}

/* 产品图片 */
.product-gallery {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.main-image {
  width: 100%;
  height: 400px;
  background: #f5f7fa;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.main-image :deep(img) {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.image-placeholder {
  color: #999;
  font-size: 16px;
}

.thumbnail-list {
  display: flex;
  gap: 10px;
}

.thumbnail {
  width: 80px;
  height: 80px;
  background: #f5f7fa;
  border: 2px solid transparent;
  border-radius: 4px;
  overflow: hidden;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.thumbnail.active {
  border-color: #409eff;
}

.thumbnail :deep(img) {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

/* 产品信息 */
.product-info {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.product-title {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.product-description {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  margin: 0;
}

.product-meta {
  display: flex;
  gap: 30px;
  padding: 15px 0;
  border-top: 1px solid #eee;
  border-bottom: 1px solid #eee;
}

.meta-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.meta-item .label {
  font-size: 12px;
  color: #999;
}

.meta-item .value {
  font-size: 14px;
  color: #333;
}

.price-stock {
  display: flex;
  gap: 40px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.price {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.price-label {
  font-size: 14px;
  color: #999;
}

.price-value {
  font-size: 32px;
  color: #f56c6c;
  font-weight: 600;
}

.price-unit {
  font-size: 14px;
  color: #999;
}

.stock {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.stock-label {
  font-size: 14px;
  color: #999;
}

.stock-value {
  font-size: 20px;
  color: #67c23a;
  font-weight: 600;
}

.stock-unit {
  font-size: 14px;
  color: #999;
}

.out-of-stock .stock-value {
  color: #999;
}

.out-of-stock-tag {
  background: #f56c6c;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.low-stock-tag {
  background: #e6a23c;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.quantity-selector {
  display: flex;
  align-items: center;
  gap: 15px;
}

.quantity-label {
  font-size: 14px;
  color: #333;
}

.quantity-control {
  display: flex;
  align-items: center;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
}

.quantity-control button {
  width: 40px;
  height: 40px;
  border: none;
  background: #f5f7fa;
  cursor: pointer;
  font-size: 18px;
}

.quantity-control button:hover:not(:disabled) {
  background: #ecf5ff;
}

.quantity-control button:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.quantity-control input {
  width: 60px;
  height: 38px;
  border: none;
  text-align: center;
  font-size: 14px;
}

.quantity-max {
  font-size: 12px;
  color: #999;
}

.action-buttons {
  display: flex;
  gap: 15px;
}

.btn-add-to-cart,
.btn-buy-now {
  flex: 1;
  padding: 15px;
  font-size: 16px;
  font-weight: 600;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-add-to-cart {
  background: #f56c6c;
  color: white;
}

.btn-add-to-cart:hover:not(:disabled) {
  background: #f78989;
}

.btn-buy-now {
  background: #409eff;
  color: white;
}

.btn-buy-now:hover:not(:disabled) {
  background: #66b1ff;
}

.btn-add-to-cart:disabled,
.btn-buy-now:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.product-services {
  display: flex;
  gap: 20px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.service-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #67c23a;
}

.service-icon {
  font-weight: bold;
}

/* 产品规格 */
.product-specifications {
  padding: 30px;
  border-bottom: 1px solid #eee;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 20px;
}

.spec-table {
  width: 100%;
  border-collapse: collapse;
}

.spec-table tr {
  border-bottom: 1px solid #eee;
}

.spec-table tr:last-child {
  border-bottom: none;
}

.spec-table td {
  padding: 12px 0;
}

.spec-label {
  width: 150px;
  font-weight: 500;
  color: #666;
}

.spec-value {
  color: #333;
}

/* Datasheet 下载 */
.datasheet-section {
  padding: 30px;
  border-bottom: 1px solid #eee;
}

.datasheet-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.datasheet-link {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 15px 25px;
  background: #ecf5ff;
  border-radius: 8px;
  text-decoration: none;
  color: #409eff;
  transition: background 0.2s;
}

.datasheet-link:hover {
  background: #d9ecff;
}

.datasheet-icon {
  font-size: 20px;
}

/* 相关产品 */
.related-products {
  padding: 30px;
}

.related-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
}

.related-card {
  border: 1px solid #eee;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: box-shadow 0.3s;
}

.related-card:hover {
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.related-image {
  height: 120px;
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
}

.related-image :deep(img) {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.related-info {
  padding: 15px;
}

.related-name {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.related-desc {
  font-size: 12px;
  color: #666;
  margin-bottom: 10px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.related-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.related-price {
  font-size: 16px;
  color: #f56c6c;
  font-weight: 600;
}

.related-stock {
  font-size: 12px;
  color: #999;
}

/* 商品评价 */
.product-reviews {
  padding: 30px;
  background: white;
  margin-top: 20px;
  border-radius: 8px;
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
