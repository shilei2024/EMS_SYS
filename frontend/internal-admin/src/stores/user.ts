import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login, logout, getUserInfo } from '../api/auth'
import router from '../router'

interface UserInfo {
  id: string
  username: string
  email: string
  fullName: string
  role: string
  department?: string
}

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref<UserInfo | null>(null)

  const isAuthenticated = computed(() => !!token.value)

  async function loginAction(username: string, password: string) {
    try {
      const res = await login(username, password)
      token.value = res.access_token
      localStorage.setItem('token', res.access_token)

      // 获取用户信息
      await fetchUserInfo()

      return res
    } catch (error) {
      throw error
    }
  }

  async function fetchUserInfo() {
    try {
      const res = await getUserInfo()
      userInfo.value = res
    } catch (error) {
      console.error('获取用户信息失败', error)
    }
  }

  async function logoutAction() {
    try {
      await logout()
    } catch (error) {
      console.error('登出失败', error)
    } finally {
      token.value = ''
      userInfo.value = null
      localStorage.removeItem('token')
      router.push('/login')
    }
  }

  function hasPermission(permission: string): boolean {
    if (!userInfo.value) return false
    // 简化权限检查
    return true
  }

  return {
    token,
    userInfo,
    isAuthenticated,
    loginAction,
    logoutAction,
    fetchUserInfo,
    hasPermission
  }
})
