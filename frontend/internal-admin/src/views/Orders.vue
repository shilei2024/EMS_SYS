<template>
  <div class="orders-page">
    <!-- 搜索栏 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="订单号">
          <el-input v-model="searchForm.orderNumber" placeholder="请输入订单号" clearable />
        </el-form-item>
        <el-form-item label="客户名称">
          <el-input v-model="searchForm.customerName" placeholder="请输入客户名称" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable>
            <el-option label="待处理" value="pending" />
            <el-option label="处理中" value="processing" />
            <el-option label="待审核" value="review_needed" />
            <el-option label="已通过" value="approved" />
            <el-option label="已拒绝" value="rejected" />
            <el-option label="已完成" value="completed" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="searchForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 操作栏 -->
    <el-card class="toolbar-card">
      <div class="toolbar">
        <div class="toolbar-left">
          <el-button type="primary" @click="$router.push('/orders/upload')">
            <el-icon><Upload /></el-icon>
            上传订单
          </el-button>
          <el-button :disabled="!selectedRows.length" @click="handleBatchApprove">
            批量通过
          </el-button>
          <el-button :disabled="!selectedRows.length" type="danger" @click="handleBatchReject">
            批量拒绝
          </el-button>
        </div>
        <div class="toolbar-right">
          <el-button :icon="Refresh" @click="loadOrders">刷新</el-button>
        </div>
      </div>
    </el-card>

    <!-- 订单列表 -->
    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="orders"
        @selection-change="handleSelectionChange"
        style="width: 100%"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="order_number" label="订单号" width="180" />
        <el-table-column prop="customer_name" label="客户名称" min-width="150" />
        <el-table-column prop="customer_email" label="客户邮箱" min-width="150" />
        <el-table-column prop="total_amount" label="订单金额" width="120" align="right">
          <template #default="{ row }">
            ¥{{ row.total_amount?.toFixed(2) || '0.00' }}
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="80">
          <template #default="{ row }">
            <el-tag :type="getPriorityType(row.priority)">{{ getPriorityText(row.priority) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="ocr_confidence" label="OCR置信度" width="100">
          <template #default="{ row }">
            <el-progress
              :percentage="Math.round((row.ocr_confidence || 0) * 100)"
              :color="getConfidenceColor(row.ocr_confidence)"
              :stroke-width="10"
            />
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">查看</el-button>
            <el-button type="success" link @click="handleApprove(row)" v-if="row.status === 'pending' || row.status === 'review_needed'">通过</el-button>
            <el-button type="danger" link @click="handleReject(row)" v-if="row.status === 'pending' || row.status === 'review_needed'">拒绝</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[20, 50, 100, 200]"
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
         label="订单号<el-descriptions-item">{{ currentOrder.order_number }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentOrder.status)">{{ getStatusText(currentOrder.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="客户名称">{{ currentOrder.customer_name }}</el-descriptions-item>
        <el-descriptions-item label="客户邮箱">{{ currentOrder.customer_email }}</el-descriptions-item>
        <el-descriptions-item label="客户电话">{{ currentOrder.customer_phone }}</el-descriptions-item>
        <el-descriptions-item label="订单金额">¥{{ currentOrder.total_amount?.toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="OCR置信度">{{ ((currentOrder.ocr_confidence || 0) * 100).toFixed(1) }}%</el-descriptions-item>
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
          <template #default="{ row }">¥{{ row.unit_price?.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="total_price" label="总价" width="100">
          <template #default="{ row }">¥{{ row.total_price?.toFixed(2) }}</template>
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
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import {
  getOrders,
  getOrder,
  reviewOrder,
  deleteOrder,
  batchApproveOrders,
  batchRejectOrders,
  getOrderStats
} from '../api/order'

const loading = ref(false)
const detailVisible = ref(false)
const currentOrder = ref<any>(null)
const selectedRows = ref<any[]>([])

const searchForm = reactive({
  orderNumber: '',
  customerName: '',
  status: '',
  dateRange: []
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const orders = ref<any[]>([])

onMounted(() => {
  loadOrders()
})

async function loadOrders() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      order_number: searchForm.orderNumber,
      customer_name: searchForm.customerName,
      status: searchForm.status
    }
    // 添加日期范围参数
    if (searchForm.dateRange && searchForm.dateRange.length === 2) {
      params.start_date = searchForm.dateRange[0].toISOString()
      params.end_date = searchForm.dateRange[1].toISOString()
    }
    const res = await getOrders(params)
    orders.value = res.orders || []
    pagination.total = res.total || 0
    ElMessage.success('订单加载成功')
  } catch (error: any) {
    console.error('加载订单失败:', error)
    ElMessage.error(error.message || '加载订单失败，请检查网络连接')
    // 使用模拟数据
    orders.value = [
      { id: '1', order_number: 'PO-20260221-001', customer_name: '华为技术有限公司', customer_email: 'purchase@huawei.com', total_amount: 15800, status: 'pending', priority: 'high', ocr_confidence: 0.85, created_at: '2026-02-21T10:30:00Z', items: [] },
      { id: '2', order_number: 'PO-20260220-023', customer_name: '中兴通讯', customer_email: 'order@zte.com.cn', total_amount: 23500, status: 'processing', priority: 'normal', ocr_confidence: 0.92, created_at: '2026-02-20T15:20:00Z', items: [] },
      { id: '3', order_number: 'PO-20260220-018', customer_name: '小米科技', customer_email: 'supply@xiaomi.com', total_amount: 8900, status: 'approved', priority: 'low', ocr_confidence: 0.95, created_at: '2026-02-20T11:45:00Z', items: [] }
    ]
    pagination.total = 3
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  pagination.page = 1
  loadOrders()
}

function handleReset() {
  searchForm.orderNumber = ''
  searchForm.customerName = ''
  searchForm.status = ''
  searchForm.dateRange = []
  handleSearch()
}

function handleSelectionChange(rows: any[]) {
  selectedRows.value = rows
}

async function handleView(row: any) {
  currentOrder.value = null
  detailVisible.value = true
  try {
    const res = await getOrder(row.id)
    currentOrder.value = res
  } catch (error: any) {
    console.error('加载订单详情失败:', error)
    ElMessage.warning('加载订单详情失败，显示基本信息')
    currentOrder.value = row
  }
}

async function handleApprove(row: any) {
  try {
    await ElMessageBox.confirm('确定要通过此订单吗？', '审核通过', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    })
    await reviewOrder(row.id, 'approve', '')
    ElMessage.success('审核通过')
    loadOrders()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('审核失败:', error)
      ElMessage.error(error.message || '操作失败')
    }
  }
}

async function handleReject(row: any) {
  try {
    const { value } = await ElMessageBox.prompt('请输入拒绝原因', '拒绝订单', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPattern: /.+/,
      inputErrorMessage: '请输入拒绝原因'
    })
    await reviewOrder(row.id, 'reject', value)
    ElMessage.success('已拒绝')
    loadOrders()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('拒绝失败:', error)
      ElMessage.error(error.message || '操作失败')
    }
  }
}

