<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon orders-icon">
            <el-icon><Document /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.totalOrders }}</div>
            <div class="stat-label">总订单数</div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon pending-icon">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.pendingOrders }}</div>
            <div class="stat-label">待处理</div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon revenue-icon">
            <el-icon><Money /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">¥{{ formatNumber(stats.totalRevenue) }}</div>
            <div class="stat-label">总营收</div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon components-icon">
            <el-icon><Box /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.totalComponents }}</div>
            <div class="stat-label">元器件型号</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="16">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>订单趋势</span>
              <el-radio-group v-model="trendType" size="small">
                <el-radio-button label="week">本周</el-radio-button>
                <el-radio-button label="month">本月</el-radio-button>
                <el-radio-button label="year">本年</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div class="chart-container">
            <v-chart :option="trendChartOption" autoresize />
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>订单状态分布</span>
            </div>
          </template>
          <div class="chart-container">
            <v-chart :option="statusChartOption" autoresize />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card class="table-card">
          <template #header>
            <div class="card-header">
              <span>最近订单</span>
              <el-button type="primary" link @click="$router.push('/orders')">查看全部</el-button>
            </div>
          </template>
          <el-table :data="recentOrders" style="width: 100%">
            <el-table-column prop="order_number" label="订单号" width="180" />
            <el-table-column prop="customer_name" label="客户" />
            <el-table-column prop="total_amount" label="金额" width="120">
              <template #default="{ row }">
                ¥{{ row.total_amount?.toFixed(2) || '0.00' }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card class="table-card">
          <template #header>
            <div class="card-header">
              <span>库存预警</span>
              <el-button type="primary" link @click="$router.push('/inventory')">查看全部</el-button>
            </div>
          </template>
          <el-table :data="lowStockItems" style="width: 100%">
            <el-table-column prop="mpn" label="型号" />
            <el-table-column prop="manufacturer" label="厂商" />
            <el-table-column prop="quantity" label="当前库存" width="100" />
            <el-table-column prop="reorder_point" label="补货点" width="100" />
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.quantity <= row.min_stock_level ? 'danger' : 'warning'">
                  {{ row.quantity <= row.min_stock_level ? '紧急' : '预警' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, PieChart, BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent, TitleComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { ElMessage } from 'element-plus'
import { getOrderStats, getOrderTrend, getOrders } from '../api/order'
import { getInventoryAlerts } from '../api/inventory'
import { getComponents } from '../api/kg'

use([CanvasRenderer, LineChart, PieChart, BarChart, GridComponent, TooltipComponent, LegendComponent, TitleComponent])

const trendType = ref('month')

const stats = reactive({
  totalOrders: 0,
  pendingOrders: 0,
  processingOrders: 0,
  approvedOrders: 0,
  rejectedOrders: 0,
  completedOrders: 0,
  todayOrders: 0,
  weekOrders: 0,
  monthOrders: 0,
  totalRevenue: 0,
  totalComponents: 0,
  lowStockItems: 0
})

const recentOrders = ref<any[]>([])
const lowStockItems = ref<any[]>([])
const trendData = ref<any[]>([])
const statusData = ref<any[]>([])
const loading = ref(false)

// 加载数据
async function loadData() {
  loading.value = true
  try {
    // 加载订单统计
    const orderStats = await getOrderStats()
    stats.totalOrders = orderStats.total_orders || 0
    stats.pendingOrders = orderStats.pending_orders || 0
    stats.processingOrders = orderStats.processing_orders || 0
    stats.approvedOrders = orderStats.approved_orders || 0
    stats.rejectedOrders = orderStats.rejected_orders || 0
    stats.completedOrders = orderStats.completed_orders || 0
    stats.todayOrders = orderStats.today_orders || 0
    stats.weekOrders = orderStats.week_orders || 0
    stats.monthOrders = orderStats.month_orders || 0

    // 加载订单趋势
    const days = trendType.value === 'week' ? 7 : trendType.value === 'month' ? 30 : 365
    const trendResult = await getOrderTrend(days)
    trendData.value = trendResult.data || []

    // 加载订单状态分布
    statusData.value = [
      { value: stats.pendingOrders, name: '待处理' },
      { value: stats.processingOrders, name: '处理中' },
      { value: stats.approvedOrders, name: '已通过' },
      { value: stats.rejectedOrders, name: '已拒绝' },
      { value: stats.completedOrders, name: '已完成' }
    ]

    // 加载最近订单
    const ordersRes = await getOrders({ page: 1, page_size: 5 })
    recentOrders.value = ordersRes.orders || []

    // 加载库存预警
    try {
      const alertsRes = await getInventoryAlerts({ type: 'low_stock', page: 1, page_size: 5 })
      lowStockItems.value = alertsRes.items || []
    } catch (e) {
      console.warn('加载库存预警失败')
    }

    // 加载元器件统计
    try {
      const kgStats = await getComponents({ limit: 1 })
      stats.totalComponents = kgStats.total || 0
    } catch (e) {
      console.warn('加载元器件统计失败')
    }

  } catch (error: any) {
    console.error('加载 Dashboard 数据失败:', error)
    ElMessage.warning('加载数据失败，使用模拟数据')
    loadMockData()
  } finally {
    loading.value = false
  }
}

function loadMockData() {
  stats.totalOrders = 1256
  stats.pendingOrders = 45
  stats.processingOrders = 120
  stats.approvedOrders = 856
  stats.rejectedOrders = 35
  stats.completedOrders = 200
  stats.todayOrders = 23
  stats.weekOrders = 156
  stats.monthOrders = 678
  stats.totalRevenue = 5680000
  stats.totalComponents = 8562

  recentOrders.value = [
    { order_number: 'PO-20260221-001', customer_name: '华为技术有限公司', total_amount: 15800, status: 'pending', created_at: '2026-02-21T10:30:00Z' },
    { order_number: 'PO-20260220-023', customer_name: '中兴通讯', total_amount: 23500, status: 'processing', created_at: '2026-02-20T15:20:00Z' },
    { order_number: 'PO-20260220-018', customer_name: '小米科技', total_amount: 8900, status: 'approved', created_at: '2026-02-20T11:45:00Z' },
    { order_number: 'PO-20260219-056', customer_name: 'OPPO 电子', total_amount: 32100, status: 'completed', created_at: '2026-02-19T14:20:00Z' },
    { order_number: 'PO-20260219-042', customer_name: 'vco 通信', total_amount: 18600, status: 'completed', created_at: '2026-02-19T09:15:00Z' }
  ]

  lowStockItems.value = [
    { mpn: 'STM32F407VGT6', manufacturer: 'STMicroelectronics', quantity: 50, reorder_point: 100, min_stock_level: 30 },
    { mpn: 'ESP32-WROOM-32', manufacturer: 'Espressif', quantity: 80, reorder_point: 200, min_stock_level: 50 },
    { mpn: 'ATMEGA328P-PU', manufacturer: 'Microchip', quantity: 25, reorder_point: 500, min_stock_level: 100 }
  ]

  trendData.value = [
    { date: '2026-02-01', count: 120 },
    { date: '2026-02-02', count: 132 },
    { date: '2026-02-03', count: 101 },
    { date: '2026-02-04', count: 134 },
    { date: '2026-02-05', count: 190 },
    { date: '2026-02-06', count: 230 },
    { date: '2026-02-07', count: 210 }
  ]
}

onMounted(() => {
  loadData()
})

// 监听趋势类型变化
watch(trendType, () => {
  loadData()
})

const trendChartOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  legend: { data: ['订单数', '营收'] },
  xAxis: {
    type: 'category',
    data: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
  },
  yAxis: [
    { type: 'value', name: '订单数' },
    { type: 'value', name: '营收(万元)' }
  ],
  series: [
    {
      name: '订单数',
      type: 'line',
      data: [120, 132, 101, 134, 190, 230, 210, 180, 201, 154, 190, 220],
      smooth: true
    },
    {
      name: '营收',
      type: 'line',
      yAxisIndex: 1,
      data: [45, 52, 48, 58, 72, 85, 80, 70, 78, 65, 72, 88],
      smooth: true
    }
  ]
}))

const statusChartOption = computed(() => ({
  tooltip: { trigger: 'item' },
  series: [
    {
      type: 'pie',
      radius: ['40%', '70%'],
      data: statusData.value
    }
  ]
}))

function formatNumber(num: number): string {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + '万'
  }
  return num.toString()
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN') + ' ' + date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

function getStatusType(status: string): string {
  const map: Record<string, string> = {
    pending: 'warning',
    processing: 'primary',
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
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 20px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: white;
  margin-right: 16px;
}

.orders-icon { background: linear-gradient(135deg, #667eea, #764ba2); }
.pending-icon { background: linear-gradient(135deg, #f093fb, #f5576c); }
.revenue-icon { background: linear-gradient(135deg, #4facfe, #00f2fe); }
.components-icon { background: linear-gradient(135deg, #43e97b, #38f9d7); }

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #333;
}

.stat-label {
  font-size: 14px;
  color: #999;
  margin-top: 4px;
}

.chart-card, .table-card {
  height: 400px;
}

.chart-container {
  height: 320px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
