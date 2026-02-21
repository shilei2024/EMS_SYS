<template>
  <div class="review-list">
    <!-- 评价总览 -->
    <div v-if="showOverview" class="review-overview">
      <div class="overview-left">
        <div class="rating-average">
          <span class="rating-number">{{ averageRating.toFixed(1) }}</span>
          <el-rate
            v-model="averageRating"
            disabled
            :colors="['#99A9BF', '#F7BA2A', '#FF9900']"
          />
          <span class="rating-count">{{ reviews.length }} 条评价</span>
        </div>
        <div class="rating-distribution">
          <div
            v-for="star in [5, 4, 3, 2, 1]"
            :key="star"
            class="rating-row"
          >
            <span class="star-label">{{ star }}星</span>
            <el-progress
              :percentage="(getRatingCount(star) / reviews.length) * 100"
              :color="getRatingColor(star)"
              :stroke-width="6"
              :show-text="false"
            />
            <span class="star-count">{{ getRatingCount(star) }}</span>
          </div>
        </div>
      </div>
      <div class="overview-right">
        <div class="filter-tags">
          <el-tag
            v-for="tag in filterTags"
            :key="tag.key"
            :type="selectedTag === tag.key ? 'primary' : ''"
            effect="plain"
            @click="selectedTag = tag.key"
          >
            {{ tag.label }}
          </el-tag>
        </div>
      </div>
    </div>

    <!-- 评价列表 -->
    <div class="review-items">
      <div
        v-for="review in filteredReviews"
        :key="review.id"
        class="review-item"
      >
        <div class="review-header">
          <div class="user-info">
            <div class="user-avatar">
              <el-avatar :size="40" :src="review.user?.avatar">
                <span>{{ review.user?.username?.charAt(0) || 'U' }}</span>
              </el-avatar>
            </div>
            <div class="user-detail">
              <span class="username">{{ review.user?.username || '匿名用户' }}</span>
              <span class="purchase-info">
                购买型号：{{ review.product?.mpn || review.product_name }}
              </span>
            </div>
          </div>
          <div class="review-meta">
            <el-rate
              v-model="review.rating"
              disabled
              :colors="['#99A9BF', '#F7BA2A', '#FF9900']"
            />
            <span class="review-time">{{ formatDate(review.created_at) }}</span>
          </div>
        </div>

        <div class="review-content">
          <p class="review-text">{{ review.comment }}</p>

          <!-- 评价图片 -->
          <div v-if="review.images && review.images.length > 0" class="review-images">
            <div
              v-for="(img, index) in review.images"
              :key="index"
              class="review-image"
              @click="previewImage(img)"
            >
              <el-image
                :src="img"
                fit="cover"
                class="image-thumb"
              />
            </div>
          </div>

          <!-- 商家回复 -->
          <div v-if="review.reply" class="seller-reply">
            <div class="reply-header">
              <el-icon><ChatDotRound /></el-icon>
              <span>商家回复</span>
            </div>
            <p class="reply-text">{{ review.reply }}</p>
          </div>
        </div>

        <!-- 评价操作 -->
        <div class="review-actions">
          <el-button link type="primary" @click="toggleHelpful(review.id)">
            <el-icon><ThumbUp /></el-icon>
            有用 ({{ review.helpful_count || 0 }})
          </el-button>
          <el-button link @click="reportReview(review.id)">
            <el-icon><WarningFilled /></el-icon>
            举报
          </el-button>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <el-empty v-if="filteredReviews.length === 0" description="暂无评价" />

    <!-- 图片预览 -->
    <el-image-viewer
      v-if="previewVisible"
      :url-list="[previewUrl]"
      @close="previewVisible = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ChatDotRound, ThumbUp, WarningFilled } from '@element-plus/icons-vue'

interface Review {
  id: string
  order_id: string
  product_id: string
  product_name: string
  product?: any
  user?: any
  rating: number
  comment: string
  images?: string[]
  reply?: string
  helpful_count?: number
  created_at: string
}

const props = defineProps({
  productId: {
    type: String,
    default: ''
  },
  orderId: {
    type: String,
    default: ''
  },
  showOverview: {
    type: Boolean,
    default: true
  }
})

// 状态
const reviews = ref<Review[]>([])
const averageRating = ref(0)
const selectedTag = ref('')
const previewVisible = ref(false)
const previewUrl = ref('')

// 筛选标签
const filterTags = [
  { key: '', label: '全部' },
  { key: 'with_image', label: '有图' },
  { key: '5', label: '好评' },
  { key: '3', label: '中评' },
  { key: '1', label: '差评' }
]

// 计算属性
const filteredReviews = computed(() => {
  let result = [...reviews.value]

  if (selectedTag.value === 'with_image') {
    result = result.filter(r => r.images && r.images.length > 0)
  } else if (selectedTag.value) {
    const rating = parseInt(selectedTag.value)
    result = result.filter(r => {
      if (rating === 5) return r.rating >= 4
      if (rating === 3) return r.rating === 3
      if (rating === 1) return r.rating <= 2
      return true
    })
  }

  return result
})

// 方法
function getRatingCount(star: number): number {
  if (star === 5) return reviews.value.filter(r => r.rating >= 4).length
  if (star === 1) return reviews.value.filter(r => r.rating <= 2).length
  return reviews.value.filter(r => r.rating === star).length
}

