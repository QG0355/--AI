<template>
  <div class="login-page-wrapper">
    <div class="login-container">
      <div class="login-header">
        <i class="fas fa-user-plus"></i> <h1>注册新账号</h1>
        <p>加入 IT 报修平台</p>
      </div>

      <form class="login-form" @submit.prevent="handleRegister">
        <div class="form-group">
          <label for="name">姓名</label>
          <input type="text" id="name" v-model="name" required>
        </div>

        <div class="form-group">
          <label for="username">工号 (登录用)</label>
          <input type="text" id="username" v-model="username" required>
        </div>

        <div class="form-group">
          <label for="password">密码</label>
          <input type="password" id="password" v-model="password" required>
        </div>
        
      
        
        <button type="submit" class="btn-primary" :disabled="loading">
          {{ loading ? '注册中...' : '立即注册' }}
        </button>
      </form>

      <div class="demo-info">
        <p>已有账号? 
          <RouterLink to="/login">返回登录</RouterLink>
        </p>
      </div>
      
      <p v-if="message" class="message">{{ message }}</p>
      <p v-if="error" class="error-message">{{ error }}</p>

    </div>
  </div>
</template>

<script setup>
// 1. 导入 Vue、Router 和 Axios
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios' // 我们直接用 axios，不通过 Pinia

// 2. 创建响应式变量
const name = ref('')
const username = ref('')
const password = ref('')
const role = ref('employee') // 默认角色
const loading = ref(false)
const error = ref(null)
const message = ref(null)

const router = useRouter() // router 实例用于页面跳转

// 3. 定义注册方法
async function handleRegister() {
  loading.value = true
  error.value = null
  message.value = null

  try {
    // 4. 【⭐ 这就是数据交换！⭐】
    // 直接调用我们刚在 Django 上创建的 /api/register/ 接口
    const response = await axios.post('http://127.0.0.1:8000/api/register/', {
      name: name.value,
      username: username.value,
      password: password.value,
      role: role.value,
    })
    
    // 5. 注册成功
    loading.value = false
    message.value = '注册成功！正在跳转到登录页...'

    // 2秒后自动跳转到登录页
    setTimeout(() => {
      router.push('/login')
    }, 2000)

  } catch (err) {
    // 6. 注册失败
    loading.value = false
    if (err.response && err.response.data.username) {
      error.value = '注册失败：工号（用户名）已存在！'
    } else {
      error.value = '注册失败，请检查网络或联系管理员。'
    }
    console.error(err)
  }
}
</script>

<style scoped>
/* 样式和 LoginPage.vue 基本一样 */
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

.form-group input, .form-group select {
  width: 100%;
  padding: 12px 15px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.3s ease;
}

.form-group input:focus, .form-group select:focus {
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
.message {
  color: #28a745; /* 绿色成功提示 */
  margin-top: 15px;
  font-weight: 500;
}
</style>