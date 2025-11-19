<template>
  <div class="register-container">
    <div class="register-box">
      <div class="register-header">
        <div class="logo-icon">
          <i class="fas fa-user-plus"></i>
        </div>
        <h2>创建新账号</h2>
        <p>Join IT Service Desk</p>
      </div>

      <form @submit.prevent="handleRegister">
        
        <div class="form-row">
          <div class="input-group half">
            <label>账号 / ID</label>
            <div class="input-wrapper">
              <i class="fas fa-id-badge"></i>
              <input type="text" v-model="form.username" placeholder="设置登录账号" required>
            </div>
          </div>
          <div class="input-group half">
            <label>密码 / Password</label>
            <div class="input-wrapper">
              <i class="fas fa-lock"></i>
              <input type="password" v-model="form.password" placeholder="设置登录密码" required>
            </div>
          </div>
        </div>

        <div class="input-group">
          <label>真实姓名 / Real Name</label>
          <div class="input-wrapper">
            <i class="fas fa-signature"></i>
            <input type="text" v-model="form.name" placeholder="请输入您的真实姓名" required>
          </div>
        </div>

        <div class="input-group">
          <label>身份角色 / Role</label>
          <div class="input-wrapper">
            <i class="fas fa-users"></i>
            <select v-model="form.role" required>
              <option value="student">在校学生</option>
              <option value="teacher">教职工</option>
              <option value="dorm_manager">宿管人员</option>
              <option value="building_manager">教学楼管理员</option>
              <option value="repair_admin">审核人员</option>
              <option value="maintenance">维修人员</option>
            </select>
          </div>
        </div>

        <div class="input-group">
          <label>{{ identityLabel }}</label>
          <div class="input-wrapper">
            <i class="fas fa-address-card"></i>
            <input type="text" v-model="form.identity_id" :placeholder="`请输入您的${identityLabel}`" required>
          </div>
        </div>
        
        <button type="submit" class="btn-register" :disabled="loading">
          {{ loading ? '注册中...' : '立即注册' }}
        </button>

        <div class="register-footer">
          <span>已有账号？</span>
          <RouterLink to="/login">返回登录</RouterLink>
        </div>
      </form>
      
      <div v-if="message" class="message-banner success">
        <i class="fas fa-check-circle"></i> {{ message }}
      </div>
      <div v-if="error" class="message-banner error">
        <i class="fas fa-exclamation-circle"></i> {{ error }}
      </div>

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

// 表单数据
const form = ref({
  username: '',
  password: '',
  name: '',
  role: 'student', 
  identity_id: ''
})

// 动态标签
const identityLabel = computed(() => {
  const map = {
    'student': '学号 (Student ID)',
    'teacher': '教师编号 (Teacher ID)',
    'dorm_manager': '宿管工号 (Staff ID)',
    'building_manager': '管理员工号 (Admin ID)',
    'repair_admin': '审核员工号 (Admin ID)',
    'maintenance': '维修员工号 (Worker ID)'
  }
  return map[form.value.role] || '身份ID'
})

async function handleRegister() {
  loading.value = true
  error.value = null
  message.value = null

  try {
    await axios.post('http://127.0.0.1:8000/api/register/', form.value)
    
    message.value = '注册成功！即将跳转...'
    setTimeout(() => {
      router.push('/login')
    }, 1500)

  } catch (err) {
    loading.value = false
    console.error(err.response?.data)

    if (err.response && err.response.data) {
      const data = err.response.data
      if (data.username) error.value = "注册失败: 账号已存在"
      else if (data.identity_id) error.value = `注册失败: 该${identityLabel.value.split(' ')[0]}已被绑定`
      else error.value = '注册失败，请检查输入信息'
    } else {
      error.value = '请求失败，请检查后端服务'
    }
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  /* 与登录页保持一致的深色科技背景 */
  background-image: url('https://images.unsplash.com/photo-1518770660439-4636190af475?q=80&w=2070&auto=format&fit=crop');
  background-size: cover;
  background-position: center;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  padding: 20px;
}

.register-container::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(15, 23, 42, 0.8);
  backdrop-filter: blur(3px);
}

.register-box {
  position: relative;
  width: 100%;
  max-width: 480px; /* 稍微宽一点，适合放两列 */
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  animation: slideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes slideUp {
  from { transform: translateY(30px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.register-header {
  text-align: center;
  margin-bottom: 30px;
}

.logo-icon {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #10b981, #059669); /* 绿色调，区分于登录页的蓝色 */
  color: white;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  margin: 0 auto 15px;
  box-shadow: 0 10px 15px -3px rgba(16, 185, 129, 0.4);
}

.register-header h2 {
  color: #1e293b;
  font-size: 24px;
  font-weight: 800;
  margin-bottom: 5px;
}

.register-header p {
  color: #64748b;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-weight: 600;
}

.form-row {
  display: flex;
  gap: 15px;
}
.half { flex: 1; }

.input-group { margin-bottom: 20px; }

.input-group label {
  display: block;
  margin-bottom: 8px;
  color: #475569;
  font-size: 13px;
  font-weight: 600;
}

.input-wrapper { position: relative; }

.input-wrapper i {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  font-size: 14px;
  pointer-events: none; /* 防止图标遮挡点击 */
}

.input-wrapper input, .input-wrapper select {
  width: 100%;
  padding: 12px 14px 12px 40px;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  font-size: 14px;
  color: #334155;
  background: #f8fafc;
  transition: all 0.3s;
  box-sizing: border-box;
  appearance: none; /* 移除原生 select 样式 */
}

.input-wrapper input:focus, .input-wrapper select:focus {
  border-color: #10b981;
  background: white;
  outline: none;
  box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.1);
}

.input-wrapper input:focus + i, .input-wrapper select:focus + i {
  color: #10b981;
}

.btn-register {
  width: 100%;
  padding: 14px;
  background: linear-gradient(to right, #10b981, #059669);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  margin-top: 10px;
  box-shadow: 0 4px 6px -1px rgba(16, 185, 129, 0.5);
}

.btn-register:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 15px -3px rgba(16, 185, 129, 0.6);
}

.btn-register:disabled {
  background: #cbd5e1;
  transform: none;
  box-shadow: none;
  cursor: not-allowed;
}

.register-footer {
  margin-top: 20px;
  text-align: center;
  font-size: 14px;
  color: #64748b;
}

.register-footer a {
  color: #059669;
  text-decoration: none;
  font-weight: 700;
  margin-left: 5px;
}
.register-footer a:hover { text-decoration: underline; }

.message-banner {
  margin-top: 20px;
  padding: 12px;
  border-radius: 8px;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  animation: fadeIn 0.3s ease;
}
.message-banner.error { background: #fee2e2; color: #b91c1c; }
.message-banner.success { background: #d1fae5; color: #047857; }

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>