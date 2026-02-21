<template>
  <div class="products-page">
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
        <div class="page-layout">
          <!-- 侧边栏过滤 -->
          <aside class="sidebar">
            <div class="filter-section">
              <h3>产品分类</h3>
              <ul class="category-list">
                <li
                  v-for="cat in categories"
                  :key="cat.id"
                  :class="{ active: selectedCategory === cat.id }"
                  @click="selectCategory(cat.id)"
                >
                  {{ cat.name }} ({{ cat.count }})
                </li>
              </ul>
            </div>

            <div class="filter-section">
              <h3>价格区间</h3>
              <div class="price-range">
                <input v-model="priceMin" type="number" placeholder="最低" />
                <span>-</span>
                <input v-model="priceMax" type="number" placeholder="最高" />
              </div>
            </div>

            <div class="filter-section">
              <h3>品牌</h3>
              <div class="brand-list">
                <label v-for="brand in brands" :key="brand">
                  <input type="checkbox" :value="brand" v-model="selectedBrands" />
                  {{ brand }}
                </label>
              </div>
            </div>

            <button class="btn-apply" @click="applyFilters">应用筛选</button>
          </aside>

          <!-- 产品列表 -->
          <div class="product-list-section">
            <div class="list-header">
              <div class="search-box">
                <input
                  v-model="keyword"
                  type="text"
                  placeholder="搜索产品型号..."
                  @keyup.enter="handleSearch"
                />
                <button @click="handleSearch">搜索</button>
              </div>
              <div class="sort-options">
                <select v-model="sortBy" @change="handleSort">
                  <option value="default">默认排序</option>
                  <option value="price_asc">价格从低到高</option>
                  <option value="price_desc">价格从高到低</option>
                  <option value="stock">库存优先</option>
                </select>
              </div>
            </div>

            <div class="product-grid">
              <div
                v-for="product in filteredProducts"
                :key="product.id"
                class="product-card"
                @click="goToProduct(product.id)"
              >
                <div class="product-image">
                  <LazyImage
                    v-if="product.image_url"
                    :src="product.image_url"
                    :alt="product.mpn"
                    height="180"
                  />
                  <span v-else class="image-placeholder">产品图片</span>
                </div>
                <div class="product-info">
                  <h3 class="product-name">{{ product.mpn }}</h3>
                  <p class="product-desc">{{ product.description }}</p>
                  <p class="product-manufacturer">厂商：{{ product.manufacturer }}</p>
                  <div class="product-meta">
                    <span class="product-price">¥{{ product.price }}</span>
                    <span class="product-stock">库存：{{ product.stock }}</span>
                  </div>
                  <button class="btn-cart" :disabled="product.stock === 0" @click.stop="addToCart(product)">
                    {{ product.stock === 0 ? '缺货' : '加入购物车' }}
                  </button>
                </div>
              </div>
            </div>

            <!-- 分页 -->
            <div class="pagination" v-if="totalPages > 1">
              <button
                :disabled="currentPage === 1"
                @click="changePage(currentPage - 1)"
              >
                上一页
              </button>
              <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
              <button
                :disabled="currentPage === totalPages"
                @click="changePage(currentPage + 1)"
              >
                下一页
              </button>
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
import { api, type Product } from '~/utils/api'
import { useCartStore } from '~/stores/cart'

const route = useRoute()
const router = useRouter()
const cartStore = useCartStore()

// 分类数据
const categories = ref([
  { id: 'mcu', name: 'MCU/处理器', count: 2000 },
  { id: 'memory', name: '存储器', count: 1500 },
  { id: 'sensor', name: '传感器', count: 1000 },
  { id: 'power', name: '电源管理', count: 800 },
  { id: 'analog', name: '模拟器件', count: 1200 },
  { id: 'wireless', name: '无线模块', count: 600 }
])

// 品牌数据
const brands = ['STMicroelectronics', 'Texas Instruments', 'NXP', 'Infineon', 'Microchip', 'Espressif']

// 筛选状态
const selectedCategory = ref<string>('')
const selectedBrands = ref<string[]>([])
const priceMin = ref<string>('')
const priceMax = ref<string>('')
const keyword = ref('')
const sortBy = ref('default')

// 分页
const currentPage = ref(1)
const totalPages = ref(10)

// 产品数据
const allProducts = ref<Product[]>([])