async function handleDelete(row: any) {
  try {
    await ElMessageBox.confirm('确定要删除此订单吗？此操作不可恢复', '提示', {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    })
    await deleteOrder(row.id)
    ElMessage.success('删除成功')
    loadOrders()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error(error.message || '删除失败')
    }
  }
}

async function handleBatchApprove() {
  if (!selectedRows.value.length) {
    ElMessage.warning('请先选择要审核的订单')
    return
  }
  try {
    await ElMessageBox.confirm(`确定要批量通过 ${selectedRows.value.length} 个订单吗？`, '批量审核', {
      type: 'info'
    })
    const ids = selectedRows.value.map(r => r.id)
    await batchApproveOrders(ids)
    ElMessage.success(`已批量通过 ${ids.length} 个订单`)
    selectedRows.value = []
    loadOrders()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('批量通过失败:', error)
      ElMessage.error(error.message || '批量通过失败')
    }
  }
}

async function handleBatchReject() {
  if (!selectedRows.value.length) {
    ElMessage.warning('请先选择要拒绝的订单')
    return
  }
  try {
    const { value } = await ElMessageBox.prompt('请输入拒绝原因', '批量拒绝', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPattern: /.+/,
      inputErrorMessage: '请输入拒绝原因'
    })
    const ids = selectedRows.value.map(r => r.id)
    await batchRejectOrders(ids, value)
    ElMessage.success(`已批量拒绝 ${ids.length} 个订单`)
    selectedRows.value = []
    loadOrders()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('批量拒绝失败:', error)
      ElMessage.error(error.message || '批量拒绝失败')
    }
  }
}

function formatDate(dateStr: string): string {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN') + ' ' + date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

function getStatusType(status: string): string {
  const map: Record<string, string> = {
    pending: 'warning',
    processing: 'primary',
    review_needed: 'warning',
    approved: 'success',
    rejected: 'danger',
    completed: 'info'
  }
  return map[status] || 'info'
}

function getStatusText(status: string): string {
  const map: Record<string, string> = {
    pending: '待处理',
    processing: '处理中',
    review_needed: '待审核',
    approved: '已通过',
    rejected: '已拒绝',
    completed: '已完成'
  }
  return map[status] || status
}

function getPriorityType(priority: string): string {
  const map: Record<string, string> = {
    urgent: 'danger',
    high: 'warning',
    normal: '',
    low: 'info'
  }
  return map[priority] || ''
}

function getPriorityText(priority: string): string {
  const map: Record<string, string> = {
    urgent: '紧急',
    high: '高',
    normal: '普通',
    low: '低'
  }
  return map[priority] || priority
}

function getConfidenceColor(confidence?: number): string {
  if (!confidence || confidence >= 0.9) return '#67c23a'
  if (confidence >= 0.7) return '#e6a23c'
  return '#f56c6c'
}
</script>

<style scoped>
.orders-page {
  padding: 20px;
}

.search-card, .toolbar-card, .table-card {
  margin-bottom: 20px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
