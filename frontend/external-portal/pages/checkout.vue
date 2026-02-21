<template>
  <div class="checkout-page">
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
          <NuxtLink to="/cart" class="cart-link">
            <span class="cart-icon">🛒</span>
            <span class="cart-count" v-if="cartCount > 0">{{ cartCount }}</span>
          </NuxtLink>
        </div>
      </div>
    </header>

    <!-- 主内容 -->
    <main class="main-content">
      <div class="container">
        <h1 class="page-title">结算订单</h1>

        <div class="checkout-content">
          <!-- 左侧：表单 -->
          <div class="checkout-form">
            <!-- 收货地址 -->
            <section class="form-section">
              <h2 class="section-title">收货地址</h2>
              <div class="address-form">
                <div class="form-row">
                  <div class="form-group">
                    <label>收件人姓名</label>
                    <input
                      v-model="formData.contactName"
                      type="text"
                      placeholder="请输入收件人姓名"
                    />
                  </div>
                  <div class="form-group">
                    <label>手机号码</label>
                    <input
                      v-model="formData.phone"
                      type="tel"
                      placeholder="请输入手机号码"
                    />
                  </div>
                </div>
                <div class="form-row">
                  <div class="form-group full-width">
                    <label>所在地区</label>
                    <div class="region-select">
                      <select v-model="formData.province">
                        <option value="">请选择省份</option>
                        <option value="beijing">北京市</option>
                        <option value="shanghai">上海市</option>
                        <option value="guangdong">广东省</option>
                        <option value="jiangsu">江苏省</option>
                        <option value="zhejiang">浙江省</option>
                      </select>
                      <select v-model="formData.city">
                        <option value="">请选择城市</option>
                        <option value="beijing">北京市</option>
                        <option value="shanghai">上海市</option>
                        <option value="guangzhou">广州市</option>
                        <option value="shenzhen">深圳市</option>
                        <option value="nanjing">南京市</option>
                        <option value="hangzhou">杭州市</option>
                      </select>
                      <select v-model="formData.district">
                        <option value="">请选择区县</option>
                        <option value="chaoyang">朝阳区</option>
                        <option value="haidian">海淀区</option>
                        <option value="pudong">浦东新区</option>
                      </select>
                    </div>
                  </div>
                </div>
                <div class="form-row">
                  <div class="form-group full-width">
                    <label>详细地址</label>
                    <input
                      v-model="formData.address"
                      type="text"
                      placeholder="请输入详细地址，如：XX 路 XX 号 XX 大厦"
                    />
                  </div>
                </div>
              </div>
            </section>

            <!-- 支付方式 -->
            <section class="form-section">
              <h2 class="section-title">支付方式</h2>
              <div class="payment-methods">
                <label class="payment-option" :class="{ selected: paymentMethod === 'alipay' }">
                  <input type="radio" v-model="paymentMethod" value="alipay" />
                  <div class="payment-icon">💳</div>
                  <span>支付宝</span>
                </label>
                <label class="payment-option" :class="{ selected: paymentMethod === 'wechat' }">
                  <input type="radio" v-model="paymentMethod" value="wechat" />
                  <div class="payment-icon">📱</div>
                  <span>微信支付</span>
                </label>
                <label class="payment-option" :class="{ selected: paymentMethod === 'bank' }">
                  <input type="radio" v-model="paymentMethod" value="bank" />
                  <div class="payment-icon">🏦</div>
                  <span>银行转账</span>
                </label>
              </div>
            </section>

            <!-- 发票信息 -->
            <section class="form-section">
              <h2 class="section-title">发票信息</h2>
              <div class="invoice-option">
                <label>
                  <input type="checkbox" v-model="needInvoice" />
                  需要发票
                </label>
                <div v-if="needInvoice" class="invoice-form">
                  <div class="form-group">
                    <label>发票抬头</label>
                    <input
                      v-model="invoiceTitle"
                      type="text"
                      placeholder="请输入发票抬头"
                    />
                  </div>
                  <div class="form-group">
                    <label>税号</label>
                    <input
                      v-model="taxId"
                      type="text"
                      placeholder="请输入税号"
                    />
                  </div>
                </div>
              </div>
            </section>

            <!-- 订单备注 -->
            <section class="form-section">
              <h2 class="section-title">订单备注</h2>
              <div class="form-group">
                <textarea
                  v-model="remark"
                  placeholder="请输入订单备注，如：送货时间要求等"
                  rows="3"
                ></textarea>
              </div>
            </section>
          </div>

          <!-- 右侧：订单摘要 -->
          <div class="order-summary">
            <h2 class="summary-title">订单摘要</h2>

            <!-- 商品列表 -->
            <div class="summary-items">
              <div
                v-for="item in cartStore.items"
                :key="item.id"
                class="summary-item"
              >
                <div class="item-info">
                  <span class="item-name">{{ item.product.mpn }}</span>
                  <span class="item-quantity">x{{ item.quantity }}</span>
                </div>
                <div class="item-price">¥{{ (item.product.price * item.quantity).toFixed(2) }}</div>
              </div>
            </div>

            <!-- 金额汇总 -->
            <div class="summary-totals">
              <div class="summary-row">
                <span>商品总额：</span>
                <span class="amount">¥{{ cartStore.totalPrice.toFixed(2) }}</span>
              </div>
              <div class="summary-row">
                <span>运费：</span>
                <span class="amount">¥{{ shippingFee.toFixed(2) }}</span>
              </div>
              <div class="summary-row discount" v-if="discountAmount > 0">
                <span>优惠：</span>
                <span class="amount">-¥{{ discountAmount.toFixed(2) }}</span>
              </div>
              <div class="summary-row total">
                <span>应付总额：</span>
                <span class="amount total-amount">¥{{ totalAmount.toFixed(2) }}</span>
              </div>
            </div>

            <!-- 提交订单 -->
            <button
              class="btn-submit"
              @click="submitOrder"
              :disabled="submitting || !isFormValid"
            >
              <span v-if="submitting">提交中...</span>
              <span v-else>提交订单</span>
            </button>

            <!-- 返回购物车 -->
            <NuxtLink to="/cart" class="btn-back">返回购物车</NuxtLink>
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
import { useCartStore } from '~/stores/cart'
import { api } from '~/utils/api'

