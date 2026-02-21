<template>
  <div class="profile-page">
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
          <NuxtLink to="/contact">联系我们</NuxtLink>
        </nav>

        <div class="header-actions">
          <NuxtLink to="/cart" class="btn btn-outline">
            <el-icon><ShoppingCart /></el-icon>
            购物车
          </NuxtLink>
          <NuxtLink to="/profile" class="btn btn-primary">个人中心</NuxtLink>
        </div>
      </div>
    </header>

    <!-- 主要内容 -->
    <main class="main-content">
      <div class="container">
        <h1 class="page-title">个人中心</h1>

        <div class="profile-layout">
          <!-- 侧边栏 -->
          <aside class="sidebar">
            <div class="user-card">
              <div class="avatar">
                <el-avatar :size="80" :src="userStore.avatar">
                  <span class="avatar-text">{{ userStore.fullName.charAt(0) }}</span>
                </el-avatar>
              </div>
              <h3 class="username">{{ userStore.fullName }}</h3>
              <p class="user-email">{{ userStore.email || '未设置邮箱' }}</p>
            </div>

            <div class="sidebar-menu">
              <a class="menu-item active">
                <el-icon><User /></el-icon>
                个人信息
              </a>
              <NuxtLink to="/orders" class="menu-item">
                <el-icon><Document /></el-icon>
                我的订单
              </NuxtLink>
              <NuxtLink to="/addresses" class="menu-item">
                <el-icon><Location /></el-icon>
                地址管理
              </NuxtLink>
              <div class="menu-divider"></div>
              <button class="menu-item logout" @click="handleLogout">
                <el-icon><SwitchButton /></el-icon>
                退出登录
              </button>
            </div>
          </aside>

          <!-- 个人信息表单 -->
          <div class="profile-content">
            <el-tabs v-model="activeTab">
              <el-tab-pane label="基本信息" name="profile">
                <el-form
                  ref="profileFormRef"
                  :model="profileForm"
                  :rules="profileRules"
                  label-width="100px"
                >
                  <el-form-item label="用户名" prop="username">
                    <el-input v-model="profileForm.username" disabled />
                  </el-form-item>
                  <el-form-item label="邮箱" prop="email">
                    <el-input v-model="profileForm.email" />
                  </el-form-item>
                  <el-form-item label="手机号" prop="phone">
                    <el-input v-model="profileForm.phone" placeholder="请输入手机号" />
                  </el-form-item>
                  <el-form-item label="姓名" prop="full_name">
                    <el-input v-model="profileForm.full_name" placeholder="请输入姓名" />
                  </el-form-item>
                  <el-form-item>
                    <el-button type="primary" @click="saveProfile" :loading="savingProfile">
                      保存修改
                    </el-button>
                  </el-form-item>
                </el-form>
              </el-tab-pane>

              <el-tab-pane label="账户安全" name="security">
                <el-form
                  ref="passwordFormRef"
                  :model="passwordForm"
                  :rules="passwordRules"
                  label-width="100px"
                >
                  <el-form-item label="当前密码" prop="old_password">
                    <el-input
                      v-model="passwordForm.old_password"
                      type="password"
                      placeholder="请输入当前密码"
                      show-password
                    />
                  </el-form-item>
                  <el-form-item label="新密码" prop="new_password">
                    <el-input
                      v-model="passwordForm.new_password"
                      type="password"
                      placeholder="请输入新密码"
                      show-password
                    />
                  </el-form-item>
                  <el-form-item label="确认密码" prop="confirm_password">
                    <el-input
                      v-model="passwordForm.confirm_password"
                      type="password"
                      placeholder="请再次输入新密码"
                      show-password
                    />
                  </el-form-item>
                  <el-form-item>
                    <el-button type="primary" @click="changePassword" :loading="savingPassword">
                      修改密码
                    </el-button>
                  </el-form-item>
                </el-form>
              </el-tab-pane>
            </el-tabs>
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
  </div>
