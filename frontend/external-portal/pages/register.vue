<template>
  <div class="register-page">
    <!-- 顶部导航 -->
    <header class="site-header">
      <div class="container header-content">
        <div class="logo">
          <NuxtLink to="/">
            <span class="logo-text">元器件商城</span>
          </NuxtLink>
        </div>

        <nav class="main-nav">
          <NuxtLink to="/">首页</NuxtLink>
          <NuxtLink to="/products">产品中心</NuxtLink>
          <NuxtLink to="/about">关于我们</NuxtLink>
        </nav>

        <div class="header-actions">
          <span>已有账号？</span>
          <NuxtLink to="/login" class="btn btn-primary">登录</NuxtLink>
        </div>
      </div>
    </header>

    <!-- 主内容 -->
    <main class="main-content">
      <div class="container">
        <div class="register-card">
          <h1 class="page-title">注册新账号</h1>
          <p class="page-desc">填写以下信息，快速开启您的采购之旅</p>

          <el-form
            ref="formRef"
            :model="formData"
            :rules="formRules"
            class="register-form"
          >
            <!-- 用户名 -->
            <el-form-item prop="username">
              <el-input
                v-model="formData.username"
                placeholder="请输入用户名"
                size="large"
                clearable
              >
                <template #prefix>
                  <el-icon><User /></el-icon>
                </template>
              </el-input>
            </el-form-item>

            <!-- 手机号 -->
            <el-form-item prop="phone">
              <el-input
                v-model="formData.phone"
                placeholder="请输入手机号"
                size="large"
                maxlength="11"
              >
                <template #prefix>
                  <el-icon><Phone /></el-icon>
                </template>
                <template #append>
                  <el-button
                    :disabled="countdown > 0"
                    @click="sendCode"
                  >
                    {{ countdown > 0 ? `${countdown}s 后重发` : '获取验证码' }}
                  </el-button>
                </template>
              </el-input>
            </el-form-item>

            <!-- 验证码 -->
            <el-form-item prop="code">
              <el-input
                v-model="formData.code"
                placeholder="请输入验证码"
                size="large"
                maxlength="6"
              >
                <template #prefix>
                  <el-icon><Checked /></el-icon>
                </template>
              </el-input>
            </el-form-item>

            <!-- 密码 -->
            <el-form-item prop="password">
              <el-input
                v-model="formData.password"
                type="password"
                placeholder="请输入密码（8-20 位，包含字母和数字）"
                size="large"
                show-password
              >
                <template #prefix>
                  <el-icon><Lock /></el-icon>
                </template>
              </el-input>
            </el-form-item>

            <!-- 确认密码 -->
            <el-form-item prop="confirmPassword">
              <el-input
                v-model="formData.confirmPassword"
                type="password"
                placeholder="请确认密码"
                size="large"
                show-password
              >
                <template #prefix>
                  <el-icon><Lock /></el-icon>
                </template>
              </el-input>
            </el-form-item>

            <!-- 协议 -->
            <el-form-item prop="agree">
              <el-checkbox v-model="formData.agree" size="large">
                我已阅读并同意
                <el-link type="primary" :underline="false" @click="showProtocol('user')">
                  《用户服务协议》
                </el-link>
                和
                <el-link type="primary" :underline="false" @click="showProtocol('privacy')">
                  《隐私政策》
                </el-link>
              </el-checkbox>
            </el-form-item>

            <!-- 提交按钮 -->
            <el-form-item>
              <el-button
                type="primary"
                size="large"
                class="submit-btn"
                :loading="submitting"
                @click="handleSubmit"
              >
                {{ submitting ? '注册中...' : '立即注册' }}
              </el-button>
            </el-form-item>
          </el-form>

          <!-- 第三方登录 -->
          <div class="third-party">
            <div class="divider">
              <span>或使用以下方式注册</span>
            </div>
            <div class="third-party-icons">
              <el-tooltip content="微信快捷登录">
                <div class="third-icon">
                  <span>💚</span>
                </div>
              </el-tooltip>
              <el-tooltip content="支付宝快捷登录">
                <div class="third-icon">
                  <span>💙</span>
                </div>
              </el-tooltip>
              <el-tooltip content="企业微信">
                <div class="third-icon">
                  <span>🩵</span>
                </div>
              </el-tooltip>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- 底部 -->
    <footer class="site-footer">
      <div class="container">
        <div class="footer-content">
          <div class="footer-section">
            <h4>关于我们</h4>
            <p>专业的电子元器件供应商</p>
          </div>
          <div class="footer-section">
            <h4>快速链接</h4>
            <ul>
              <li><NuxtLink to="/products">产品中心</NuxtLink></li>
              <li><NuxtLink to="/about">关于我们</NuxtLink></li>
            </ul>
          </div>
          <div class="footer-section">
            <h4>联系方式</h4>
            <p>电话：400-xxx-xxxx</p>
            <p>邮箱：info@example.com</p>
          </div>
        </div>
        <div class="footer-bottom">
          <p>&copy; 2026 元器件商城。All rights reserved.</p>
        </div>
      </div>
    </footer>

    <!-- 协议弹窗 -->
    <el-dialog
      v-model="protocolVisible"
      :title="protocolTitle"
      width="600px"
    >
      <div class="protocol-content">
        <p>这里是{{ protocolTitle }}的详细内容...</p>
        <p>1. 服务条款一</p>
        <p>2. 服务条款二</p>
        <p>3. 服务条款三</p>
        <p>...</p>
      </div>
      <template #footer>
        <el-button @click="protocolVisible = false">取消</el-button>
        <el-button type="primary" @click="protocolVisible = false">同意</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { User, Phone, Checked, Lock } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { api } from '~/utils/api'
