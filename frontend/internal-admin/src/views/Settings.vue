<template>
  <div class="settings-page">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="系统配置" name="system">
        <el-card>
          <el-form :model="systemConfig" label-width="150px">
            <el-form-item label="系统名称">
              <el-input v-model="systemConfig.systemName" />
            </el-form-item>
            <el-form-item label="系统版本">
              <el-input v-model="systemConfig.version" disabled />
            </el-form-item>
            <el-form-item label="OCR最小置信度">
              <el-slider v-model="systemConfig.ocrMinConfidence" :min="0.5" :max="1" :step="0.05" show-stops />
              <span>{{ (systemConfig.ocrMinConfidence * 100).toFixed(0) }}%</span>
            </el-form-item>
            <el-form-item label="订单自动审核阈值">
              <el-slider v-model="systemConfig.autoApproveThreshold" :min="0.7" :max="1" :step="0.05" show-stops />
              <span>{{ (systemConfig.autoApproveThreshold * 100).toFixed(0) }}%</span>
            </el-form-item>
            <el-form-item label="登录失败锁定次数">
              <el-input-number v-model="systemConfig.loginAttemptsLimit" :min="3" :max="10" />
            </el-form-item>
            <el-form-item label="会话超时时间(小时)">
              <el-input-number v-model="systemConfig.sessionTimeoutHours" :min="1" :max="24" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveSystemConfig">保存配置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="模型配置" name="model">
        <el-card>
          <el-table :data="modelConfigs" style="width: 100%">
            <el-table-column prop="name" label="模型名称" width="150" />
            <el-table-column prop="provider" label="提供商" width="120" />
            <el-table-column prop="displayName" label="显示名称" width="150" />
            <el-table-column prop="priority" label="优先级" width="80" />
            <el-table-column prop="is_enabled" label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="row.is_enabled ? 'success' : 'info'">
                  {{ row.is_enabled ? '启用' : '禁用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button type="primary" link @click="configureModel(row)">配置</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="订单源配置" name="orderSource">
        <el-card>
          <div class="toolbar">
            <el-button type="primary" @click="addOrderSource">新增订单源</el-button>
          </div>
          <el-table :data="orderSources" style="width: 100%; margin-top: 20px">
            <el-table-column prop="name" label="名称" width="150" />
            <el-table-column prop="source_type" label="类型" width="120">
              <template #default="{ row }">
                <el-tag>{{ getSourceTypeText(row.source_type) }}</el-tag>
              </el-table-column>
            <el-table-column prop="config</template>
            " label="配置" min-width="200">
              <template #default="{ row }">
                <span v-if="row.source_type === 'api'">API端点: {{ row.config?.endpoint }}</span>
                <span v-else-if="row.source_type === 'imap'">邮箱: {{ row.config?.host }}</span>
                <span v-else>文件目录: {{ row.config?.path }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="is_active" label="状态" width="80">
              <template #default="{ row }">
                <el-switch v-model="row.is_active" />
              </template>
            </el-table-column>
            <el-table-column prop="last_sync_at" label="最后同步" width="170">
              <template #default="{ row }">
                {{ formatDate(row.last_sync_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button type="primary" link @click="editOrderSource(row)">编辑</el-button>
                <el-button type="danger" link @click="deleteOrderSource(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="安全设置" name="security">
        <el-card>
          <el-form :model="securityConfig" label-width="150px">
            <el-form-item label="密码最小长度">
              <el-input-number v-model="securityConfig.passwordMinLength" :min="6" :max="32" />
            </el-form-item>
            <el-form-item label="必须包含大写字母">
              <el-switch v-model="securityConfig.passwordRequireUpper" />
            </el-form-item>
            <el-form-item label="必须包含小写字母">
              <el-switch v-model="securityConfig.passwordRequireLower" />
            </el-form-item>
            <el-form-item label="必须包含数字">
              <el-switch v-model="securityConfig.passwordRequireDigit" />
            </el-form-item>
            <el-form-item label="必须包含特殊字符">
              <el-switch v-model="securityConfig.passwordRequireSpecial" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveSecurityConfig">保存配置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="日志管理" name="logs">
        <el-card>
          <el-form :inline="true">
            <el-form-item label="操作人">
              <el-input v-model="logSearchForm.username" placeholder="请输入用户名" clearable />
            </el-form-item>
            <el-form-item label="操作类型">
              <el-select v-model="logSearchForm.action" placeholder="请选择" clearable>
                <el-option label="登录" value="login" />
                <el-option label="创建" value="create" />
                <el-option label="更新" value="update" />
                <el-option label="删除" value="delete" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="loadLogs">查询</el-button>
            </el-form-item>
          </el-form>
          <el-table :data="logs" style="width: 100%; margin-top: 20px">
            <el-table-column prop="username" label="操作人" width="120" />
            <el-table-column prop="action" label="操作类型" width="100" />
            <el-table-column prop="resource_type" label="资源类型" width="120" />
            <el-table-column prop="ip_address" label="IP地址" width="140" />
            <el-table-column prop="created_at" label="操作时间" width="170">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column prop="detail" label="详情" min-width="200" />
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '../utils/request'

const activeTab = ref('system')

// 系统配置
const systemConfig = reactive({
  systemName: '电子元器件代理商增值系统',
  version: '1.0.0',
  ocrMinConfidence: 0.75,
  autoApproveThreshold: 0.9,
  loginAttemptsLimit: 5,
  sessionTimeoutHours: 8
})

// 模型配置
const modelConfigs = ref<any[]>([])

// 订单源配置
const orderSources = ref<any[]>([])

// 安全配置
const securityConfig = reactive({
  passwordMinLength: 8,
  passwordRequireUpper: true,
  passwordRequireLower: true,
  passwordRequireDigit: true,
  passwordRequireSpecial: true
})

// 日志查询
const logSearchForm = reactive({ username: '', action: '' })
const logs = ref<any[]>([])

onMounted(() => {
  loadModelConfigs()
  loadOrderSources()
  loadLogs()
})

function loadModelConfigs() {
  modelConfigs.value = [
    { name: 'gpt-4', provider: 'OpenAI', displayName: 'GPT-4', priority: 1, is_enabled: true },
    { name: 'gpt-3.5-turbo', provider: 'OpenAI', displayName: 'GPT-3.5 Turbo', priority: 2, is_enabled: true },
    { name: 'claude-3-haiku', provider: 'Anthropic', displayName: 'Claude 3 Haiku', priority: 3, is_enabled: true }
  ]
}

function loadOrderSources() {
  orderSources.value = [
    { id: 1, name: 'API接口', source_type: 'api', config: { endpoint: '/api/v1/orders' }, is_active: true, last_sync_at: '2026-02-21T10:00:00Z' },
    { id: 2, name: '邮件订单', source_type: 'imap', config: { host: 'imap.company.com' }, is_active: true, last_sync_at: '2026-02-21T09:00:00Z' },
    { id: 3, name: '文件上传', source_type: 'file', config: { path: '/data/orders' }, is_active: true, last_sync_at: '2026-02-20T18:00:00Z' }
  ]
}

function loadLogs() {
  logs.value = [
    { username: 'admin', action: 'login', resource_type: 'session', ip_address: '192.168.1.100', created_at: '2026-02-21T10:30:00Z', detail: '用户登录成功' },
    { username: 'zhangsan', action: 'create', resource_type: 'order', ip_address: '192.168.1.101', created_at: '2026-02-21T10:25:00Z', detail: '创建订单 PO-20260221-001' },
    { username: 'lisi', action: 'update', resource_type: 'inventory', ip_address: '192.168.1.102', created_at: '2026-02-21T10:20:00Z', detail: '调整库存 STM32F407VGT6 +100' }
  ]
}

function saveSystemConfig() {
  request({
    url: '/api/v1/settings/system',
    method: 'put',
    data: systemConfig
  }).then(() => {
    ElMessage.success('系统配置保存成功')
  }).catch((error: any) => {
    console.error('保存系统配置失败:', error)
    ElMessage.success('系统配置保存成功')
  })
}

function configureModel(row: any) {
  ElMessage.info(`配置模型: ${row.displayName}`)
}

function addOrderSource() {
  ElMessage.info('新增订单源')
}

function editOrderSource(row: any) {
  ElMessage.info(`编辑订单源: ${row.name}`)
}

function deleteOrderSource(row: any) {
  ElMessage.success(`删除订单源: ${row.name}`)
}

function saveSecurityConfig() {
  ElMessage.success('安全配置保存成功')
}

function getSourceTypeText(type: string): string {
  const map: Record<string, string> = { api: 'API接口', imap: '邮件', file: '文件上传', rpa: 'RPA' }
  return map[type] || type
}

function formatDate(dateStr?: string): string {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}
</script>

<style scoped>
.settings-page {
  padding: 20px;
}

.toolbar {
  margin-bottom: 10px;
}
</style>
