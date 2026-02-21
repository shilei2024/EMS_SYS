<template>
  <el-upload
    ref="uploadRef"
    :class="['file-upload', { 'is-disabled': disabled }]"
    :action="uploadUrl"
    :headers="headers"
    :data="extraData"
    :show-file-list="showFileList"
    :drag="drag"
    :multiple="multiple"
    :accept="accept"
    :before-upload="handleBeforeUpload"
    :on-success="handleSuccess"
    :on-error="handleError"
    :on-progress="handleProgress"
    :limit="limit"
    :disabled="disabled"
  >
    <slot v-if="!showFileList">
      <el-icon class="upload-icon"><UploadFilled /></el-icon>
      <div class="upload-text">
        {{ drag ? '将文件拖到此处，或' : '' }}点击上传
      </div>
      <div v-if="tip" class="upload-tip">{{ tip }}</div>
    </slot>
    <template #file="{ file }">
      <slot name="file" :file="file">
        <el-tag size="small" :type="getFileStatusType(file.status)">
          {{ file.name }}
        </el-tag>
      </slot>
    </template>
  </el-upload>
  <div v-if="progress > 0" class="upload-progress">
    <el-progress :percentage="progress" />
  </div>
</template>

<script setup lang="ts">
import { UploadInstance, UploadUserFile, UploadProps } from 'element-plus'

interface Props {
  uploadUrl?: string
  extraData?: Record<string, any>
  showFileList?: boolean
  drag?: boolean
  multiple?: boolean
  accept?: string
  limit?: number
  disabled?: boolean
  tip?: string
  maxSize?: number // MB
}

const props = withDefaults(defineProps<Props>(), {
  uploadUrl: '/api/v1/upload',
  showFileList: true,
  drag: false,
  multiple: false,
  limit: 1
})

const emit = defineEmits<{
  success: [response: any, file: UploadUserFile]
  error: [error: any, file: UploadUserFile]
  progress: [percentage: number]
  change: [files: UploadUserFile[]]
}>()

const uploadRef = ref<UploadInstance>()
const progress = ref(0)

const headers = computed(() => {
  const token = localStorage.getItem('token')
  return {
    Authorization: token ? `Bearer ${token}` : ''
  }
})

const handleBeforeUpload: UploadProps['beforeUpload'] = (file) => {
  if (props.maxSize && file.size > props.maxSize * 1024 * 1024) {
    ElMessage.error(`文件大小不能超过 ${props.maxSize}MB`)
    return false
  }
  return true
}

const handleSuccess = (response: any, file: UploadUserFile) => {
  progress.value = 0
  emit('success', response, file)
}

const handleError = (error: any, file: UploadUserFile) => {
  progress.value = 0
  ElMessage.error('上传失败')
  emit('error', error, file)
}

const handleProgress = (percentage: number) => {
  progress.value = percentage
  emit('progress', percentage)
}

const getFileStatusType = (status: string) => {
  const map: Record<string, any> = {
    ready: 'info',
    uploading: 'warning',
    success: 'success',
    error: 'danger'
  }
  return map[status] || 'info'
}

// 暴露方法
defineExpose({
  clearFiles: () => {
    uploadRef.value?.clearFiles()
  },
  submit: () => {
    uploadRef.value?.submit()
  }
})
</script>

<style scoped>
.file-upload {
  width: 100%;
}

.file-upload.is-disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.upload-icon {
  font-size: 48px;
  color: #909399;
  margin-bottom: 16px;
}

.upload-text {
  color: #606266;
  font-size: 14px;
  text-align: center;
}

.upload-tip {
  color: #909399;
  font-size: 12px;
  text-align: center;
  margin-top: 8px;
}

.upload-progress {
  margin-top: 12px;
}

:deep(.el-upload-dragger) {
  padding: 40px 20px;
}

:deep(.el-upload__text) {
  color: #606266;
}
</style>