import { useRouter } from 'vue-router'

const router = useRouter()
const formRef = ref<FormInstance>()
const submitting = ref(false)
const countdown = ref(0)
const protocolVisible = ref(false)
const protocolTitle = ref('')

// 表单数据
const formData = ref({
  username: '',
  phone: '',
  code: '',
  password: '',
  confirmPassword: '',
  agree: false
})

// 表单验证规则
const formRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3-20 个字符', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { len: 6, message: '验证码为 6 位数字', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, max: 20, message: '密码长度在 8-20 位', trigger: 'blur' },
    { pattern: /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,20}$/, message: '密码需包含字母和数字', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== formData.value.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  agree: [
    {
      validator: (rule, value, callback) => {
        if (!value) {
          callback(new Error('请先同意用户服务协议和隐私政策'))
        } else {
          callback()
        }
      },
      trigger: 'change'
    }
  ]
}

// 发送验证码
async function sendCode() {
  if (!formData.value.phone || !/^1[3-9]\d{9}$/.test(formData.value.phone)) {
    alert('请输入正确的手机号')
    return
  }

  try {
    // TODO: 调用发送验证码 API
    await new Promise(resolve => setTimeout(resolve, 500))
    alert('验证码已发送')
    countdown.value = 60
    const timer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        clearInterval(timer)
      }
    }, 1000)
  } catch (error: any) {
    console.error('发送验证码失败:', error)
    alert('发送验证码失败，请稍后重试')
  }
}

// 显示协议
function showProtocol(type: string) {
  protocolVisible.value = true
  protocolTitle.value = type === 'user' ? '用户服务协议' : '隐私政策'
}

// 提交注册
async function handleSubmit() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true

    try {
      // TODO: 调用注册 API
      await api.register({
        username: formData.value.username,
        phone: formData.value.phone,
        code: formData.value.code,
        password: formData.value.password
      })

      alert('注册成功！')
      router.push('/login')
    } catch (error: any) {
      console.error('注册失败:', error)
      alert(error.message || '注册失败，请稍后重试')
    } finally {
      submitting.value = false
    }
  })
}

// SEO
useHead({
  title: '用户注册 - 元器件商城'
})
</script>

<style scoped>
.container {
  max-width: 500px;
  margin: 0 auto;
  padding: 0 20px;
}

/* 顶部导航 */
.site-header {
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 60px;
}

.logo-text {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
}

.main-nav {
  display: flex;
  gap: 30px;
}

.main-nav a {
  color: #333;
  text-decoration: none;
  font-size: 16px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  color: #666;
}

.btn {
  padding: 8px 20px;
  border-radius: 4px;
  text-decoration: none;
  font-size: 14px;
  cursor: pointer;
}

.btn-primary {
  background: #409eff;
  color: white;
  border: none;
}

/* 主内容区 */
.main-content {
  background: #f5f7fa;
  min-height: calc(100vh - 60px - 200px);
  padding: 40px 0;
}

/* 注册卡片 */
.register-card {
  background: white;
  border-radius: 8px;
  padding: 40px;
}

.page-title {
  font-size: 24px;
  color: #333;
  text-align: center;
  margin-bottom: 10px;
}

.page-desc {
  font-size: 14px;
  color: #999;
  text-align: center;
  margin-bottom: 30px;
}

/* 注册表单 */
.register-form {
  margin-bottom: 30px;
}

.register-form :deep(.el-input__wrapper) {
  padding: 12px 15px;
}

.register-form :deep(.el-input__inner) {
  font-size: 14px;
}

.register-form :deep(.el-form-item) {
  margin-bottom: 20px;
}

.submit-btn {
  width: 100%;
  height: 45px;
  font-size: 16px;
  font-weight: 600;
}

/* 第三方登录 */
.third-party {
  text-align: center;
}

.divider {
  position: relative;
  margin-bottom: 25px;
}

.divider::before {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  top: 50%;
  height: 1px;
  background: #eee;
}

.divider span {
  position: relative;
  background: white;
  padding: 0 15px;
  font-size: 12px;
  color: #999;
}

.third-party-icons {
  display: flex;
  justify-content: center;
  gap: 20px;
}

.third-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  cursor: pointer;
  transition: all 0.2s;
}

.third-icon:hover {
  background: #ecf5ff;
  transform: scale(1.1);
}

/* 协议内容 */
.protocol-content {
  max-height: 400px;
  overflow-y: auto;
  font-size: 14px;
  line-height: 1.8;
  color: #666;
}

.protocol-content p {
  margin-bottom: 10px;
}

/* 底部 */
.site-footer {
  background: #2c3e50;
  color: white;
  padding: 40px 0 20px;
}

.footer-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 30px;
  margin-bottom: 30px;
}

.footer-bottom {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}
</style>
