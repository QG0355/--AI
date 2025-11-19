<template>
  <div class="login-page-wrapper">
    <div class="login-container">
      <div class="login-header">
        <i class="fas fa-user-plus"></i> <h1>注册新账号</h1>
        <p>加入 IT 报修平台</p>
      </div>

      <form class="login-form" @submit.prevent="handleRegister">
        <div class="form-group">
          <label>账号 (登录用)</label>
          <input type="text" v-model="form.username" placeholder="请设置登录账号" required>
        </div>

        <div class="form-group">
          <label>密码</label>
          <input type="password" v-model="form.password" placeholder="请设置登录密码" required>
        </div>

        <div class="form-group">
          <label>真实姓名</label>
          <input type="text" v-model="form.name" placeholder="请输入您的姓名" required>
        </div>

        <div class="form-group">
          <label>我是：</label>
          <select v-model="form.role" required>
           <option value="student">在校学生</option>
            <option value="teacher">教职工</option>
            <option value="dorm_manager">宿管人员</option>
            <option value="building_manager">教学楼管理员</option>
            <option value="repair_admin">报修管理员 (审核)</option> <option value="maintenance">维修人员</option> 
          </select>
        </div>

        <div class="form-group">
          <label>{{ identityLabel }}</label>
          <input type="text" v-model="form.identity_id" :placeholder="`请输入您的${identityLabel}`" required>
        </div>
        
        <button type="submit" class="btn-primary" :disabled="loading">
          {{ loading ? '注册中...' : '立即注册' }}
        </button>
      </form>

      <div class="demo-info">
        <p>已有账号? <RouterLink to="/login">返回登录</RouterLink></p>
      </div>
      
      <p v-if="message" class="message">{{ message }}</p>
      <p v-if="error" class="error-message">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const loading = ref(false)
const error = ref(null)
const message = ref(null)

const form = ref({
  username: '',
  password: '',
  name: '',
  role: 'student', 
  identity_id: ''
})

const identityLabel = computed(() => {
  const map = {
    'student': '学号',
    'teacher': '教师编号',
    'dorm_manager': '工号',
    'building_manager': '管理员工号'
  }
  return map[form.value.role] || '身份ID'
})

async function handleRegister() {
  loading.value = true
  error.value = null
  
  try {
    await axios.post('http://127.0.0.1:8000/api/register/', form.value)
    message.value = '注册成功！正在跳转...'
    setTimeout(() => router.push('/login'), 1500)
  } catch (err) {
    loading.value = false
    const data = err.response?.data || {}
    if (data.username) error.value = "注册失败: 账号已存在"
    else if (data.identity_id) error.value = `注册失败: 该${identityLabel.value}已被绑定`
    else error.value = '注册失败，请检查输入'
  }
}
</script>

<style scoped>
/* 保持你原有的样式 */
.login-page-wrapper { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; }
.login-container { max-width: 400px; width: 90%; margin: 20px auto; background: white; border-radius: 15px; padding: 40px; text-align: center; }
.login-header { margin-bottom: 20px; }
.login-header i { font-size: 48px; color: #667eea; }
.form-group { margin-bottom: 15px; text-align: left; }
.form-group label { display: block; margin-bottom: 5px; font-weight: 600; }
.form-group input, select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box;}
.btn-primary { width: 100%; padding: 12px; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer; margin-top: 10px; }
.error-message { color: #dc3545; margin-top: 15px; }
.message { color: #28a745; margin-top: 15px; }
</style>