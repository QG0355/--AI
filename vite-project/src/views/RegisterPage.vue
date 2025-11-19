<template>
  <div class="login-page-wrapper">
    <div class="login-container">
      <div class="login-header">
        <i class="fas fa-user-plus"></i>
        <h1>注册新账号</h1>
        <p>加入校园报修平台</p>
      </div>

      <form class="login-form" @submit.prevent="handleRegister">
        <div class="form-group">
          <label>账号</label>
          <input type="text" v-model="form.username" placeholder="请设置登录账号" required>
        </div>

        <div class="form-group">
          <label>密码</label>
          <input type="password" v-model="form.password" placeholder="请设置密码" required>
        </div>

        <div class="form-group">
          <label>确认密码</label>
          <input type="password" v-model="form.confirmPassword" placeholder="请再次输入密码" required>
        </div>
        
        <button type="submit" class="btn-primary" :disabled="loading">
          {{ loading ? '注册中...' : '立即注册' }}
        </button>
      </form>

      <div class="demo-info">
        <p>已有账号? <RouterLink to="/login">返回登录</RouterLink></p>
      </div>
      
      <p v-if="error" class="error-message">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const loading = ref(false)
const error = ref(null)

const form = ref({
  username: '',
  password: '',
  confirmPassword: ''
})

async function handleRegister() {
  if (form.value.password !== form.value.confirmPassword) {
    error.value = "两次输入的密码不一致！"
    return
  }

  loading.value = true
  error.value = null

  try {
    // 发送最简单的注册请求
    await axios.post('http://127.0.0.1:8000/api/register/', {
      username: form.value.username,
      password: form.value.password
    })
    
    alert("注册成功！请登录并完成身份绑定。")
    router.push('/login')

  } catch (err) {
    loading.value = false
    const data = err.response?.data || {}
    if (data.username) error.value = "注册失败: 账号已存在"
    else error.value = '注册失败，请检查网络或联系管理员。'
  }
}
</script>

<style scoped>
/* (保持原有样式不变，为了节省篇幅省略，请保留你原来的style部分) */
/* 建议直接复用 LoginPage.vue 的样式 */
.login-page-wrapper { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; }
.login-container { max-width: 400px; width: 90%; margin: 20px auto; background: white; border-radius: 15px; padding: 40px; text-align: center; }
.login-header { margin-bottom: 20px; }
.login-header i { font-size: 48px; color: #667eea; }
.form-group { margin-bottom: 15px; text-align: left; }
.form-group label { display: block; margin-bottom: 5px; font-weight: 600; }
.form-group input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box;}
.btn-primary { width: 100%; padding: 12px; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer; margin-top: 10px; }
.error-message { color: #dc3545; margin-top: 15px; }
</style>