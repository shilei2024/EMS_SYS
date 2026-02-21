<template>
  <div class="users-page">
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="用户名">
          <el-input v-model="searchForm.username" placeholder="请输入用户名" clearable />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="searchForm.email" placeholder="请输入邮箱" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.isActive" placeholder="请选择" clearable>
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
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
        新增用户
      </el-button>
    </el-card>

    <el-card>
      <el-table :data="users" v-loading="loading">
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="email" label="邮箱" min-width="180" />
        <el-table-column prop="full_name" label="姓名" width="120" />
        <el-table-column prop="department" label="部门" width="120" />
        <el-table-column prop="role_name" label="角色" width="120">
          <template #default="{ row }">
            <el-tag>{{ row.role_name || '普通用户' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_login_at" label="最后登录" width="170">
          <template #default="{ row }">
            {{ formatDate(row.last_login_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="warning" link @click="handleChangePassword(row)">改密</el-button>
            <el-button :type="row.is_active ? 'danger' : 'success'" link @click="toggleStatus(row)">
              {{ row.is_active ? '禁用' : '启用' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          layout="total, prev, pager, next"
          @current-change="loadUsers"
        />
      </div>
    </el-card>

    <!-- 用户对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form :model="userForm" :rules="userRules" ref="formRef" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" :disabled="dialogType === 'edit'" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" />
        </el-form-item>
        <el-form-item label="姓名" prop="fullName">
          <el-input v-model="userForm.full_name" />
        </el-form-item>
        <el-form-item label="部门" prop="department">
          <el-input v-model="userForm.department" />
        </el-form-item>
        <el-form-item label="角色" prop="roleId">
          <el-select v-model="userForm.role_id" placeholder="请选择角色">
            <el-option v-for="role in roles" :key="role.id" :label="role.name" :value="role.id" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="dialogType === 'add'" label="密码" prop="password">
          <el-input v-model="userForm.password" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>

    <!-- 修改密码对话框 -->
    <el-dialog v-model="passwordDialogVisible" title="修改密码" width="400px">
      <el-form :model="passwordForm" :rules="passwordFormRules" ref="passwordFormRef" label-width="100px">
        <el-form-item label="旧密码" prop="old_password">
          <el-input v-model="passwordForm.old_password" type="password" show-password placeholder="请输入旧密码" />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="passwordForm.new_password" type="password" show-password placeholder="请输入新密码" />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm_password">
          <el-input v-model="passwordForm.confirm_password" type="password" show-password placeholder="请再次输入新密码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="passwordDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitPasswordForm">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox, FormInstance } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import {
  getUsers,
  createUser,
  updateUser,
  getRoles,
  toggleUserStatus,
  changePassword
} from '../api/auth'

const loading = ref(false)
const dialogVisible = ref(false)
const passwordDialogVisible = ref(false)
const dialogType = ref<'add' | 'edit'>('add')
const formRef = ref<FormInstance>()
const passwordFormRef = ref<FormInstance>()
const currentUserId = ref('')

const searchForm = reactive({ username: '', email: '', isActive: '' })
const pagination = reactive({ page: 1, pageSize: 20, total: 0 })
const users = ref<any[]>([])
const roles = ref<any[]>([])

const userForm = reactive({
  id: '',
  username: '',
  email: '',
  full_name: '',
  department: '',
  role_id: 0,
  password: ''
})

const userRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  full_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少 6 位', trigger: 'blur' }
  ]
}

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const passwordFormRules = {
  old_password: [{ required: true, message: '请输入旧密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少 6 位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule: any, value: string, callback: any) => {
        if (value !== passwordForm.new_password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const dialogTitle = computed(() => dialogType.value === 'add' ? '新增用户' : '编辑用户')

onMounted(() => {
  loadUsers()
  loadRoles()
})

async function loadUsers() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      username: searchForm.username,
      email: searchForm.email,
      is_active: searchForm.isActive === '' ? undefined : searchForm.isActive
    }
    const res = await getUsers(params)
    users.value = res.items || []
    pagination.total = res.total || 0
  } catch (error: any) {
    console.error('加载用户列表失败:', error)
    ElMessage.warning('加载失败，使用模拟数据')
    users.value = [
      { id: '1', username: 'admin', email: 'admin@example.com', full_name: '系统管理员', department: 'IT', role_name: '超级管理员', is_active: true, last_login_at: '2026-02-21T10:00:00Z', created_at: '2026-01-01T00:00:00Z' },
      { id: '2', username: 'zhangsan', email: 'zhangsan@example.com', full_name: '张三', department: '销售', role_name: '订单管理员', is_active: true, last_login_at: '2026-02-20T15:30:00Z', created_at: '2026-01-15T00:00:00Z' },
      { id: '3', username: 'lisi', email: 'lisi@example.com', full_name: '李四', department: '技术', role_name: 'FAE 工程师', is_active: true, last_login_at: '2026-02-19T09:20:00Z', created_at: '2026-01-20T00:00:00Z' }
    ]
    pagination.total = 3
  } finally {
    loading.value = false
  }
}

async function loadRoles() {
  try {
    const res = await getRoles()
    roles.value = res.roles || []
  } catch (error) {
    console.warn('加载角色列表失败')
  }
}

function handleSearch() {
  pagination.page = 1
  loadUsers()
}

function handleReset() {
  searchForm.username = ''
  searchForm.email = ''
  searchForm.isActive = ''
  handleSearch()
}

function handleAdd() {
  dialogType.value = 'add'
  resetForm()
  dialogVisible.value = true
}

function handleEdit(row: any) {
  dialogType.value = 'edit'
  Object.assign(userForm, row)
  dialogVisible.value = true
}

function handleChangePassword(row: any) {
  currentUserId.value = row.id
  resetPasswordForm()
  passwordDialogVisible.value = true
}

async function submitPasswordForm() {
  if (!passwordFormRef.value) return
  await passwordFormRef.value.validate()
  try {
    await changePassword(currentUserId.value, passwordForm.old_password, passwordForm.new_password)
    ElMessage.success('密码修改成功')
    passwordDialogVisible.value = false
    resetPasswordForm()
  } catch (error: any) {
    console.error('修改密码失败:', error)
    ElMessage.error(error.message || '修改密码失败')
  }
}

function resetPasswordForm() {
  passwordForm.old_password = ''
  passwordForm.new_password = ''
  passwordForm.confirm_password = ''
  passwordFormRef.value?.clearValidate()
}

async function toggleStatus(row: any) {
  try {
    const action = row.is_active ? '禁用' : '启用'
    await ElMessageBox.confirm(`确定要${action}此用户吗？`, '提示', { type: 'warning' })
    await toggleUserStatus(row.id, !row.is_active)
    ElMessage.success(`${action}成功`)
    loadUsers()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('状态变更失败:', error)
      ElMessage.error(error.message || '操作失败')
    }
  }
}

async function submitForm() {
  if (!formRef.value) return
  await formRef.value.validate()
  try {
    if (dialogType.value === 'add') {
      await createUser({
        username: userForm.username,
        email: userForm.email,
        full_name: userForm.full_name,
        department: userForm.department,
        role_id: userForm.role_id,
        password: userForm.password
      })
      ElMessage.success('创建成功')
    } else {
      await updateUser(userForm.id, {
        email: userForm.email,
        full_name: userForm.full_name,
        department: userForm.department,
        role_id: userForm.role_id
      })
      ElMessage.success('更新成功')
    }
    dialogVisible.value = false
    loadUsers()
  } catch (error: any) {
    console.error('提交失败:', error)
    ElMessage.error(error.message || '操作失败')
  }
}

function resetForm() {
  userForm.id = ''
  userForm.username = ''
  userForm.email = ''
  userForm.full_name = ''
  userForm.department = ''
  userForm.role_id = 0
  userForm.password = ''
  formRef.value?.clearValidate()
}

function formatDate(dateStr?: string): string {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}
</script>

<style scoped>
.users-page {
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
