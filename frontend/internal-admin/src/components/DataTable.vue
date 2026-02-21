<template>
  <el-table :data="data" v-bind="$attrs" stripe>
    <el-table-column
      v-if="showSelection"
      type="selection"
      width="55"
      align="center"
    />
    <el-table-column
      v-if="showIndex"
      type="index"
      label="序号"
      width="60"
      align="center"
    />
    <slot>
      <el-table-column
        v-for="column in columns"
        :key="column.prop"
        :prop="column.prop"
        :label="column.label"
        :width="column.width"
        :min-width="column.minWidth"
        :align="column.align || 'left'"
        :sortable="column.sortable"
      >
        <template #default="{ row }" v-if="column.slotName">
          <slot :name="column.slotName" :row="row" />
        </template>
      </el-table-column>
    </slot>
    <el-table-column
      v-if="showOperation"
      label="操作"
      width="200"
      align="center"
      fixed="right"
    >
      <template #default="{ row }">
        <slot name="operation" :row="row">
          <el-button link type="primary" size="small" @click="handleEdit(row)">
            编辑
          </el-button>
          <el-button link type="danger" size="small" @click="handleDelete(row)">
            删除
          </el-button>
        </slot>
      </template>
    </el-table-column>
  </el-table>
</template>

<script setup lang="ts">
interface Column {
  prop: string
  label: string
  width?: number | string
  minWidth?: number | string
  align?: 'left' | 'center' | 'right'
  sortable?: boolean
  slotName?: string
}

interface Props {
  data: any[]
  columns?: Column[]
  showSelection?: boolean
  showIndex?: boolean
  showOperation?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showSelection: false,
  showIndex: false,
  showOperation: false
})

const emit = defineEmits<{
  edit: [row: any]
  delete: [row: any]
}>()

const handleEdit = (row: any) => {
  emit('edit', row)
}

const handleDelete = (row: any) => {
  emit('delete', row)
}
</script>