function getRatingColor(star: number): string {
  const colors: Record<number, string> = {
    5: '#67c23a',
    4: '#67c23a',
    3: '#e6a23c',
    2: '#f56c6c',
    1: '#f56c6c'
  }
  return colors[star]
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleString('zh-CN')
}

function toggleHelpful(reviewId: string) {
  const review = reviews.value.find(r => r.id === reviewId)
  if (review) {
    review.helpful_count = (review.helpful_count || 0) + 1
  }
}

function reportReview(reviewId: string) {
  alert('举报已提交，我们会尽快处理')
}

function previewImage(url: string) {
  previewUrl.value = url
  previewVisible.value = true
}

// 加载评价
async function loadReviews() {
  try {
    // TODO: 调用评价 API
    // 使用模拟数据
    reviews.value = [
      {
        id: '1',
        order_id: '1',
        product_id: '1',
        product_name: 'STM32F407VGT6',
        product: { mpn: 'STM32F407VGT6' },
        user: { username: '张***3', avatar: '' },
        rating: 5,
        comment: '质量很好，是正品，物流也很快，好评！',
        images: [],
        reply: '感谢您的好评，祝您生活愉快！',
        helpful_count: 12,
        created_at: new Date(Date.now() - 86400000 * 5).toISOString()
      },
      {
        id: '2',
        order_id: '2',
        product_id: '2',
        product_name: 'ESP32-WROOM-32',
        product: { mpn: 'ESP32-WROOM-32' },
        user: { username: '李***8', avatar: '' },
        rating: 5,
        comment: '多次购买了，质量稳定，价格实惠，会继续支持',
        images: ['https://via.placeholder.com/200'],
        reply: '',
        helpful_count: 8,
        created_at: new Date(Date.now() - 86400000 * 10).toISOString()
      },
      {
        id: '3',
        order_id: '3',
        product_id: '3',
        product_name: 'ATMEGA328P-PU',
        product: { mpn: 'ATMEGA328P-PU' },
        user: { username: '王***5', avatar: '' },
        rating: 4,
        comment: '整体不错，就是物流有点慢',
        images: [],
        reply: '抱歉物流给您带来不便，我们会督促物流改进',
        helpful_count: 3,
        created_at: new Date(Date.now() - 86400000 * 15).toISOString()
      }
    ]

    // 计算平均评分
    if (reviews.value.length > 0) {
      averageRating.value = reviews.value.reduce((sum, r) => sum + r.rating, 0) / reviews.value.length
    }
  } catch (error: any) {
    console.error('加载评价失败:', error)
  }
}

onMounted(() => {
  loadReviews()
})

// 暴露方法供外部调用
defineExpose({
  loadReviews
})
</script>

<style scoped>
.review-list {
  background: white;
  border-radius: 8px;
  padding: 20px;
}

/* 评价总览 */
.review-overview {
  display: flex;
  gap: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
  margin-bottom: 20px;
}

.overview-left {
  width: 300px;
}

.rating-average {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.rating-number {
  font-size: 48px;
  font-weight: 700;
  color: #f56c6c;
}

.rating-count {
  font-size: 14px;
  color: #999;
  margin-top: 10px;
}

.rating-distribution {
  padding-top: 15px;
}

.rating-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.star-label {
  font-size: 12px;
  color: #999;
  width: 30px;
}

.rating-row :deep(.el-progress) {
  flex: 1;
}

.star-count {
  font-size: 12px;
  color: #666;
  width: 30px;
  text-align: right;
}

/* 筛选标签 */
.overview-right {
  flex: 1;
}

.filter-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

/* 评价列表 */
.review-items {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.review-item {
  padding: 20px;
  border: 1px solid #eee;
  border-radius: 8px;
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.user-info {
  display: flex;
  gap: 12px;
  align-items: center;
}

.user-avatar {
  flex-shrink: 0;
}

.user-detail {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.username {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.purchase-info {
  font-size: 12px;
  color: #999;
}

.review-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 5px;
}

.review-time {
  font-size: 12px;
  color: #999;
}

/* 评价内容 */
.review-content {
  margin-bottom: 15px;
}

.review-text {
  font-size: 14px;
  color: #333;
  line-height: 1.6;
  margin-bottom: 15px;
}

/* 评价图片 */
.review-images {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 15px;
}

.review-image {
  width: 100px;
  height: 100px;
  border-radius: 4px;
  overflow: hidden;
  cursor: pointer;
}

.image-thumb {
  width: 100%;
  height: 100%;
  transition: transform 0.2s;
}

.image-thumb:hover {
  transform: scale(1.1);
}

/* 商家回复 */
.seller-reply {
  background: #f5f7fa;
  border-radius: 4px;
  padding: 15px;
}

.reply-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #666;
  margin-bottom: 10px;
}

.reply-text {
  font-size: 14px;
  color: #333;
  line-height: 1.6;
  margin: 0;
}

/* 评价操作 */
.review-actions {
  display: flex;
  gap: 15px;
  padding-top: 15px;
  border-top: 1px solid #eee;
}

.review-actions :deep(.el-button) {
  font-size: 13px;
  color: #999;
}
</style>
