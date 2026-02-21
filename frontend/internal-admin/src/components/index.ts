// 自动注册全局组件
import type { App } from 'vue'
import StatCard from './StatCard.vue'
import DataTable from './DataTable.vue'
import Pagination from './Pagination.vue'
import ModalForm from './ModalForm.vue'
import FileUpload from './FileUpload.vue'

const components = {
  StatCard,
  DataTable,
  Pagination,
  ModalForm,
  FileUpload
}

export function registerComponents(app: App) {
  for (const key in components) {
    app.component(key, components[key])
  }
}

export {
  StatCard,
  DataTable,
  Pagination,
  ModalForm,
  FileUpload
}

export default components
