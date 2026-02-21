<template>
  <div class="home-page">
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

    <!-- Hero 区域 -->
    <section class="hero-section">
      <div class="container">
        <div class="hero-content">
          <h1 class="hero-title">专业的电子元器件供应商</h1>
          <p class="hero-subtitle">提供 IC 芯片、传感器、连接器等电子产品，一站式采购解决方案</p>

          <!-- 搜索框 -->
          <div class="search-box">
            <input
              v-model="searchKeyword"
              type="text"
              placeholder="输入型号或关键词搜索..."
              @keyup.enter="handleSearch"
            />
            <button class="search-btn" @click="handleSearch">搜索</button>
          </div>

          <div class="hero-stats">
            <div class="stat-item">
              <span class="stat-value">10,000+</span>
              <span class="stat-label">产品型号</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">5,000+</span>
              <span class="stat-label">合作客户</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">99%</span>
              <span class="stat-label">客户满意度</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 产品分类 -->
    <section class="category-section">
      <div class="container">
        <h2 class="section-title">产品分类</h2>
        <div class="category-grid">
          <div
            v-for="category in categories"
            :key="category.id"
            class="category-card"
            @click="goToCategory(category.id)"
          >
            <div class="category-icon">{{ category.icon }}</div>
            <h3 class="category-name">{{ category.name }}</h3>
            <p class="category-count">{{ category.count }}+ 产品</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 热门产品 -->
    <section class="product-section">
      <div class="container">
        <h2 class="section-title">热门产品</h2>
        <div class="product-grid">
          <div
            v-for="product in hotProducts"
            :key="product.id"
            class="product-card"
            @click="goToProduct(product.id)"
          >
            <div class="product-image">
              <LazyImage
                v-if="product.image_url"
                :src="product.image_url"
                :alt="product.mpn"
                height="200"
              />
              <span v-else class="image-placeholder">产品图片</span>
            </div>
            <div class="product-info">
              <h3 class="product-name">{{ product.mpn }}</h3>
              <p class="product-desc">{{ product.description }}</p>
              <div class="product-meta">
                <span class="product-price">¥{{ product.price.toFixed(2) }}</span>
                <span class="product-stock">库存：{{ product.stock }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 底部 -->
    <footer class="site-footer">
      <div class="container">
        <div class="footer-content">
          <div class="footer-section">
            <h4>关于我们</h4>
            <p>专业的电子元器件供应商，致力于为客户提供优质的产品和服</p>
          </div>
          <div class="footer-section">
            <h4>快速链接</h4>
            <ul>
              <li><NuxtLink to="/products">产品中心</NuxtLink></li>
              <li><NuxtLink to="/about">关于我们</NuxtLink></li>
              <li><NuxtLink to="/contact">联系我们</NuxtLink></li>
            </ul>
          </div>
          <div class="footer-section">
            <h4>联系方式</h4>
            <p>电话：400-xxx-xxxx</p>
            <p>邮箱：info@example.com</p>
            <p>地址：某某省某某市某某区</p>
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
import { api, type Product } from '~/utils/api'

const router = useRouter()
const searchKeyword = ref('')

// 分类数据
const categories = ref([
  { id: 'mcu', name: 'MCU/处理器', icon: '🔧', count: 2000 },
  { id: 'memory', name: '存储器', icon: '💾', count: 1500 },
  { id: 'sensor', name: '传感器', icon: '📡', count: 1000 },
  { id: 'power', name: '电源管理', icon: '⚡', count: 800 },
  { id: 'analog', name: '模拟器件', icon: '📊', count: 1200 },
  { id: 'wireless', name: '无线模块', icon: '📶', count: 600 }
])

// 热门产品数据
const hotProducts = ref<Product[]>([])

// 加载热门产品
async function loadHotProducts() {
  try {
    const response = await api.getProducts({
      page: 1,
      page_size: 8
    })
    hotProducts.value = response.data.products
  } catch (e) {
    console.error('加载热门产品失败:', e)
  }
}

function handleSearch() {
  if (searchKeyword.value.trim()) {
    router.push(`/products?keyword=${encodeURIComponent(searchKeyword.value)}`)
  }
}

function goToCategory(categoryId: string) {
  router.push(`/products?category=${categoryId}`)
}

function goToProduct(id: string) {
  router.push(`/product/${id}`)
}

onMounted(() => {
  loadHotProducts()
})

// SEO
useHead({
  title: '首页 - 元器件商城',
  meta: [
    { name: 'description', content: '专业的电子元器件供应商，提供 IC 芯片、传感器、连接器等电子产品' }
  ]
})
</script>

<style scoped>
/* 基础样式 */
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

.main-nav a:hover {
  color: #409eff;
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

/* Hero 区域 */
.hero-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 80px 0;
  text-align: center;
}

.hero-title {
  font-size: 48px;
  margin-bottom: 20px;
}

.hero-subtitle {
  font-size: 20px;
  margin-bottom: 40px;
  opacity: 0.9;
}

.search-box {
  display: flex;
  max-width: 600px;
  margin: 0 auto 40px;
}

.search-box input {
  flex: 1;
  padding: 15px 20px;
  border: none;
  border-radius: 4px 0 0 4px;
  font-size: 16px;
}

.search-btn {
  padding: 15px 30px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 0 4px 4px 0;
  font-size: 16px;
  cursor: pointer;
}

.search-btn:hover {
  background: #66b1ff;
}

.hero-stats {
  display: flex;
  justify-content: center;
  gap: 60px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 36px;
  font-weight: bold;
}

.stat-label {
  font-size: 14px;
  opacity: 0.8;
}

/* 分类区域 */
.category-section {
  padding: 60px 0;
  background: #f5f7fa;
}

.section-title {
  text-align: center;
  font-size: 32px;
  margin-bottom: 40px;
  color: #333;
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 20px;
}

.category-card {
  background: white;
  padding: 30px;
  border-radius: 8px;
  text-align: center;
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
}

.category-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.category-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

.category-name {
  font-size: 18px;
  color: #333;
  margin-bottom: 8px;
}

.category-count {
  font-size: 14px;
  color: #999;
}

/* 产品区域 */
.product-section {
  padding: 60px 0;
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 25px;
}

.product-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s, box-shadow 0.3s;
  cursor: pointer;
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
}

.product-image {
  height: 200px;
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-placeholder {
  color: #999;
  font-size: 14px;
}

.product-info {
  padding: 20px;
}

.product-name {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.product-desc {
  font-size: 14px;
  color: #666;
  margin-bottom: 15px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.product-price {
  font-size: 20px;
  color: #f56c6c;
  font-weight: 600;
}

.product-stock {
  font-size: 14px;
  color: #999;
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

.footer-section p {
  font-size: 14px;
  line-height: 1.8;
  opacity: 0.8;
}

.footer-section ul {
  list-style: none;
  padding: 0;
}

.footer-section ul li {
  margin-bottom: 10px;
}

.footer-section a {
  color: white;
  text-decoration: none;
  opacity: 0.8;
}

.footer-section a:hover {
  opacity: 1;
}

.footer-bottom {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.footer-bottom p {
  font-size: 14px;
  opacity: 0.6;
}
</style>