</template>

<script setup lang="ts">
import { User, Document, Location, SwitchButton, ShoppingCart } from '@element-plus/icons-vue'
import { useUserStore } from '~/stores/user'
import { api } from '~/utils/api'
import type { FormInstance, FormRules } from 'element-plus'

const userStore = useUserStore()
const router = useRouter()

const activeTab = ref('profile')
const savingProfile = ref(false)
const savingPassword = ref(false)

const profileFormRef = ref<FormInstance>()
const passwordFormRef = ref<FormInstance>()

const profileForm = ref({
  username: userStore.username,
  email: userStore.email || '',
  phone: '',
  full_name: userStore.fullName
})

const passwordForm = ref({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const profileRules: FormRules = {
  email: [
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ]
}

const passwordRules: FormRules = {
  old_password: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少 6 位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value && value !== passwordForm.value.new_password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

async function saveProfile() {
  if (!profileFormRef.value) return
  await profileFormRef.value.validate(async (valid) => {
    if (!valid) return

    savingProfile.value = true
    try {
      // TODO: 调用保存个人信息 API
      await new Promise(resolve => setTimeout(resolve, 1000))
      userStore.updateUser(profileForm.value)
      alert('保存成功')
    } catch (error: any) {
      console.error('保存失败:', error)
      alert('保存失败')
    } finally {
      savingProfile.value = false
    }
  })
}

async function changePassword() {
  if (!passwordFormRef.value) return
  await passwordFormRef.value.validate(async (valid) => {
    if (!valid) return

    savingPassword.value = true
    try {
      // TODO: 调用修改密码 API
      await new Promise(resolve => setTimeout(resolve, 1000))
      alert('密码修改成功，请重新登录')
      passwordForm.value = { old_password: '', new_password: '', confirm_password: '' }
      await userStore.logout()
      router.push('/login')
    } catch (error: any) {
      console.error('修改密码失败:', error)
      alert('修改密码失败')
    } finally {
      savingPassword.value = false
    }
  })
}

async function handleLogout() {
  await userStore.logout()
  router.push('/')
}

// SEO
useHead({
  title: '个人中心 - 元器件商城'
})
</script>

<style scoped>
.container {
  max-width: 1200px;
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
  gap: 15px;
  align-items: center;
}

.btn {
  padding: 8px 20px;
  border-radius: 4px;
  text-decoration: none;
  font-size: 14px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.btn-outline {
  border: 1px solid #409eff;
  color: #409eff;
  background: white;
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
  padding: 30px 0;
}

.page-title {
  font-size: 28px;
  color: #333;
  margin-bottom: 25px;
}

.profile-layout {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 25px;
}

/* 侧边栏 */
.sidebar {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.user-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  padding: 30px;
  text-align: center;
  color: white;
}

.avatar {
  margin-bottom: 15px;
}

.avatar-text {
  font-size: 32px;
  font-weight: 600;
}

.username {
  font-size: 18px;
  margin-bottom: 5px;
}

.user-email {
  font-size: 14px;
  opacity: 0.8;
}

.sidebar-menu {
  background: white;
  border-radius: 8px;
  padding: 20px 0;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 20px;
  color: #333;
  text-decoration: none;
  transition: background 0.2s;
  border: none;
  background: none;
  width: 100%;
  text-align: left;
  cursor: pointer;
  font-size: 14px;
}

.menu-item:hover {
  background: #f5f7fa;
}

.menu-item.active {
  background: #ecf5ff;
  color: #409eff;
}

.menu-divider {
  height: 1px;
  background: #eee;
  margin: 10px 0;
}

.menu-item.logout {
  color: #f56c6c;
}

/* 个人信息内容区 */
.profile-content {
  background: white;
  border-radius: 8px;
  padding: 25px;
}

.el-form {
  max-width: 500px;
  margin-top: 20px;
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
