<template>
  <div class="pagination-container">
    <el-pagination
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      :page-sizes="pageSizes"
      :total="total"
      :background="background"
      layout="total, sizes, prev, pager, next, jumper"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
    />
  </div>
</template>

<script setup lang="ts">
interface Props {
  total: number
  currentPage?: number
  pageSize?: number
  pageSizes?: number[]
  background?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  currentPage: 1,
  pageSize: 20,
  pageSizes: () => [10, 20, 50, 100],
  background: true
})

const emit = defineEmits<{
  'update:currentPage': [value: number]
  'update:pageSize': [value: number]
  change: [page: number, pageSize: number]
}>()

const currentPage = computed({
  get: () => props.currentPage,
  set: (value) => emit('update:currentPage', value)
})

const pageSize = computed({
  get: () => props.pageSize,
  set: (value) => emit('update:pageSize', value)
})

const handleSizeChange = (val: number) => {
  currentPage.value = 1
  emit('change', 1, val)
}

const handleCurrentChange = (val: number) => {
  emit('change', val, pageSize.value)
}
</script>

<style scoped>
.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
