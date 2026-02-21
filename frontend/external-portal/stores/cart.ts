import { defineStore } from 'pinia'
import type { CartItem, Product } from '~/utils/api'
import { api } from '~/utils/api'

interface CartState {
  items: CartItem[]
  loading: boolean
  total: number
}

export const useCartStore = defineStore('cart', {
  state: (): CartState => ({
    items: [],
    loading: false,
    total: 0
  }),

  getters: {
    count: (state) => state.items.reduce((sum, item) => sum + item.quantity, 0),
    itemCount: (state) => state.items.length,
    totalPrice: (state) => {
      return state.items.reduce((sum, item) => sum + item.product.price * item.quantity, 0)
    },
    hasItems: (state) => state.items.length > 0
  },

  actions: {
    // 加载购物车
    async loadCart() {
      this.loading = true
      try {
        const res = await api.getCart()
        this.items = res.data
        this.total = this.totalPrice
      } catch (error: any) {
        console.error('加载购物车失败:', error)
        // 使用本地购物车
        this.loadLocalCart()
      } finally {
        this.loading = false
      }
    },

    // 加载本地购物车
    loadLocalCart() {
      const localCart = localStorage.getItem('cart')
      if (localCart) {
        this.items = JSON.parse(localCart)
        this.total = this.totalPrice
      }
    },

    // 添加商品项（供产品详情页使用）
    async addItem(productId: string, quantity: number) {
      this.loading = true
      try {
        const res = await api.addToCart(productId, quantity)
        const productRes = await api.getProduct(productId)
        const existingItem = this.items.find(item => item.product_id === productId)
        if (existingItem) {
          existingItem.quantity += quantity
        } else {
          this.items.push({
            id: res.data.id,
            product_id: productId,
            quantity,
            product: productRes.data
          })
        }
        this.saveLocalCart()
        return { success: true }
      } catch (error: any) {
        console.error('添加到购物车失败，使用本地购物车:', error)
        // 降级到本地购物车
        const existingItem = this.items.find(item => item.product_id === productId)
        if (existingItem) {
          existingItem.quantity += quantity
        } else {
          // 本地购物车需要产品数据，这里使用一个临时对象
          this.items.push({
            id: Date.now().toString(),
            product_id: productId,
            quantity,
            product: {
              id: productId,
              mpn: productId,
              manufacturer: 'Unknown',
              description: '',
              category: '',
              package: '',
              price: 0,
              stock: 0
            } as Product
          })
        }
        this.saveLocalCart()
        return { success: true }
      } finally {
        this.loading = false
      }
    },

    // 更新购物车项
    async updateQuantity(itemId: string, quantity: number) {
      if (quantity <= 0) {
        return this.removeFromCart(itemId)
      }

      try {
        await api.updateCartItem(itemId, quantity)
      } catch (error) {
        console.error('更新购物车失败:', error)
      }

      const item = this.items.find(item => item.id === itemId)
      if (item) {
        item.quantity = quantity
        this.saveLocalCart()
      }
    },

    // 从购物车移除
    async removeFromCart(itemId: string) {
      try {
        await api.deleteCartItem(itemId)
      } catch (error) {
        console.error('删除购物车项失败:', error)
        // 本地删除
      }

      this.items = this.items.filter(item => item.id !== itemId)
      this.saveLocalCart()
    },

    // 清空购物车
    async clearCart() {
      try {
        await api.clearCart()
      } catch (error) {
        console.error('清空购物车失败:', error)
      }

      this.items = []
      this.saveLocalCart()
    },

    // 保存本地购物车
    saveLocalCart() {
      localStorage.setItem('cart', JSON.stringify(this.items))
      this.total = this.totalPrice
    }
  }
})
