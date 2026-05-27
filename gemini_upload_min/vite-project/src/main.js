import { createApp } from 'vue'
import { createPinia } from 'pinia' // 1. 导入 Pinia
import './style.css' 
import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth' // 导入 authStore



const app = createApp(App)
const pinia = createPinia() // 2. 创建 Pinia 实例

app.use(router) // 告诉 Vue 使用路由
app.use(pinia) // 3. 告诉 Vue 使用 Pinia

// 4. 初始化时恢复用户信息
const auth = useAuthStore()
if (auth.token) {
  auth.fetchUser()
}

app.mount('#app')