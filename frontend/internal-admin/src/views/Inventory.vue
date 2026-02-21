<template>
  <div class="inventory-page">
    <!-- 搜索栏 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="型号">
          <el-input v-model="searchForm.mpn" placeholder="请输入型号" clearable />
        </el-form-item>
        <el-form-item label="厂商">
          <el-input v-model="searchForm.manufacturer" placeholder="请输入厂商" clearable />
        </el-form-item>
        <el-form-item label="仓库">
          <el-select v-model="searchForm.warehouse" placeholder="请选择仓库" clearable>
            <el-option label="深圳仓" value="SZ" />
            <el-option label="上海仓" value="SH" />
            <el-option label="北京仓" value="BJ" />
          </el-select>
        </el-form-item>
        <el-form-item label="库存状态">
          <el-checkbox v-model="searchForm.lowStock">仅看低库存</el-checkbox>
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
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增库存
          </el-button>
          <el-button @click="handleExport">导出</el-button>
        </div>
        <div class="toolbar-right">
          <el-button :icon="Refresh" @click="loadInventory">刷新</el-button>
        </div>
      </div>
    </el-card>

    <!-- 库存列表 -->
    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="inventoryList"
        style="width: 100%"
      >
        <el-table-column prop="mpn" label="型号" width="180" />
        <el-table-column prop="manufacturer" label="厂商" width="150" />
        <el-table-column prop="warehouse_location" label="仓库" width="100" />
        <el-table-column prop="quantity" label="库存数量" width="100">
          <template #default="{ row }">
            <span :class="{ 'low-stock': row.quantity <= row.reorder_point }">
              {{ row.quantity }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="safety_stock" label="安全库存" width="100" />
        <el-table-column prop="reorder_point" label="补货点" width="80" />
        <el-table-column prop="unit_cost" label="成本" width="100">
          <template #default="{ row }">
            ¥{{ row.unit_cost?.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.quantity <= row.safety_stock" type="danger">紧急</el-tag>
            <el-tag v-else-if="row.quantity <= row.reorder_point" type="warning">预警</el-tag>
            <el-tag v-else type="success">正常</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="更新时间" width="170">
          <template #default="{ row }">
            {{ formatDate(row.updated_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleAdjust(row)">调整</el-button>
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
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
          @size-change="loadInventory"
          @current-change="loadInventory"
        />
      </div>
    </el-card>

    <!-- 库存调整对话框 -->
    <el-dialog v-model="adjustVisible" title="库存调整" width="500px">
      <el-form :model="adjustForm" label-width="100px">
        <el-form-item label="型号">
          <el-input v-model="adjustForm.mpn" disabled />
        </el-form-item>
        <el-form-item label="当前库存">
          <el-input v-model="adjustForm.currentQty" disabled />
        </el-form-item>
        <el-form-item label="调整类型">
          <el-radio-group v-model="adjustForm.adjustType">
            <el-radio label="in">入库</el-radio>
            <el-radio label="out">出库</el-radio>
            <el-radio label="adjustment">调整</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="调整数量">
          <el-input-number v-model="adjustForm.adjustQty" :min="1" />
        </el-form-item>
        <el-form-item label="原因">
          <el-input v-model="adjustForm.reason" type="textarea" :rows="2" placeholder="请输入调整原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="adjustVisible = false">取消</el-button>
        <el-button type="primary" @click="submitAdjust">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'
import {
  getInventoryList,
  adjustInventory,
  deleteInventory
} from '../api/inventory'

const loading = ref(false)
const adjustVisible = ref(false)
const currentInventoryId = ref('')

const searchForm = reactive({
  mpn: '',
  manufacturer: '',
  warehouse: '',
  lowStock: false
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const inventoryList = ref<any[]>([])

const adjustForm = reactive({
  mpn: '',
  currentQty: 0,
  adjustType: 'in' as 'in' | 'out' | 'adjustment',
  adjustQty: 1,
  reason: ''
})

onMounted(() => {
  loadInventory()
})

async function loadInventory() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      mpn: searchForm.mpn,
      manufacturer: searchForm.manufacturer,
      warehouse_location: searchForm.warehouse
    }
    const res = await getInventoryList(params)
    inventoryList.value = res.items || []
    pagination.total = res.total || 0
  } catch (error: any) {
    console.error('加载库存列表失败:', error)
    ElMessage.warning('加载库存列表失败，使用模拟数据')
    // 使用模拟数据
    inventoryList.value = [
      { mpn: 'STM32F407VGT6', manufacturer: 'STMicroelectronics', warehouse_location: 'SZ', quantity: 50, safety_stock: 30, reorder_point: 100, unit_cost: 5.2, updated_at: '2026-02-21T10:00:00Z' },
      { mpn: 'ESP32-WROOM-32', manufacturer: 'Espressif', warehouse_location: 'SZ', quantity: 80, safety_stock: 50, reorder_point: 200, unit_cost: 3.5, updated_at: '2026-02-21T09:30:00Z' },
      { mpn: 'ATMEGA328P-PU', manufacturer: 'Microchip', warehouse_location: 'SH', quantity: 500, safety_stock: 100, reorder_point: 500, unit_cost: 2.8, updated_at: '2026-02-20T16:00:00Z' }
    ]
    pagination.total = 3
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  pagination.page = 1
  loadInventory()
}

function handleReset() {
  searchForm.mpn = ''
  searchForm.manufacturer = ''
  searchForm.warehouse = ''
  searchForm.lowStock = false
  handleSearch()
}

function handleAdd() {
  ElMessage.info('新增库存功能开发中')
}

function handleExport() {
  ElMessage.info('导出功能开发中')
}

function handleEdit(row: any) {
  ElMessage.info('编辑功能开发中')
}

function handleAdjust(row: any) {
  currentInventoryId.value = row.id
  adjustForm.mpn = row.mpn
  adjustForm.currentQty = row.quantity
  adjustForm.adjustType = 'in'
  adjustForm.adjustQty = 1
  adjustForm.reason = ''
  adjustVisible.value = true
}

async function submitAdjust() {
  try {
    await adjustInventory({
      inventory_id: currentInventoryId.value,
      adjustment_type: adjustForm.adjustType,
      quantity_change: adjustForm.adjustType === 'out' ? -adjustForm.adjustQty : adjustForm.adjustQty,
      reason: adjustForm.reason
    })
    ElMessage.success('库存调整成功')
    adjustVisible.value = false
    loadInventory()
  } catch (error: any) {
    console.error('库存调整失败:', error)
    ElMessage.error(error.message || '库存调整失败')
  }
}

async function handleDelete(row: any) {
  try {
    await ElMessageBox.confirm('确定要删除此库存记录吗？', '提示', { type: 'warning' })
    await deleteInventory(row.id)
    ElMessage.success('删除成功')
    loadInventory()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error(error.message || '删除失败')
    }
  }
}

function formatDate(dateStr: string): string {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN') + ' ' + date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}
</script>

<style scoped>
.inventory-page {
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

.toolbar-left {
  display: flex;
  gap: 10px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.low-stock {
  color: #f56c6c;
  font-weight: 600;
}
</style>
