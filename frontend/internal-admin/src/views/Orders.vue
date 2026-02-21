<template>
  <div class="orders-container">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>订单列表</span>
          <el-button type="primary" @click="loadOrders">刷新</el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="订单号">
          <el-input v-model="searchForm.order_number" placeholder="请输入订单号" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable>
            <el-option label="待处理" value="pending" />
            <el-option label="处理中" value="processing" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 订单表格 -->
      <el-table :data="orders" v-loading="loading" style="width: 100%">
        <el-table-column prop="order_number" label="订单号" />
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="customer_name" label="客户名称" />
        <el-table-column prop="customer_email" label="客户邮箱" />
        <el-table-column prop="total_amount" label="订单金额">
          <template #default="{ row }">
            ¥{{ row.total_amount?.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="viewDetail(row)">详情</el-button>
            <el-button size="small" type="primary" @click="processOrder(row)">处理</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.page_size"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadOrders"
          @current-change="loadOrders"
        />
      </div>
    </el-card>

    <!-- 订单详情对话框 -->
    <el-dialog v-model="detailVisible" title="订单详情" width="800px">
      <el-descriptions :column="2" border v-if="currentOrder">
        <el-descriptions-item label="订单号">{{ currentOrder.order_number }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentOrder.status)">{{ getStatusText(currentOrder.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="客户名称">{{ currentOrder.customer_name }}</el-descriptions-item>
        <el-descriptions-item label="客户邮箱">{{ currentOrder.customer_email }}</el-descriptions-item>
        <el-descriptions-item label="客户电话">{{ currentOrder.customer_phone }}</el-descriptions-item>
        <el-descriptions-item label="订单金额">¥{{ currentOrder.total_amount?.toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="OCR 置信度">{{ ((currentOrder.ocr_confidence || 0) * 100).toFixed(1) }}%</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatDate(currentOrder.created_at) }}</el-descriptions-item>
      </el-descriptions>

      <el-divider>订单明细</el-divider>

      <el-table :data="currentOrder?.items || []" style="width: 100%">
        <el-table-column prop="line_number" label="行号" width="60" />
        <el-table-column prop="mpn" label="型号" />
        <el-table-column prop="manufacturer" label="厂商" />
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="quantity" label="数量" width="80" />
        <el-table-column prop="unit_price" label="单价" width="100">
          <template #default="{ row }">
            ¥{{ row.unit_price?.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="total_price" label="总价" width="100">
          <template #default="{ row }">
            ¥{{ row.total_price?.toFixed(2) }}
          </template>
        </el-table-column>
      </el-table>

      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

interface Order {
  id: number
  order_number: string
  status: string
  customer_name: string
  customer_email: string
  customer_phone: string
  total_amount: number
  ocr_confidence: number
  created_at: string
  items: OrderItem[]
}

interface OrderItem {
  line_number: number
  mpn: string
  manufacturer: string
  description: string
  quantity: number
  unit_price: number
  total_price: number
}

const loading = ref(false)
const detailVisible = ref(false)
const currentOrder = ref<Order | null>(null)

const searchForm = reactive({
  order_number: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

const orders = ref<Order[]>([])

const loadOrders = async () => {
  loading.value = true
  try {
    // TODO: Replace with actual API call
    // const response = await api.getOrders(pagination.page, pagination.page_size, searchForm)
    // orders.value = response.data.orders
    // pagination.total = response.data.total

    // Mock data for demo
    orders.value = [
      {
        id: 1,
        order_number: 'ORD-2024-001',
        status: 'pending',
        customer_name: '张三',
        customer_email: 'zhangsan@example.com',
        customer_phone: '13800138000',
        total_amount: 12500.00,
        ocr_confidence: 0.95,
        created_at: new Date().toISOString(),
        items: []
      }
    ]
    pagination.total = 1
  } catch (error) {
    ElMessage.error('加载订单列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadOrders()
}

const resetSearch = () => {
  searchForm.order_number = ''
  searchForm.status = ''
  pagination.page = 1
  loadOrders()
}

const viewDetail = async (order: Order) => {
  currentOrder.value = order
  detailVisible.value = true
}

const processOrder = async (order: Order) => {
  ElMessage.info(`处理订单：${order.order_number}`)
  // TODO: Implement order processing logic
}

const getStatusType = (status: string): string => {
  const types: Record<string, string> = {
    pending: 'warning',
    processing: 'primary',
    completed: 'success',
    cancelled: 'danger'
  }
  return types[status] || 'info'
}

const getStatusText = (status: string): string => {
  const texts: Record<string, string> = {
    pending: '待处理',
    processing: '处理中',
    completed: '已完成',
    cancelled: '已取消'
  }
  return texts[status] || status
}

const formatDate = (date: string): string => {
  return new Date(date).toLocaleString('zh-CN')
}

onMounted(() => {
  loadOrders()
})
</script>

<style scoped>
.orders-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
</style>
