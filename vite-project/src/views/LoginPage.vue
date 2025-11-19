<template>
  <div class="login-page-wrapper">
    <div class="login-container">
      
      <div class="login-header">
        <i class="fas fa-tools"></i>
        <h1>IT 报修速响应平台</h1>
        <p>快速响应，专业服务</p>
      </div>

      <form id="loginForm" class="login-form" @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="username">工号</label>
          <input type="text" id="username" v-model="username" required>
        </div>
        <div class="form-group">
          <label for="password">密码</label>
          <input type="password" id="password" v-model="password" required>
        </div>
        
        <button type="submit" class="btn-primary" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>

      <div class="demo-info">
        <p><strong>演示账号：</strong></p>
        <p>员工：emp001 / 123456</p>
        <p>IT管理员：admin / admin123</p>
      </div>
      
      <div class="register-link">
        <p>还没有账号? 
          <RouterLink to="/register">立即注册</RouterLink>
        </p>
      </div>

      <p v-if="error" class="error-message">{{ error }}</p>

    </div> </div> </template>

<script setup>
// 1. 导入 Vue、Pinia 和 Vue Router
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

// 2. 创建响应式变量
// ref() 用于创建可以被 Vue 跟踪的变量
const username = ref('emp001') // 默认填入演示账号
const password = ref('123456') // 默认填入演示密码
const loading = ref(false)
const error = ref(null)

// 3. 获取 Pinia store 和 router 实例
const authStore = useAuthStore()
const router = useRouter() // router 实例用于页面跳转

// 4. 定义登录方法
async function handleLogin() {
  loading.value = true
  error.value = null
  
  // 5. 【⭐ 这就是数据交互！⭐】
  // 调用 Pinia (authStore) 里的 login action
  // authStore 会在内部调用 Axios 向 Django 发送请求
  const success = await authStore.login(username.value, password.value)
  
  loading.value = false
  
  // 6. 根据交互结果，进行页面跳转
  if (success) {
    // 登录成功！跳转到仪表板
    router.push('/dashboard')
  } else {
    // 登录失败！显示错误
    error.value = '用户名或密码错误！'
  }
}
</script>

<style scoped>
/* scoped 关键字意味着这些样式只对
  当前这个 .vue 文件生效，不会污染全局 
*/

/* 从 styles.css 复制过来的登录页面样式 */
.login-page-wrapper {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-container {
  max-width: 400px;
  width: 90%;
  margin: 40px auto;
  background: white;
  border-radius: 15px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  padding: 40px;
  text-align: center;
}

.login-header {
  margin-bottom: 30px;
}

.login-header i {
  font-size: 48px;
  color: #667eea;
  margin-bottom: 15px;
}

.login-header h1 {
  font-size: 24px;
  color: #333;
  margin-bottom: 8px;
}

.login-header p {
  color: #666;
  font-size: 14px;
}

.login-form {
  text-align: left;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.form-group input {
  width: 100%;
  padding: 12px 15px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.3s ease;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
}

.btn-primary {
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary:hover {
  transform: translateY(-2px);
}
.btn-primary:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.demo-info {
  margin-top: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  font-size: 12px;
  color: #666;
}

.demo-info p {
  margin-bottom: 5px;
}

.error-message {
  color: #dc3545;
  margin-top: 15px;
  font-weight: 500;
}
.register-link {
  margin-top: 20px;
  font-size: 14px;
}

.register-link a {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
}

.register-link a:hover {
  text-decoration: underline;
}

</style>