<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <div class="logo-icon">
          <i class="fas fa-tools"></i>
        </div>
        <h2>校园报修服务平台</h2>
        <p>Enterprise IT Service Desk</p>
      </div>

      <form @submit.prevent="handleLogin">
        <div class="input-group">
          <label>账号 / User ID</label>
          <div class="input-wrapper">
            <i class="fas fa-user"></i>
            <input type="text" v-model="username" placeholder="请输入工号/学号" required>
          </div>
        </div>

        <div class="input-group">
          <label>密码 / Password</label>
          <div class="input-wrapper">
            <i class="fas fa-lock"></i>
            <input type="password" v-model="password" placeholder="请输入密码" required>
          </div>
        </div>

        <button type="submit" class="btn-login" :disabled="loading">
          {{ loading ? '正在登录...' : '登 录' }}
        </button>

        <div class="login-footer">
          <span>还没有账号？</span>
          <RouterLink to="/register">注册新用户</RouterLink>
        </div>
      </form>

      <div v-if="error" class="error-banner">
        <i class="fas fa-exclamation-circle"></i> {{ error }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref(null)
const authStore = useAuthStore()
const router = useRouter()

async function handleLogin() {
  loading.value = true
  error.value = null
  
  const result = await authStore.login(username.value, password.value)
  
  loading.value = false
  
  if (result.success) {
    const user = authStore.currentUser
    const role = user?.role

    if (!user?.is_identity_bound) {
      router.push('/bind')
      return
    }

    if (['maintenance', 'repair_admin', 'admin', 'auditor'].includes(role)) {
      router.push('/workplace')
    } else {
      router.push('/')
    }
  } else {
    error.value = result.message 
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  /* ⭐ 核心修改：使用 CSS 线性渐变作为背景 */
  /* 左上角 #1e3c72 (深蓝)，右下角 #2a5298 (稍亮的蓝) */
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
  
  display: flex;
  align-items: center;
  justify-content: center;
  /* 之前的 position: relative 和伪元素遮罩都不需要了，因为没有图片要遮 */
}

.login-box {
  width: 100%;
  max-width: 420px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 40px;
  /* 给盒子加一点深色阴影，让它在渐变背景上浮起来 */
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2); 
  animation: slideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes slideUp {
  from { transform: translateY(30px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.login-header {
  text-align: center;
  margin-bottom: 35px;
}

.logo-icon {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  margin: 0 auto 15px;
  box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.4);
  transform: rotate(-5deg);
}

.login-header h2 {
  color: #1e293b;
  font-size: 26px;
  font-weight: 800;
  margin-bottom: 5px;
  letter-spacing: -0.5px;
}

.login-header p {
  color: #64748b;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-weight: 600;
}

.input-group {
  margin-bottom: 24px;
}

.input-group label {
  display: block;
  margin-bottom: 8px;
  color: #475569;
  font-size: 14px;
  font-weight: 600;
}

.input-wrapper {
  position: relative;
}

.input-wrapper i {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  font-size: 16px;
  transition: color 0.3s;
}

.input-wrapper input {
  width: 100%;
  padding: 14px 16px 14px 48px;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  font-size: 15px;
  color: #334155;
  background: #f8fafc;
  transition: all 0.3s;
  box-sizing: border-box;
}

.input-wrapper input:focus {
  border-color: #3b82f6;
  background: white;
  outline: none;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
}

.input-wrapper input:focus + i {
  color: #3b82f6;
}

.btn-login {
  width: 100%;
  padding: 14px;
  background: linear-gradient(to right, #3b82f6, #2563eb);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  margin-top: 10px;
  box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.5);
}

.btn-login:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.6);
}

.btn-login:active {
  transform: translateY(0);
}

.btn-login:disabled {
  background: #cbd5e1;
  transform: none;
  box-shadow: none;
  cursor: not-allowed;
}

.login-footer {
  margin-top: 25px;
  text-align: center;
  font-size: 14px;
  color: #64748b;
}

.login-footer a {
  color: #2563eb;
  text-decoration: none;
  font-weight: 700;
  margin-left: 5px;
}

.login-footer a:hover {
  text-decoration: underline;
}

.error-banner {
  margin-top: 20px;
  padding: 12px;
  background: #fee2e2;
  color: #b91c1c;
  border-radius: 8px;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  animation: shake 0.5s cubic-bezier(.36,.07,.19,.97) both;
}

@keyframes shake {
  10%, 90% { transform: translate3d(-1px, 0, 0); }
  20%, 80% { transform: translate3d(2px, 0, 0); }
  30%, 50%, 70% { transform: translate3d(-4px, 0, 0); }
  40%, 60% { transform: translate3d(4px, 0, 0); }
}
</style>
