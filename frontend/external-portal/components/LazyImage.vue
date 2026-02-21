<template>
  <div ref="container" class="lazy-image" :style="containerStyle">
    <!-- 加载中占位图 -->
    <div v-if="!loaded" class="lazy-placeholder">
      <el-icon class="is-loading" :size="32"><Loading /></el-icon>
    </div>

    <!-- 实际图片 -->
    <img
      v-show="loaded"
      :data-src="src"
      :src="src"
      :alt="alt"
      :class="['lazy-img', imageClass]"
      :style="imageStyle"
      @load="handleLoad"
      @error="handleError"
    />

    <!-- 错误状态 -->
    <div v-if="error && !loaded" class="lazy-error">
      <el-icon :size="24"><PictureFilled /></el-icon>
      <span>{{ errorText }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Loading, PictureFilled } from '@element-plus/icons-vue'

const props = defineProps({
  src: {
    type: String,
    required: true
  },
  alt: {
    type: String,
    default: ''
  },
  width: {
    type: [String, Number],
    default: '100%'
  },
  height: {
    type: [String, Number],
    default: 'auto'
  },
  placeholder: {
    type: String,
    default: ''
  },
  errorText: {
    type: String,
    default: '图片加载失败'
  },
  threshold: {
    type: Number,
    default: 50
  }
})

const emit = defineEmits<{
  load: [e: Event]
  error: [e: Event]
}>()

const container = ref<HTMLElement | null>(null)
const loaded = ref(false)
const error = ref(false)
const observer = ref<IntersectionObserver | null>(null)

const containerStyle = computed(() => ({
  width: typeof props.width === 'number' ? `${props.width}px` : props.width,
  height: typeof props.height === 'number' ? `${props.height}px` : props.height,
  position: 'relative' as const
}))

const imageStyle = computed(() => ({
  width: '100%',
  height: '100%',
  objectFit: 'cover' as const
}))

const imageClass = ref('')

function handleLoad(e: Event) {
  loaded.value = true
  error.value = false
  emit('load', e)
}

function handleError(e: Event) {
  error.value = true
  loaded.value = false
  emit('error', e)
}

function loadImage() {
  if (!props.src) {
    error.value = true
    return
  }

  const img = new Image()
  img.src = props.src
  img.onload = handleLoad
  img.onerror = handleError
}

onMounted(() => {
  // 使用 IntersectionObserver 实现懒加载
  if ('IntersectionObserver' in window) {
    observer.value = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            loadImage()
            observer.value?.unobserve(entry.target)
          }
        })
      },
      {
        rootMargin: `${props.threshold}px`
      }
    )

    if (container.value) {
      observer.value.observe(container.value)
    }
  } else {
    // 降级处理，直接加载
    loadImage()
  }
})

onUnmounted(() => {
  if (observer.value) {
    observer.value.disconnect()
  }
})
</script>

<style scoped>
.lazy-image {
  display: inline-block;
  background: #f5f7fa;
  overflow: hidden;
}

.lazy-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
}

.lazy-img {
  display: block;
  transition: opacity 0.3s;
}

.lazy-error {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #999;
  background: #f5f7fa;
}

.lazy-error .el-icon {
  margin-bottom: 8px;
}

.lazy-error span {
  font-size: 12px;
}
</style>