// 计算属性：筛选后的产品
const filteredProducts = computed(() => {
  let result = [...allProducts.value]

  // 按分类筛选
  if (selectedCategory.value) {
    result = result.filter(p => p.category === selectedCategory.value)
  }

  // 按品牌筛选
  if (selectedBrands.value.length > 0) {
    result = result.filter(p =>
      selectedBrands.value.some(b => p.manufacturer.toLowerCase().includes(b.toLowerCase()))
    )
  }

  // 按价格筛选
  if (priceMin.value) {
    result = result.filter(p => p.price >= parseFloat(priceMin.value))
  }
  if (priceMax.value) {
    result = result.filter(p => p.price <= parseFloat(priceMax.value))
  }

  // 按关键词搜索
  if (keyword.value) {
    const kw = keyword.value.toLowerCase()
    result = result.filter(p =>
      p.mpn.toLowerCase().includes(kw) ||
      p.description.toLowerCase().includes(kw) ||
      p.manufacturer.toLowerCase().includes(kw)
    )
  }

  // 排序
  switch (sortBy.value) {
    case 'price_asc':
      result.sort((a, b) => a.price - b.price)
      break
    case 'price_desc':
      result.sort((a, b) => b.price - a.price)
      break
    case 'stock':
      result.sort((a, b) => b.stock - a.stock)
      break
  }

  return result
})

function selectCategory(id: string) {
  selectedCategory.value = selectedCategory.value === id ? '' : id
}

function applyFilters() {
  currentPage.value = 1
  // TODO: 调用 API 获取筛选后的产品
}

function handleSearch() {
  currentPage.value = 1
  // TODO: 调用 API 搜索产品
}

function handleSort() {
  // 排序已在计算属性中处理
}

function changePage(page: number) {
  currentPage.value = page
  // TODO: 调用 API 获取对应页数据
}

// 跳转到产品详情
function goToProduct(id: string) {
  router.push(`/product/${id}`)
}

// 加入购物车
async function addToCart(product: Product) {
  if (product.stock === 0) return
  try {
    await cartStore.addItem(product.id, 1)
    alert('已成功添加到购物车')
  } catch (e) {
    console.error('添加到购物车失败:', e)
    alert('添加到购物车失败，请稍后重试')
  }
}

// 加载产品数据
async function loadProducts() {
  try {
    const response = await api.getProducts({
      page: 1,
      page_size: 20
    })
    allProducts.value = response.data.products
    totalPages.value = Math.ceil(response.data.total / response.data.page_size)
  } catch (e) {
    console.error('加载产品失败:', e)
  }
}

// 生命周期
onMounted(() => {
  loadProducts()
})

// SEO
useHead({
  title: '产品中心 - 元器件商城',
  meta: [
    { name: 'description', content: '浏览我们的产品中心，找到您需要的电子元器件' }
  ]
})
</script>

<style scoped>
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* 顶部导航（复用首页样式） */
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

.page-layout {
  display: grid;
  grid-template-columns: 250px 1fr;
  gap: 25px;
}

/* 侧边栏 */
.sidebar {
  background: white;
  padding: 20px;
  border-radius: 8px;
  height: fit-content;
}

.filter-section {
  margin-bottom: 25px;
}

.filter-section h3 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 15px;
  color: #333;
}

.category-list {
  list-style: none;
  padding: 0;
}

.category-list li {
  padding: 10px;
  cursor: pointer;
  border-radius: 4px;
  transition: background 0.2s;
}

.category-list li:hover {
  background: #f5f7fa;
}

.category-list li.active {
  background: #ecf5ff;
  color: #409eff;
}

.price-range {
  display: flex;
  align-items: center;
  gap: 10px;
}

.price-range input {
  flex: 1;
  padding: 8px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
}

.brand-list label {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  cursor: pointer;
}

.btn-apply {
  width: 100%;
  padding: 12px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
}

.btn-apply:hover {
  background: #66b1ff;
}

/* 产品列表区 */
.product-list-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  gap: 20px;
}

.search-box {
  display: flex;
  flex: 1;
  max-width: 400px;
}

.search-box input {
  flex: 1;
  padding: 10px 15px;
  border: 1px solid #dcdfe6;
  border-radius: 4px 0 0 4px;
  font-size: 14px;
}

.search-box button {
  padding: 10px 20px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
}

.sort-options select {
  padding: 10px 15px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
}

/* 产品网格 */
.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
}

.product-card {
  border: 1px solid #eee;
  border-radius: 8px;
  overflow: hidden;
  transition: box-shadow 0.3s, transform 0.2s;
  cursor: pointer;
}

.product-card:hover {
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.product-image {
  height: 180px;
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-placeholder {
  color: #999;
}

.product-info {
  padding: 15px;
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
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-manufacturer {
  font-size: 13px;
  color: #999;
  margin-bottom: 12px;
}

.product-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.product-price {
  font-size: 18px;
  color: #f56c6c;
  font-weight: 600;
}

.product-stock {
  font-size: 13px;
  color: #999;
}

.btn-cart {
  width: 100%;
  padding: 10px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
}

.btn-cart:hover {
  background: #66b1ff;
}

.btn-cart:disabled {
  background: #dcdfe6;
  cursor: not-allowed;
}

/* 分页 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.pagination button {
  padding: 8px 20px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.pagination button:disabled {
  background: #dcdfe6;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: #666;
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
