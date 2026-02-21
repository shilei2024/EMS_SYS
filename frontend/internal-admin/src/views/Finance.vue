<template>
  <div class="finance-page">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="报销管理" name="expense">
        <!-- 报销搜索栏 -->
        <el-card class="search-card">
          <el-form :inline="true" :model="expenseSearchForm">
            <el-form-item label="报销类型">
              <el-select v-model="expenseSearchForm.type" placeholder="请选择" clearable>
                <el-option label="差旅" value="travel" />
                <el-option label="办公用品" value="office" />
                <el-option label="通讯" value="communication" />
                <el-option label="培训" value="training" />
                <el-option label="招待" value="entertainment" />
                <el-option label="其他" value="other" />
              </el-select>
            </el-form-item>
            <el-form-item label="状态">
              <el-select v-model="expenseSearchForm.status" placeholder="请选择" clearable>
                <el-option label="待审批" value="pending" />
                <el-option label="已批准" value="approved" />
                <el-option label="已拒绝" value="rejected" />
                <el-option label="已付款" value="paid" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="loadExpenses">查询</el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 报销操作栏 -->
        <el-card class="toolbar-card">
          <el-button type="primary" @click="handleCreateExpense">
            <el-icon><Plus /></el-icon>
            新建报销
          </el-button>
        </el-card>

        <!-- 报销列表 -->
        <el-card>
          <el-table :data="expenses" v-loading="expenseLoading">
            <el-table-column prop="id" label="报销单号" width="180" />
            <el-table-column prop="type" label="类型" width="100">
              <template #default="{ row }">
                {{ getExpenseTypeText(row.type) }}
              </template>
            </el-table-column>
            <el-table-column prop="amount" label="金额" width="120">
              <template #default="{ row }">
                ¥{{ row.amount?.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="currency" label="币种" width="60" />
            <el-table-column prop="description" label="描述" min-width="150" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getExpenseStatusType(row.status)">
                  {{ getExpenseStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="170">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button type="primary" link v-if="row.status === 'pending'" @click="handleApproveExpense(row)">审批</el-button>
                <el-button type="danger" link v-if="row.status === 'pending'" @click="handleRejectExpense(row)">拒绝</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="工资奖金" name="salary">
        <el-card>
          <el-table :data="salaries" v-loading="salaryLoading">
            <el-table-column prop="user_name" label="员工姓名" width="120" />
            <el-table-column prop="year" label="年份" width="80" />
            <el-table-column prop="month" label="月份" width="80" />
            <el-table-column prop="base_salary" label="基本工资" width="120">
              <template #default="{ row }">
                ¥{{ row.base_salary?.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="bonus" label="奖金" width="100">
              <template #default="{ row }">
                ¥{{ row.bonus?.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="net_salary" label="实发工资" width="120">
              <template #default="{ row }">
                <strong>¥{{ row.net_salary?.toFixed(2) }}</strong>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'paid' ? 'success' : 'warning'">
                  {{ row.status === 'paid' ? '已发放' : '待发放' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="销售对账" name="reconciliation">
        <el-card>
          <el-table :data="reconciliations" v-loading="reconciliationLoading">
            <el-table-column prop="sales_order_id" label="订单号" width="180" />
            <el-table-column prop="customer_name" label="客户" min-width="150" />
            <el-table-column prop="order_amount" label="订单金额" width="120">
              <template #default="{ row }">
                ¥{{ row.order_amount?.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="received_amount" label="已收金额" width="120">
              <template #default="{ row }">
                ¥{{ row.received_amount?.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="difference" label="差异" width="100">
              <template #default="{ row }">
                <span :class="{ 'text-danger': row.difference !== 0 }">
                  ¥{{ row.difference?.toFixed(2) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getReconciliationStatusType(row.status)">
                  {{ getReconciliationStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100">
              <template #default="{ row }">
                <el-button type="primary" link v-if="row.status === 'pending'" @click="handleConfirmReconciliation(row)">确认</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <!-- 新建报销对话框 -->
    <el-dialog v-model="expenseDialogVisible" title="新建报销" width="500px">
      <el-form :model="expenseForm" :rules="expenseFormRules" ref="expenseFormRef" label-width="100px">
        <el-form-item label="报销类型" prop="type">
          <el-select v-model="expenseForm.type" placeholder="请选择报销类型" style="width: 100%">
            <el-option label="差旅" value="travel" />
            <el-option label="办公用品" value="office" />
            <el-option label="通讯" value="communication" />
            <el-option label="培训" value="training" />
            <el-option label="招待" value="entertainment" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="金额" prop="amount">
          <el-input-number v-model="expenseForm.amount" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="币种" prop="currency">
          <el-select v-model="expenseForm.currency" placeholder="请选择币种" style="width: 100%">
            <el-option label="人民币" value="CNY" />
            <el-option label="美元" value="USD" />
            <el-option label="欧元" value="EUR" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="expenseForm.description" type="textarea" :rows="4" placeholder="请输入报销描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="expenseDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitExpenseForm">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import {
  getExpenses,
  approveExpense,
  rejectExpense,
  getSalaries,
  getReconciliations,
  confirmReconciliation,
  createExpense
} from '../api/finance'

const activeTab = ref('expense')

// 报销相关
const expenseSearchForm = reactive({ type: '', status: '' })
const expenseLoading = ref(false)
const expenses = ref<any[]>([])

// 工资相关
const salaryLoading = ref(false)
const salaries = ref<any[]>([])

// 对账相关
const reconciliationLoading = ref(false)
const reconciliations = ref<any[]>([])

// 新建报销对话框
const expenseDialogVisible = ref(false)
const expenseFormRef = ref<any>()
const expenseForm = reactive({
  type: 'travel',
  amount: 0,
  currency: 'CNY',
  description: ''
})

const expenseFormRules = {
  type: [{ required: true, message: '请选择报销类型', trigger: 'change' }],
  amount: [{ required: true, message: '请输入金额', trigger: 'blur' }],
  description: [{ required: true, message: '请输入描述', trigger: 'blur' }]
}

onMounted(() => {
  loadExpenses()
  loadSalaries()
  loadReconciliations()
})

async function loadExpenses() {
  expenseLoading.value = true
  try {
    const params = {
      status: expenseSearchForm.status,
      type: expenseSearchForm.type
    }
    const res = await getExpenses(params)
    expenses.value = res.items || []
  } catch (error: any) {
    console.error('加载报销列表失败:', error)
    ElMessage.warning('加载失败，使用模拟数据')
    expenses.value = [
      { id: 'EXP-20260221-001', type: 'travel', amount: 2580, currency: 'CNY', description: '深圳出差交通及住宿', status: 'pending', created_at: '2026-02-21T10:00:00Z' },
      { id: 'EXP-20260220-015', type: 'office', amount: 560, currency: 'CNY', description: '办公用品采购', status: 'approved', created_at: '2026-02-20T14:30:00Z' },
      { id: 'EXP-20260219-008', type: 'training', amount: 3200, currency: 'CNY', description: '技术培训费用', status: 'rejected', created_at: '2026-02-19T09:15:00Z' }
    ]
  } finally {
    expenseLoading.value = false
  }
}

async function loadSalaries() {
  salaryLoading.value = true
  try {
    const res = await getSalaries()
    salaries.value = res.items || []
  } catch (error: any) {
    console.error('加载工资列表失败:', error)
    salaries.value = [
      { user_name: '张三', year: 2026, month: 2, base_salary: 15000, bonus: 3000, net_salary: 16500, status: 'pending' },
      { user_name: '李四', year: 2026, month: 2, base_salary: 12000, bonus: 2000, net_salary: 12800, status: 'paid' }
    ]
  } finally {
    salaryLoading.value = false
  }
}

async function loadReconciliations() {
  reconciliationLoading.value = true
  try {
    const res = await getReconciliations()
    reconciliations.value = res.items || []
  } catch (error: any) {
    console.error('加载对账列表失败:', error)
    reconciliations.value = [
      { sales_order_id: 'SO-20260215-001', customer_name: '华为技术有限公司', order_amount: 56800, received_amount: 56800, difference: 0, status: 'confirmed' },
      { sales_order_id: 'SO-20260210-008', customer_name: '中兴通讯', order_amount: 23500, received_amount: 20000, difference: -3500, status: 'pending' }
    ]
  } finally {
    reconciliationLoading.value = false
  }
}

function handleCreateExpense() {
  expenseDialogVisible.value = true
}

async function submitExpenseForm() {
  if (!expenseFormRef.value) return
  await expenseFormRef.value.validate()
  try {
    await createExpense({
      type: expenseForm.type,
      amount: expenseForm.amount,
      currency: expenseForm.currency,
      description: expenseForm.description
    })
    ElMessage.success('创建成功')
    expenseDialogVisible.value = false
    loadExpenses()
    resetExpenseForm()
  } catch (error: any) {
    console.error('创建失败:', error)
    ElMessage.error(error.message || '创建失败')
  }
}

function resetExpenseForm() {
  expenseForm.type = 'travel'
  expenseForm.amount = 0
  expenseForm.currency = 'CNY'
  expenseForm.description = ''
  expenseFormRef.value?.clearValidate()
}

async function handleApproveExpense(row: any) {
  try {
    await ElMessageBox.confirm('确定要批准此报销吗？', '审批确认', { type: 'info' })
    await approveExpense(row.id, '审批通过')
    ElMessage.success('审批通过')
    loadExpenses()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('审批失败:', error)
      ElMessage.error(error.message || '审批失败')
    }
  }
}

async function handleRejectExpense(row: any) {
  try {
    const { value } = await ElMessageBox.prompt('请输入拒绝原因', '拒绝报销', {
      inputPattern: /.+/,
      inputErrorMessage: '请输入原因'
    })
    await rejectExpense(row.id, value)
    ElMessage.success('已拒绝')
    loadExpenses()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('拒绝失败:', error)
      ElMessage.error(error.message || '拒绝失败')
    }
  }
}

async function handleConfirmReconciliation(row: any) {
  try {
    await confirmReconciliation(row.id, '确认无误')
    ElMessage.success('确认成功')
    loadReconciliations()
  } catch (error: any) {
    console.error('确认失败:', error)
    ElMessage.error(error.message || '确认失败')
  }
}

function getExpenseTypeText(type: string): string {
  const map: Record<string, string> = { travel: '差旅', office: '办公', communication: '通讯', training: '培训', entertainment: '招待', other: '其他' }
  return map[type] || type
}

function getExpenseStatusType(status: string): string {
  const map: Record<string, string> = { pending: 'warning', approved: 'success', rejected: 'danger', paid: 'info' }
  return map[status] || 'info'
}

function getExpenseStatusText(status: string): string {
  const map: Record<string, string> = { pending: '待审批', approved: '已批准', rejected: '已拒绝', paid: '已付款' }
  return map[status] || status
}

function getReconciliationStatusType(status: string): string {
  const map: Record<string, string> = { pending: 'warning', confirmed: 'success', disputed: 'danger' }
  return map[status] || 'info'
}

function getReconciliationStatusText(status: string): string {
  const map: Record<string, string> = { pending: '待确认', confirmed: '已确认', disputed: '有争议' }
  return map[status] || status
}

function formatDate(dateStr: string): string {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}
</script>

<style scoped>
.finance-page {
  padding: 20px;
}

.search-card, .toolbar-card {
  margin-bottom: 20px;
}

.text-danger {
  color: #f56c6c;
}
</style>
