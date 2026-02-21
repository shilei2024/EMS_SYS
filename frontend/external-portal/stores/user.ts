import { defineStore } from 'pinia'
import type { UserInfo, LoginRequest } from '~/utils/api'
import { api, isAuthenticated } from '~/utils/api'

interface UserState {
  userInfo: UserInfo | null
  token: string | null
  isAuthenticated: boolean
  loading: boolean
}

export const useUserStore = defineStore('user', {
  state: (): UserState => ({
    userInfo: null,
    token: null,
    isAuthenticated: false,
    loading: false
  }),

  getters: {
    username: (state) => state.userInfo?.username || '游客',
    fullName: (state) => state.userInfo?.full_name || state.userInfo?.username || '游客',
    email: (state) => state.userInfo?.email || '',
    avatar: (state) => state.userInfo?.avatar || '',
    role: (state) => state.userInfo?.role || 'user'
  },

  actions: {
    // 初始化用户状态
    async initUser() {
      if (isAuthenticated()) {
        try {
          const res = await api.getUserInfo()
          this.userInfo = res.data
          this.token = api.getToken()
          this.isAuthenticated = true
        } catch (error) {
          console.error('获取用户信息失败:', error)
          this.logout()
        }
      }
    },

    // 登录
    async login(credentials: LoginRequest) {
      this.loading = true
      try {
        const res = await api.login(credentials)
        this.userInfo = {
          id: res.data.user_id,
          username: res.data.username,
          email: '',
          full_name: res.data.username,
          role: res.data.role
        }
        this.token = res.data.access_token
        this.isAuthenticated = true
        return { success: true }
      } catch (error: any) {
        console.error('登录失败:', error)
        return {
          success: false,
          message: error.response?.data?.message || '登录失败，请检查用户名和密码'
        }
      } finally {
        this.loading = false
      }
    },

    // 登出
    async logout() {
      try {
        await api.logout()
      } catch (error) {
        console.error('登出失败:', error)
      } finally {
        this.userInfo = null
        this.token = null
        this.isAuthenticated = false
      }
    },

    // 更新用户信息
    updateUser(info: Partial<UserInfo>) {
      if (this.userInfo) {
        this.userInfo = { ...this.userInfo, ...info }
      }
    }
  }
})
