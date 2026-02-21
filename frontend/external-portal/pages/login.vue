<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-box">
        <div class="login-header">
          <h1>用户登录</h1>
          <p>欢迎来到元器件商城</p>
        </div>

        <el-form
          ref="formRef"
          :model="loginForm"
          :rules="formRules"
          class="login-form"
          @keyup.enter="handleLogin"
        >
          <el-form-item prop="username">
            <el-input
              v-model="loginForm.username"
              placeholder="请输入用户名/手机号"
              prefix-icon="User"
              size="large"
            />
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              prefix-icon="Lock"
              size="large"
              show-password
            />
          </el-form-item>

          <div class="form-options">
            <el-checkbox v-model="loginForm.remember">记住我</el-checkbox>
            <el-link type="primary" :underline="false">忘记密码？</el-link>
          </div>

          <el-form-item>
            <el-button
              type="primary"
              size="large"
              :loading="loading"
              class="login-btn"
              @click="handleLogin"
            >
              登录
            </el-button>
          </el-form-item>

          <div class="login-divider">
            <span>其他登录方式</span>
          </div>

          <div class="social-login">
            <el-button circle class="social-btn">
              <el-icon><IEpWechat /></el-icon>
            </el-button>
            <el-button circle class="social-btn">
              <el-icon><IEpQRCode /></el-icon>
            </el-button>
          </div>

          <div class="login-footer">
            还没有账号？
            <NuxtLink to="/register" class="register-link">立即注册</NuxtLink>
          </div>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { User, Lock, IEpWechat, IEpQRCode } from '@element-plus/icons-vue'
import { useUserStore } from '~/stores/user'

interface LoginForm {
  username: string
  password: string
  remember: boolean
}

const router = useRouter()
const userStore = useUserStore()
const formRef = ref()
const loading = ref(false)

const loginForm = ref<LoginForm>({
  username: '',
  password: '',
  remember: false
})

const formRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少 6 位', trigger: 'blur' }
  ]
}

async function handleLogin() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid: boolean) => {
    if (!valid) return

    loading.value = true
    const result = await userStore.login({
      username: loginForm.value.username,
      password: loginForm.value.password
    })

    if (result.success) {
      // 登录成功后跳转到首页
      router.push('/')
    } else {
      // 显示错误消息
      alert(result.message)
    }
    loading.value = false
  })
}

// SEO
useHead({
  title: '用户登录 - 元器件商城'
})
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-container {
  width: 100%;
  max-width: 420px;
  padding: 20px;
}

.login-box {
  background: white;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h1 {
  font-size: 28px;
  color: #333;
  margin-bottom: 10px;
}

.login-header p {
  font-size: 14px;
  color: #999;
}

.login-form {
  width: 100%;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.login-btn {
  width: 100%;
}

.login-divider {
  position: relative;
  text-align: center;
  margin: 25px 0;
}

.login-divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: #e6e6e6;
}

.login-divider span {
  position: relative;
  background: white;
  padding: 0 15px;
  color: #999;
  font-size: 14px;
}

.social-login {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 25px;
}

.social-btn {
  width: 50px;
  height: 50px;
  border: 1px solid #e6e6e6;
}

.social-btn:hover {
  border-color: #409eff;
  color: #409eff;
}

.login-footer {
  text-align: center;
  color: #666;
  font-size: 14px;
}

.register-link {
  color: #409eff;
  text-decoration: none;
  font-weight: 500;
}

.register-link:hover {
  text-decoration: underline;
}
</style>
