<template>
  <el-dialog
    v-model="dialogVisible"
    :title="title"
    :width="width"
    :before-close="handleClose"
    v-bind="$attrs"
  >
    <slot>
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="100px"
        v-loading="loading"
      >
        <slot name="form" :form="formData" />
      </el-form>
    </slot>
    <template #footer>
      <slot name="footer" :loading="confirmLoading">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="confirmLoading">
          确定
        </el-button>
      </slot>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { FormInstance } from 'element-plus'

interface Props {
  title: string
  width?: string
  visible: boolean
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  width: '500px',
  loading: false
})

const emit = defineEmits<{
  'update:visible': [value: boolean]
  submit: [formData: any]
}>()

const formRef = ref<FormInstance>()
const formData = ref<any>({})
const rules = ref<any>({})
const confirmLoading = ref(false)

const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

const handleClose = () => {
  formRef.value?.resetFields()
  emit('update:visible', false)
}

const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    confirmLoading.value = true
    emit('submit', formData.value)
  } catch (error) {
    console.error('表单验证失败', error)
  } finally {
    confirmLoading.value = false
  }
}

// 暴露方法给父组件
defineExpose({
  formRef,
  formData,
  rules,
  reset: () => {
    formRef.value?.resetFields()
    formData.value = {}
  }
})
</script>
