import { createApp } from 'vue'
import { createPinia } from 'pinia' // 1. 导入 Pinia
import './style.css' 
import App from './App.vue'
import router from './router'



const app = createApp(App)
const pinia = createPinia() // 2. 创建 Pinia 实例

app.use(router) // 告诉 Vue 使用路由
app.use(pinia) // 3. 告诉 Vue 使用 Pinia

app.mount('#app')