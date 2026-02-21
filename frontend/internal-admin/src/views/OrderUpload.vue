<template>
  <div class="order-upload-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>订单文件上传</span>
        </div>
      </template>

      <el-steps :active="currentStep" finish-status="success" align-center>
        <el-step title="上传文件" />
        <el-step title="OCR 处理" />
        <el-step title="确认订单" />
        <el-step title="完成" />
      </el-steps>

      <!-- 步骤 1: 上传文件 -->
      <div v-show="currentStep === 0" class="step-content">
        <el-upload
          ref="uploadRef"
          class="upload-area"
          drag
          :auto-upload="false"
          :limit="1"
          :on-change="handleFileChange"
          :on-exceed="handleExceed"
          accept=".pdf,.png,.jpg,.jpeg"
        >
          <el-icon class="el-icon--upload"><Upload /></el-icon>
          <div class="el-upload__text">
            将文件拖到此处，或<em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              支持 PDF、PNG、JPG、JPEG 格式，单个文件不超过 10MB
            </div>
          </template>
        </el-upload>

        <div class="upload-actions">
          <el-button type="primary" :disabled="!selectedFile" @click="startOCR">
            开始 OCR 处理
          </el-button>
        </div>
      </div>

      <!-- 步骤 2: OCR 处理中 -->
      <div v-show="currentStep === 1" class="step-content">
        <div class="processing">
          <el-icon class="processing-icon is-loading"><Loading /></el-icon>
          <p>正在处理文件，请稍候...</p>
          <el-progress :percentage="ocrProgress" :stroke-width="8" />
          <p class="processing-tip">{{ processingTip }}</p>
        </div>
      </div>

      <!-- 步骤 3: 确认订单 -->
      <div v-show="currentStep === 2" class="step-content">
        <el-form :model="orderForm" label-width="120px" class="order-form">
          <el-form-item label="订单号">
            <el-input v-model="orderForm.orderNumber" disabled />
          </el-form-item>
          <el-form-item label="客户名称">
            <el-input v-model="orderForm.customerName" />
          </el-form-item>
          <el-form-item label="客户邮箱">
            <el-input v-model="orderForm.customerEmail" />
          </el-form-item>
          <el-form-item label="客户电话">
            <el-input v-model="orderForm.customerPhone" />
          </el-form-item>
          <el-form-item label="订单金额">
            <el-input-number v-model="orderForm.totalAmount" :precision="2" :min="0" />
          </el-form-item>
          <el-form-item label="备注">
            <el-input v-model="orderForm.notes" type="textarea" :rows="3" />
          </el-form-item>
        </el-form>

        <el-divider>订单明细</el-divider>

        <el-table :data="orderItems" style="width: 100%">
          <el-table-column prop="lineNumber" label="行号" width="60" />
          <el-table-column prop="mpn" label="型号" />
          <el-table-column prop="manufacturer" label="厂商" />
          <el-table-column prop="description" label="描述" />
          <el-table-column prop="quantity" label="数量" width="80" />
          <el-table-column prop="unitPrice" label="单价" width="100">
            <template #default="{ row }">
              ¥{{ row.unitPrice?.toFixed(2) }}
            </template>
          </el-table-column>
          <el-table-column prop="totalPrice" label="总价" width="100">
            <template #default="{ row }">
              ¥{{ row.totalPrice?.toFixed(2) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="80">
            <template #default="{ row }">
              <el-button type="danger" link @click="removeItem(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="ocr-confidence">
          <span>OCR 置信度：</span>
          <el-progress
            :percentage="Math.round(ocrResult.confidence * 100)"
            :color="confidenceColor"
            :stroke-width="12"
            style="width: 200px; display: inline-block"
          />
          <el-tag :type="confidenceType" style="margin-left: 10px">
            {{ confidenceText }}
          </el-tag>
          <el-tag v-if="ocrResult.requires_manual_review" type="warning" style="margin-left: 10px">
            需要人工审核
          </el-tag>
        </div>

        <div class="form-actions">
          <el-button @click="currentStep = 0">上一步</el-button>
          <el-button type="primary" @click="submitOrder">确认提交</el-button>
        </div>
      </div>

      <!-- 步骤 4: 完成 -->
      <div v-show="currentStep === 3" class="step-content">
        <div class="success">
          <el-icon class="success-icon"><Success /></el-icon>
          <h2>订单提交成功</h2>
          <p>订单号：{{ submittedOrderNumber }}</p>
          <p v-if="ocrResult.requires_manual_review" class="review-tip">
            <el-tag type="warning">需要人工审核</el-tag>
          </p>
          <div class="success-actions">
            <el-button type="primary" @click="$router.push('/orders')">查看订单</el-button>
            <el-button @click="handleReset">继续上传</el-button>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage, ElNotification } from 'element-plus'
import { Upload, Loading, Success } from '@element-plus/icons-vue'
import { uploadOrderFile } from '../api/order'

const uploadRef = ref()
const currentStep = ref(0)
const selectedFile = ref<File | null>(null)
const ocrProgress = ref(0)
const processingTip = ref('正在上传文件...')

const orderForm = ref({
  orderNumber: '',
  customerName: '',
  customerEmail: '',
  customerPhone: '',
  totalAmount: 0,
  notes: ''
})

const orderItems = ref<any[]>([])
const ocrResult = ref<any>({ confidence: 0, order_id: '', status: '', requires_manual_review: false })
const submittedOrderNumber = ref('')

const confidenceColor = computed(() => {
  if (ocrResult.value.confidence >= 0.9) return '#67c23a'
  if (ocrResult.value.confidence >= 0.7) return '#e6a23c'
  return '#f56c6c'
})

const confidenceType = computed(() => {
  if (ocrResult.value.confidence >= 0.9) return 'success'
  if (ocrResult.value.confidence >= 0.7) return 'warning'
  return 'danger'
})

const confidenceText = computed(() => {
  if (ocrResult.value.confidence >= 0.9) return '高置信度'
  if (ocrResult.value.confidence >= 0.7) return '中置信度'
  return '低置信度'
})

function handleFileChange(file: any) {
  selectedFile.value = file.raw
}

function handleExceed() {
  ElMessage.warning('只能上传一个文件')
}

async function startOCR() {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }

  currentStep.value = 1
  ocrProgress.value = 0
  processingTip.value = '正在上传文件...'

  try {
    // 调用真实 OCR API
    const result = await uploadOrderFile(selectedFile.value)

    // 更新进度
    ocrProgress.value = 100
    processingTip.value = 'OCR 处理完成'

    // 保存 OCR 结果
    ocrResult.value = {
      confidence: result.ocr_confidence,
      order_id: result.order_id,
      status: result.status,
      requires_manual_review: result.requires_manual_review
    }

    // 显示处理结果
    if (result.requires_manual_review) {
      ElMessage.warning({
        message: `OCR 处理成功，置信度 ${(result.ocr_confidence * 100).toFixed(1)}%，需要人工审核`,
        duration: 3000
      })
    } else {
      ElMessage.success({
        message: `OCR 处理成功，置信度 ${(result.ocr_confidence * 100).toFixed(1)}%，已自动通过`,
        duration: 3000
      })
    }

    // TODO: 根据 order_id 获取订单详情
    // 暂时使用模拟数据填充表单
    await new Promise(resolve => setTimeout(resolve, 500))

    // 模拟数据 - 实际应该从 API 获取订单详情
    const mockData = {
      order_number: `OCR-${Date.now()}`,
      customer_name: '华为技术有限公司',
      customer_email: 'purchase@huawei.com',
      customer_phone: '+86-755-28780808',
      total_amount: 16800,
      currency: 'CNY',
      line_items: [
        { line_number: 1, mpn: 'STM32F407VGT6', manufacturer: 'STMicroelectronics', description: 'ARM Cortex-M4 MCU', quantity: 1000, unit_price: 5.2, total_price: 5200 },
        { line_number: 2, mpn: 'ATMEGA328P-PU', manufacturer: 'Microchip', description: '8-bit AVR MCU', quantity: 2000, unit_price: 2.8, total_price: 5600 },
        { line_number: 3, mpn: 'ESP32-WROOM-32', manufacturer: 'Espressif', description: 'WiFi+BT MCU', quantity: 1500, unit_price: 3.5, total_price: 5250 }
      ]
    }

    // 填充表单
    orderForm.value = {
      orderNumber: mockData.order_number,
      customerName: mockData.customer_name || '',
      customerEmail: mockData.customer_email || '',
      customerPhone: mockData.customer_phone || '',
      totalAmount: mockData.total_amount || 0,
      notes: ''
    }

    orderItems.value = (mockData.line_items || []).map((item: any) => ({
      lineNumber: item.line_number,
      mpn: item.mpn,
      manufacturer: item.manufacturer,
      description: item.description,
      quantity: item.quantity,
      unitPrice: item.unit_price,
      totalPrice: item.total_price
    }))

    currentStep.value = 2

  } catch (error: any) {
    console.error('OCR 处理失败:', error)
    ElMessage.error(error.message || 'OCR 处理失败，请重试')
    currentStep.value = 0
    ocrProgress.value = 0
  }
}

