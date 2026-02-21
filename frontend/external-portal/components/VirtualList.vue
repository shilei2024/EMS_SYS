<template>
  <div ref="container" class="virtual-list" :style="{ height: `${height}px`, overflow: 'auto' }">
    <div :style="{ height: `${totalHeight}px`, position: 'relative' }">
      <div
        ref="itemsRef"
        class="virtual-items"
        :style="{
          transform: `translateY(${offsetY}px)`,
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0
        }"
      >
        <div
          v-for="item in visibleItems"
          :key="item.key"
          :style="{ height: `${itemHeight}px` }"
          class="virtual-item"
        >
          <slot :item="item.data" :index="item.index"></slot>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface VirtualItem<T> {
  key: string | number
  index: number
  data: T
}

const props = withDefaults(defineProps<{
  items: any[]
  itemHeight: number
  height: number
  getItemKey?: (item: any, index: number) => string | number
}>(), {
  itemHeight: 50,
  height: 400
})

const emit = defineEmits<{
  scroll: [startIndex: number, endIndex: number]
}>()

const container = ref<HTMLElement | null>(null)
const visibleItems = ref<VirtualItem<any>[]>([])
const offsetY = ref(0)
const startIndex = ref(0)

// 计算可见区域能容纳的项数
const visibleCount = computed(() => Math.ceil(props.height / props.itemHeight) + 2)

// 计算总高度
const totalHeight = computed(() => props.items.length * props.itemHeight)

// 获取项的键
function getItemKey(item: any, index: number): string | number {
  if (props.getItemKey) {
    return props.getItemKey(item, index)
  }
  return item?.id || item?.key || index
}

// 更新可见区域
function updateVisibleItems() {
  if (!container.value) return

  const scrollTop = container.value.scrollTop
  const start = Math.max(0, Math.floor(scrollTop / props.itemHeight))
  const end = Math.min(props.items.length, start + visibleCount.value)

  startIndex.value = start

  visibleItems.value = props.items.slice(start, end).map((item, index) => ({
    key: getItemKey(item, start + index),
    index: start + index,
    data: item
  }))

  offsetY.value = start * props.itemHeight

  emit('scroll', start, end)
}

// 滚动到指定索引
function scrollToIndex(index: number) {
  if (container.value) {
    container.value.scrollTop = index * props.itemHeight
  }
}

// 滚动到顶部
function scrollToTop() {
  if (container.value) {
    container.value.scrollTop = 0
  }
}

// 滚动到底部
function scrollToBottom() {
  if (container.value) {
    container.value.scrollTop = totalHeight.value - props.height
  }
}

watch(() => props.items, () => {
  updateVisibleItems()
}, { deep: true })

onMounted(() => {
  updateVisibleItems()
})

// 暴露方法给父组件
defineExpose({
  scrollToIndex,
  scrollToTop,
  scrollToBottom
})
</script>

<style scoped>
.virtual-list {
  overflow-y: auto;
  contain: strict;
}

.virtual-items {
  will-change: transform;
}

.virtual-item {
  border-bottom: 1px solid #eee;
  background: white;
}

/* 滚动条样式 */
.virtual-list::-webkit-scrollbar {
  width: 6px;
}

.virtual-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.virtual-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.virtual-list::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