const router = useRouter()
const cartStore = useCartStore()

// 表单数据
const formData = ref({
  contactName: '',
  phone: '',
  province: '',
  city: '',
  district: '',
  address: ''
})

const paymentMethod = ref('alipay')
const needInvoice = ref(false)
const invoiceTitle = ref('')
const taxId = ref('')
const remark = ref('')

// 提交状态
const submitting = ref(false)

// 计算属性
const shippingFee = computed(() => {
  // 满 100 包邮
  return cartStore.totalPrice >= 100 ? 0 : 10
})

const discountAmount = computed(() => 0)

const totalAmount = computed(() => {
  return cartStore.totalPrice + shippingFee.value - discountAmount.value
})

const isFormValid = computed(() => {
  return (
    formData.value.contactName.trim() &&
    formData.value.phone.trim() &&
    formData.value.province &&
    formData.value.city &&
    formData.value.address.trim()
  )
})

const cartCount = computed(() => cartStore.count)

// 提交订单
async function submitOrder() {
  if (!isFormValid.value) {
    alert('请填写完整的收货地址')
    return
  }

  if (cartStore.items.length === 0) {
    alert('购物车是空的')
    router.push('/products')
    return
  }

  submitting.value = true

  try {
    // 构建订单项
    const items = cartStore.items.map(item => ({
      product_id: item.product_id,
      quantity: item.quantity
    }))

    // 调用 API 创建订单
    const response = await api.createOrder({
      items,
      shipping_address: `${formData.value.province}${formData.value.city}${formData.value.district}${formData.value.address}`,
      phone: formData.value.phone
    })

    // 清空购物车
    await cartStore.clearCart()

    // 跳转到订单详情页或成功页
    alert('订单提交成功！')
    router.push(`/orders/${response.data.id}`)
  } catch (error: any) {
    console.error('提交订单失败:', error)
    alert('提交订单失败，请稍后重试')
  } finally {
    submitting.value = false
  }
}

// SEO
useHead({
  title: '结算订单 - 元器件商城'
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
  align-items: center;
  gap: 20px;
}

.cart-link {
  position: relative;
  font-size: 24px;
  text-decoration: none;
}

.cart-count {
  position: absolute;
  top: -8px;
  right: -8px;
  background: #f56c6c;
  color: white;
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 16px;
  text-align: center;
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

/* 结算内容 */
.checkout-content {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 25px;
}

/* 表单区域 */
.checkout-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-section {
  background: white;
  padding: 25px;
  border-radius: 8px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

/* 地址表单 */
.address-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.form-group input,
.form-group select {
  padding: 10px 15px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
}

.form-group input:focus,
.form-group select:focus {
  border-color: #409eff;
  outline: none;
}

.region-select {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 10px;
}

/* 支付方式 */
.payment-methods {
  display: flex;
  gap: 20px;
}

.payment-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 30px;
  border: 2px solid #eee;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.payment-option:hover {
  border-color: #409eff;
}

.payment-option.selected {
  border-color: #409eff;
  background: #ecf5ff;
}

.payment-option input {
  display: none;
}

.payment-icon {
  font-size: 32px;
  margin-bottom: 10px;
}

.payment-option span {
  font-size: 14px;
  color: #333;
}

/* 发票信息 */
.invoice-option {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.invoice-form {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 4px;
}

/* 订单摘要 */
.order-summary {
  background: white;
  padding: 25px;
  border-radius: 8px;
  height: fit-content;
}

.summary-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

/* 商品列表 */
.summary-items {
  display: flex;
  flex-direction: column;
  gap: 15px;
  max-height: 300px;
  overflow-y: auto;
  margin-bottom: 20px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.summary-item:last-child {
  border-bottom: none;
}

.item-info {
  display: flex;
  gap: 10px;
  align-items: center;
}

.item-name {
  font-size: 14px;
  color: #333;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-quantity {
  font-size: 12px;
  color: #999;
}

.item-price {
  font-size: 14px;
  color: #f56c6c;
  font-weight: 600;
}

/* 金额汇总 */
.summary-totals {
  background: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 20px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  font-size: 14px;
}

.summary-row .amount {
  font-weight: 600;
  color: #333;
}

.summary-row.discount .amount {
  color: #f56c6c;
}

.summary-row.total {
  border-top: 1px solid #ddd;
  padding-top: 10px;
  margin-bottom: 0;
  font-size: 16px;
}

.summary-row.total .amount {
  font-size: 20px;
  color: #f56c6c;
}

/* 提交按钮 */
.btn-submit {
  width: 100%;
  padding: 15px;
  background: #f56c6c;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  margin-bottom: 15px;
}

.btn-submit:hover:not(:disabled) {
  background: #f78989;
}

.btn-submit:disabled {
  background: #dcdfe6;
  cursor: not-allowed;
}

.btn-back {
  display: block;
  text-align: center;
  padding: 12px;
  border: 1px solid #409eff;
  color: #409eff;
  background: white;
  border-radius: 4px;
  text-decoration: none;
  font-size: 14px;
}

.btn-back:hover {
  background: #ecf5ff;
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

.footer-section h4 {
  font-size: 18px;
  margin-bottom: 15px;
}

.footer-bottom {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}
</style>
