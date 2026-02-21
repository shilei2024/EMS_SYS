<template>
  <el-card class="stat-card" :style="{ borderColor: color }">
    <div class="stat-content">
      <div class="stat-icon" :style="{ backgroundColor: color + '20' }">
        <el-icon :size="24" :color="color">
          <component :is="icon" />
        </el-icon>
      </div>
      <div class="stat-info">
        <div class="stat-value">{{ formatValue(value) }}</div>
        <div class="stat-label">{{ label }}</div>
      </div>
    </div>
    <div v-if="trend" class="stat-trend" :class="trend > 0 ? 'up' : 'down'">
      <el-icon><Top /></el-icon>
      <span>{{ Math.abs(trend) }}%</span>
    </div>
  </el-card>
</template>

<script setup lang="ts">
interface Props {
  label: string
  value: string | number
  icon?: string
  color?: string
  trend?: number
}

const props = withDefaults(defineProps<Props>(), {
  icon: 'DataLine',
  color: '#409EFF'
})

const formatValue = (value: string | number) => {
  if (typeof value === 'number') {
    if (value >= 100000000) {
      return (value / 100000000).toFixed(2) + '亿'
    }
    if (value >= 10000) {
      return (value / 10000).toFixed(2) + '万'
    }
    return value.toLocaleString()
  }
  return value
}
</script>

<style scoped>
.stat-card {
  border-left: 4px solid;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-content {
  display: flex;
  align-items: center;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.stat-trend {
  position: absolute;
  top: 16px;
  right: 16px;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 2px;
}

.stat-trend.up {
  color: #67c23a;
}

.stat-trend.down {
  color: #f56c6c;
}
</style>
