import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios'

// 响应接口
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

// 用户登录请求
export interface LoginRequest {
  username: string
  password: string
}

// 用户注册请求
export interface RegisterRequest {
  username: string
  phone: string
  code: string
  password: string
}

// 用户登录响应
export interface LoginResponse {
  access_token: string
  token_type: string
  expires_in: number
  user_id: string
  username: string
  role: string
}

// 用户信息
export interface UserInfo {
  id: string
  username: string
  email: string
  full_name: string
  phone?: string
  avatar?: string
  role: string
}

// 产品列表响应
export interface Product {
  id: string
  mpn: string
  manufacturer: string
  description: string
  category: string
  package: string
  price: number
  stock: number
  datasheet_url?: string
  image_url?: string
}

export interface ProductListResponse {
  total: number
  page: number
  page_size: number
  products: Product[]
}

// 购物车项
export interface CartItem {
  id: string
  product_id: string
  quantity: number
  product: Product
}

// 订单项
export interface OrderItem {
  id: string
  product_id: string
  product_name: string
  mpn: string
  quantity: number
  unit_price: number
  total_price: number
}

// 订单
export interface Order {
  id: string
  order_number: string
  customer_name: string
  total_amount: number
  status: string
  created_at: string
  items: OrderItem[]
}

class ApiClient {
  private client: AxiosInstance
  private baseURL: string

  constructor(baseURL: string) {
    this.baseURL = baseURL
    this.client = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    })

    // 请求拦截器
    this.client.interceptors.request.use(
      (config) => {
        const token = this.getToken()
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        // CSRF Token
        const csrfToken = this.getCSRFToken()
        if (csrfToken) {
          config.headers['X-CSRF-Token'] = csrfToken
        }
        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    // 响应拦截器
    this.client.interceptors.response.use(
      (response) => {
        return response
      },
      (error: AxiosError<ApiResponse>) => {
        if (error.response?.status === 401) {
          this.handleUnauthorized()
        } else if (error.response?.status === 403) {
          this.handleForbidden()
        }
        return Promise.reject(error)
      }
    )
  }

  // Token 管理
  private setToken(token: string): void {
    localStorage.setItem('access_token', token)
  }

  private getToken(): string | null {
    return localStorage.getItem('access_token')
  }

  private removeToken(): void {
    localStorage.removeItem('access_token')
  }

  // CSRF Token 管理
  private getCSRFToken(): string | null {
    return document.cookie
      .split('; ')
      .find(row => row.startsWith('csrf_token='))
      ?.split('=')[1] || null
  }

  // 错误处理
  private handleUnauthorized(): void {
    this.removeToken()
    window.location.href = '/login'
  }

  private handleForbidden(): void {
    console.error('没有权限访问此资源')
  }

  // 通用请求方法
  async request<T>(config: AxiosRequestConfig): Promise<ApiResponse<T>> {
    const response: AxiosResponse<ApiResponse<T>> = await this.client.request(config)
    return response.data
  }

  // 认证 API
  async login(data: LoginRequest): Promise<ApiResponse<LoginResponse>> {
    const response = await this.client.post<ApiResponse<LoginResponse>>('/api/v1/login', data)
    if (response.data.data.access_token) {
      this.setToken(response.data.data.access_token)
    }
    return response.data
  }

  async register(data: RegisterRequest): Promise<ApiResponse<LoginResponse>> {
    const response = await this.client.post<ApiResponse<LoginResponse>>('/api/v1/register', data)
    if (response.data.data.access_token) {
      this.setToken(response.data.data.access_token)
    }
    return response.data
  }

  async logout(): Promise<ApiResponse<void>> {
    this.removeToken()
    return this.client.post<ApiResponse<void>>('/api/v1/logout')
  }

  async getUserInfo(): Promise<ApiResponse<UserInfo>> {
    return this.client.get<ApiResponse<UserInfo>>('/api/v1/profile')
  }

  // 产品 API
  async getProducts(params?: {
    page?: number
    page_size?: number
    keyword?: string
    category?: string
    manufacturer?: string
    price_min?: number
    price_max?: number
  }): Promise<ApiResponse<ProductListResponse>> {
    return this.client.get<ApiResponse<ProductListResponse>>('/api/v1/products', { params })
  }

  async getProduct(id: string): Promise<ApiResponse<Product>> {
    return this.client.get<ApiResponse<Product>>(`/api/v1/products/${id}`)
  }

  async searchProducts(keyword: string): Promise<ApiResponse<Product[]>> {
    return this.client.get<ApiResponse<Product[]>>('/api/v1/products/search', {
      params: { keyword }
    })
  }

  // 购物车 API
  async getCart(): Promise<ApiResponse<CartItem[]>> {
    return this.client.get<ApiResponse<CartItem[]>>('/api/v1/cart')
  }

  async addToCart(productId: string, quantity: number): Promise<ApiResponse<CartItem>> {
    return this.client.post<ApiResponse<CartItem>>('/api/v1/cart', { product_id: productId, quantity })
  }

  async updateCartItem(itemId: string, quantity: number): Promise<ApiResponse<CartItem>> {
    return this.client.put<ApiResponse<CartItem>>(`/api/v1/cart/${itemId}`, { quantity })
  }

  async deleteCartItem(itemId: string): Promise<ApiResponse<void>> {
    return this.client.delete<ApiResponse<void>>(`/api/v1/cart/${itemId}`)
  }

  async clearCart(): Promise<ApiResponse<void>> {
    return this.client.delete<ApiResponse<void>>('/api/v1/cart/clear')
  }

  // 订单 API
  async getOrders(params?: {
    page?: number
    page_size?: number
    status?: string
  }): Promise<ApiResponse<Order[]>> {
    return this.client.get<ApiResponse<Order[]>>('/api/v1/orders', { params })
  }

  async getOrder(id: string): Promise<ApiResponse<Order>> {
    return this.client.get<ApiResponse<Order>>(`/api/v1/orders/${id}`)
  }

  async createOrder(data: {
    items: { product_id: string; quantity: number }[]
    shipping_address: string
    phone: string
  }): Promise<ApiResponse<Order>> {
    return this.client.post<ApiResponse<Order>>('/api/v1/orders', data)
  }

  async cancelOrder(id: string): Promise<ApiResponse<Order>> {
    return this.client.post<ApiResponse<Order>>(`/api/v1/orders/${id}/cancel`)
  }
}

// 导出单例
const apiBase = import.meta.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8001'
export const api = new ApiClient(apiBase)

// 导出工具函数
export function isAuthenticated(): boolean {
  return !!localStorage.getItem('access_token')
}

export function getToken(): string | null {
  return localStorage.getItem('access_token')
}