async function submitOrder() {
  try {
    // TODO: 调用真实 API 创建订单
    // await createOrder({ ... })

    submittedOrderNumber.value = orderForm.value.orderNumber
    currentStep.value = 3

    ElNotification({
      title: '成功',
      message: '订单创建成功',
      type: 'success'
    })
  } catch (error: any) {
    console.error('提交失败:', error)
    ElMessage.error('提交失败')
  }
}

function removeItem(item: any) {
  const index = orderItems.value.indexOf(item)
  if (index > -1) {
    orderItems.value.splice(index, 1)
  }
}

function handleReset() {
  selectedFile.value = null
  currentStep.value = 0
  ocrProgress.value = 0
  processingTip.value = '正在上传文件...'
  orderForm.value = {
    orderNumber: '',
    customerName: '',
    customerEmail: '',
    customerPhone: '',
    totalAmount: 0,
    notes: ''
  }
  orderItems.value = []
  ocrResult.value = { confidence: 0, order_id: '', status: '', requires_manual_review: false }
  uploadRef.value?.clearFiles()
}
</script>

<style scoped>
.order-upload-page {
  padding: 20px;
  max-width: 900px;
  margin: 0 auto;
}

.card-header {
  font-size: 18px;
  font-weight: 600;
}

.step-content {
  margin-top: 40px;
  min-height: 300px;
}

.upload-area {
  width: 100%;
}

.upload-actions {
  margin-top: 30px;
  text-align: center;
}

.processing {
  text-align: center;
  padding: 60px 20px;
}

.processing-icon {
  font-size: 48px;
  color: #409eff;
  margin-bottom: 20px;
}

.processing-tip {
  color: #999;
  margin-top: 10px;
}

.order-form {
  max-width: 600px;
  margin: 0 auto;
}

.ocr-confidence {
  margin: 30px 0;
  text-align: center;
}

.form-actions {
  margin-top: 30px;
  text-align: center;
}

.success {
  text-align: center;
  padding: 60px 20px;
}

.success-icon {
  font-size: 64px;
  color: #67c23a;
  margin-bottom: 20px;
}

.success h2 {
  color: #67c23a;
  margin-bottom: 10px;
}

.review-tip {
  margin-top: 15px;
}

.success-actions {
  margin-top: 30px;
}
</style>
