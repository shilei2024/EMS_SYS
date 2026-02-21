<template>
  <div class="components-page">
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="型号">
          <el-input v-model="searchForm.mpn" placeholder="请输入型号" clearable />
        </el-form-item>
        <el-form-item label="厂商">
          <el-input v-model="searchForm.manufacturer" placeholder="请输入厂商" clearable />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="searchForm.category" placeholder="请选择分类" clearable>
            <el-option label="MCU" value="MCU" />
            <el-option label="Memory" value="Memory" />
            <el-option label="Power" value="Power" />
            <el-option label="Analog" value="Analog" />
            <el-option label="Sensor" value="Sensor" />
            <el-option label="Wireless" value="Wireless" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="toolbar-card">
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>
        新增元器件
      </el-button>
      <el-button @click="handleImport">批量导入</el-button>
      <el-button @click="handleExport">导出</el-button>
    </el-card>

    <el-card>
      <el-table :data="components" v-loading="loading">
        <el-table-column prop="mpn" label="型号" width="180" />
        <el-table-column prop="manufacturer" label="厂商" width="150" />
        <el-table-column prop="category" label="分类" width="100" />
        <el-table-column prop="package" label="封装" width="100" />
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="lifecycle_status" label="生命周期" width="100">
          <template #default="{ row }">
            <el-tag :type="getLifecycleType(row.lifecycle_status)">{{ getLifecycleText(row.lifecycle_status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="datalink" label="规格书" width="100">
          <template #default="{ row }">
            <el-button v-if="row.datalink" type="primary" link @click="viewDatasheet(row)">查看</el-button>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">查看</el-button>
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="primary" link @click="viewSubstitutes(row)">替代料</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          layout="total, prev, pager, next"
          @current-change="loadComponents"
        />
      </div>
    </el-card>

    <!-- 替代料对话框 -->
    <el-dialog v-model="substitutesVisible" title="替代料查询" width="700px">
      <el-table :data="substitutes" v-if="substitutes.length > 0">
        <el-table-column prop="mpn" label="型号" width="180" />
        <el-table-column prop="manufacturer" label="厂商" width="150" />
        <el-table-column prop="description" label="描述" min-width="200" />
        <el-table-column prop="confidence" label="匹配度" width="100">
          <template #default="{ row }">
            <el-progress :percentage="Math.round(row.confidence * 100)" :color="getConfidenceColor(row.confidence)" />
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-else description="暂无替代料数据" />
    </el-dialog>

    <!-- 新增/编辑元器件对话框 -->
    <el-dialog v-model="componentDialogVisible" :title="dialogTitle" width="700px">
      <el-form :model="componentForm" :rules="componentFormRules" ref="componentFormRef" label-width="100px">
        <el-form-item label="型号" prop="mpn">
          <el-input v-model="componentForm.mpn" :disabled="dialogType === 'edit'" placeholder="请输入元器件型号" />
        </el-form-item>
        <el-form-item label="厂商" prop="manufacturer">
          <el-input v-model="componentForm.manufacturer" placeholder="请输入厂商名称" />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="componentForm.category" placeholder="请选择分类" style="width: 100%">
            <el-option label="MCU" value="MCU" />
            <el-option label="Memory" value="Memory" />
            <el-option label="Power" value="Power" />
            <el-option label="Analog" value="Analog" />
            <el-option label="Sensor" value="Sensor" />
            <el-option label="Wireless" value="Wireless" />
          </el-select>
        </el-form-item>
        <el-form-item label="封装" prop="package">
          <el-input v-model="componentForm.package" placeholder="请输入封装类型" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="componentForm.description" type="textarea" :rows="3" placeholder="请输入产品描述" />
        </el-form-item>
        <el-form-item label="生命周期" prop="lifecycle_status">
          <el-select v-model="componentForm.lifecycle_status" placeholder="请选择生命周期状态" style="width: 100%">
            <el-option label="量产" value="Active" />
            <el-option label="不推荐" value="NRND" />
            <el-option label="停产" value="EOL" />
            <el-option label="已淘汰" value="Obsolete" />
          </el-select>
        </el-form-item>
        <el-form-item label="规格书" prop="datalink">
          <el-input v-model="componentForm.datalink" placeholder="请输入规格书链接" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="componentDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitComponentForm">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { searchComponents, findSubstitutes, getComponent, createComponent, updateComponent } from '../api/kg'

const loading = ref(false)
const substitutesVisible = ref(false)
const substitutes = ref<any[]>([])

// 新增/编辑对话框
const componentDialogVisible = ref(false)
const componentFormRef = ref<any>()
const dialogType = ref<'add' | 'edit'>('add')

const componentForm = reactive({
  mpn: '',
  manufacturer: '',
  description: '',
  category: '',
  package: '',
  lifecycle_status: 'Active',
  datalink: ''
})

const componentFormRules = {
  mpn: [{ required: true, message: '请输入型号', trigger: 'blur' }],
  manufacturer: [{ required: true, message: '请输入厂商', trigger: 'blur' }],
  description: [{ required: true, message: '请输入描述', trigger: 'blur' }]
}

const dialogTitle = computed(() => dialogType.value === 'add' ? '新增元器件' : '编辑元器件')

const searchForm = reactive({
  mpn: '',
  manufacturer: '',
  category: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const components = ref<any[]>([])

onMounted(() => {
  loadComponents()
})

async function loadComponents() {
  loading.value = true
  try {
    const params = {
      keyword: searchForm.mpn,
      manufacturer: searchForm.manufacturer,
      category: searchForm.category,
      limit: pagination.pageSize
    }
    const res = await searchComponents(params)
    components.value = res.components || []
    pagination.total = res.total || 0
  } catch (error: any) {
    console.error('加载元器件列表失败:', error)
    ElMessage.warning('加载失败，使用模拟数据')
    // 模拟数据
    components.value = [
      { mpn: 'STM32F407VGT6', manufacturer: 'STMicroelectronics', category: 'MCU', package: 'LQFP100', description: '32-bit ARM Cortex-M4 MCU, 168MHz, 1MB Flash', lifecycle_status: 'Active', datalink: 'https://www.st.com/stm32f4' },
      { mpn: 'STM32F103C8T6', manufacturer: 'STMicroelectronics', category: 'MCU', package: 'LQFP48', description: '32-bit ARM Cortex-M3 MCU, 72MHz, 64KB Flash', lifecycle_status: 'Active', datalink: 'https://www.st.com/stm32f1' },
      { mpn: 'ESP32-WROOM-32', manufacturer: 'Espressif Systems', category: 'Wireless', package: 'Module', description: 'WiFi + Bluetooth MCU, 240MHz, 4MB Flash', lifecycle_status: 'Active', datalink: 'https://www.espressif.com/esp32' },
      { mpn: 'ATMEGA328P-PU', manufacturer: 'Microchip Technology', category: 'MCU', package: 'DIP28', description: '8-bit AVR MCU, 20MHz, 32KB Flash', lifecycle_status: 'Active', datalink: 'https://www.microchip.com/atmega328p' },
      { mpn: 'MSP430F149IPM', manufacturer: 'Texas Instruments', category: 'MCU', package: 'LQFP64', description: '16-bit Ultra-Low-Power MCU, 8KB FRAM', lifecycle_status: 'Active', datalink: 'https://www.ti.com/msp430' }
    ]
    pagination.total = 5
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  pagination.page = 1
  loadComponents()
}

function handleReset() {
  searchForm.mpn = ''
  searchForm.manufacturer = ''
  searchForm.category = ''
  handleSearch()
}

function handleAdd() {
  dialogType.value = 'add'
  resetComponentForm()
  componentDialogVisible.value = true
}

function handleEdit(row: any) {
  dialogType.value = 'edit'
  Object.assign(componentForm, row)
  componentDialogVisible.value = true
}

function handleImport() {
  ElMessage.info('批量导入功能开发中')
}

function handleExport() {
  ElMessage.info('导出功能开发中')
}

function handleView(row: any) {
  ElMessage.info(`查看元器件：${row.mpn}`)
}

async function submitComponentForm() {
  if (!componentFormRef.value) return
  await componentFormRef.value.validate()
  try {
    if (dialogType.value === 'add') {
      await createComponent({
        mpn: componentForm.mpn,
        manufacturer: componentForm.manufacturer,
        description: componentForm.description,
        category: componentForm.category,
        package: componentForm.package,
        lifecycle_status: componentForm.lifecycle_status,
        datalink: componentForm.datalink
      })
      ElMessage.success('创建成功')
    } else {
      await updateComponent(componentForm.mpn, componentForm.manufacturer, {
        description: componentForm.description,
        category: componentForm.category,
        package: componentForm.package,
        lifecycle_status: componentForm.lifecycle_status,
        datalink: componentForm.datalink
      })
      ElMessage.success('更新成功')
    }
    componentDialogVisible.value = false
    loadComponents()
    resetComponentForm()
  } catch (error: any) {
    console.error('提交失败:', error)
    ElMessage.error(error.message || '操作失败')
  }
}

function resetComponentForm() {
  componentForm.mpn = ''
  componentForm.manufacturer = ''
  componentForm.description = ''
  componentForm.category = ''
  componentForm.package = ''
  componentForm.lifecycle_status = 'Active'
  componentForm.datalink = ''
  componentFormRef.value?.clearValidate()
}


async function viewSubstitutes(row: any) {
  try {
    const res = await findSubstitutes(row.mpn, row.manufacturer)
    substitutes.value = res.substitutes || []
    if (substitutes.value.length === 0) {
      ElMessage.info('暂无替代料数据')
    }
    substitutesVisible.value = true
  } catch (error: any) {
    console.error('查询替代料失败:', error)
    ElMessage.error('查询替代料失败')
    substitutesVisible.value = true
  }
}

function viewDatasheet(row: any) {
  window.open(row.datalink, '_blank')
}

function getLifecycleType(status: string): string {
  const map: Record<string, string> = { Active: 'success', EOL: 'danger', NRND: 'warning', 'Obsolete': 'info' }
  return map[status] || 'info'
}

function getLifecycleText(status: string): string {
  const map: Record<string, string> = { Active: '量产', EOL: '停产', NRND: '不推荐', 'Obsolete': '已淘汰' }
  return map[status] || status
}

function getConfidenceColor(confidence: number): string {
  if (confidence >= 0.9) return '#67c23a'
  if (confidence >= 0.7) return '#e6a23c'
  return '#f56c6c'
}
</script>

<style scoped>
.components-page {
  padding: 20px;
}

.search-card, .toolbar-card {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
