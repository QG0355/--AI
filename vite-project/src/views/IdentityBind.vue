<template>
  <div class="bind-wrapper">
    <div class="top-bar">
      <button @click="handleLogout" class="btn-logout">
        <i class="fas fa-sign-out-alt"></i> 切换账号 / 退出
      </button>
    </div>

    <div class="bind-card">
      <h2><i class="fas fa-id-card"></i> 首次登录身份绑定</h2>
      <div class="warning">
        <i class="fas fa-exclamation-circle"></i>
        为了系统安全，新注册账号必须绑定真实身份才能使用。
        <br><strong>注意：绑定后不可自行修改！</strong>
      </div>
      
      <form @submit.prevent="handleBind">
        <div class="form-group">
          <label>我是：</label>
          <select v-model="form.role" required>
            <option value="student">在校学生</option>
            <option value="teacher">教职工</option>
            <option value="dorm_manager">宿管人员</option>
            <option value="building_manager">教学楼管理员</option>
          </select>
        </div>
        <div class="form-group">
          <label>真实姓名：</label>
          <input type="text" v-model="form.name" placeholder="例如：张三" required>
        </div>
        <div class="form-group">
          <label>学号/工号：</label>
          <input type="text" v-model="form.identity_id" placeholder="例如：2023001" required>
        </div>
        <button class="btn-primary" type="submit" :disabled="loading">
          {{ loading ? '绑定中...' : '确认绑定' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const form = ref({ role: 'student', name: '', identity_id: '' })
const loading = ref(false)
const authStore = useAuthStore()
const router = useRouter()

// 退出登录逻辑
function handleLogout() {
  authStore.logout()
  router.push('/login')
}

async function handleBind() {
  if(!confirm(`确认绑定身份为 [${form.value.name}] 吗？`)) return;
  
  loading.value = true
  try {
    // 这里的 URL 必须和你后端 urls.py 里配置的一样！
    const res = await axios.post('http://127.0.0.1:8000/api/bind-identity/', form.value, {
      headers: { Authorization: `Token ${authStore.token}` }
    })
    
    // 更新本地存储的用户信息（关键！把 is_identity_bound 更新为 true）
    authStore.currentUser = res.data.user
    localStorage.setItem('user', JSON.stringify(res.data.user)) // 如果你store里有持久化逻辑的话
    
    alert("绑定成功！欢迎进入系统。")
    
    // 绑定成功后，去主页
    router.push('/dashboard')
  } catch (e) {
    console.error(e)
    alert("绑定失败：" + (e.response?.data?.detail || "网络错误或后端未启动"))
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.bind-wrapper { 
  display: flex; 
  flex-direction: column;
  align-items: center; 
  min-height: 100vh;
  background: #f0f2f5;
  padding-top: 20px;
}

.top-bar {
  width: 100%;
  max-width: 400px;
  display: flex;
  justify-content: flex-end;
  margin-bottom: 10px;
}

.btn-logout {
  background: transparent;
  border: 1px solid #ccc;
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
  color: #666;
  font-size: 13px;
}
.btn-logout:hover { background: #e6e6e6; }

.bind-card { 
  width: 400px; 
  padding: 30px; 
  background: white; 
  border-radius: 10px; 
  box-shadow: 0 4px 12px rgba(0,0,0,0.1); 
}

.warning { 
  background: #fff3cd; 
  color: #856404; 
  padding: 12px; 
  margin-bottom: 20px; 
  font-size: 13px; 
  border-radius: 6px; 
  line-height: 1.5;
  border: 1px solid #ffeeba;
}

.form-group { margin-bottom: 20px; }
.form-group label { display: block; margin-bottom: 8px; font-weight: 600; color: #333; }
.form-group input, .form-group select { 
  width: 100%; 
  padding: 10px; 
  border: 1px solid #ddd; 
  border-radius: 6px; 
  font-size: 14px;
  box-sizing: border-box; /* 重要：防止输入框溢出 */
}

.btn-primary { 
  width: 100%; 
  padding: 12px; 
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
  color: white; 
  border: none; 
  border-radius: 6px; 
  cursor: pointer; 
  font-size: 16px;
  font-weight: 500;
}
.btn-primary:disabled { opacity: 0.7; cursor: not-allowed; }
</style>