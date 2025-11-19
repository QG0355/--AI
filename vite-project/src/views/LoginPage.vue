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

// 1. 【关键修改】默认值改为空字符串，不再自动填充
const username = ref('')
const password = ref('')

const loading = ref(false)
const error = ref(null)
const authStore = useAuthStore()
const router = useRouter()

async function handleLogin() {
  loading.value = true
  error.value = null
  
  // 1. 调用 Pinia 的登录，并接收返回值 (现在它返回的是一个对象)
  const result = await authStore.login(username.value, password.value)
  
  loading.value = false
  
  // 2. 判断结果
  if (result.success) {
    router.push('/dashboard')
  } else {
    // 3. 【关键】直接显示后端返回的详细错误！
    // 比如："Unable to log in with provided credentials." 或者 "账号不存在"
    error.value = result.message 
  }
}
</script>

<style scoped>
/* --- 全新设计的 UI --- */

.login-container {
  min-height: 100vh;
  /* 背景图：深蓝科技感背景 */
  background-image: url('https://images.unsplash.com/photo-1518770660439-4636190af475?q=80&w=2070&auto=format&fit=crop');
  background-size: cover;
  background-position: center;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

/* 加一层半透明深色遮罩，让文字更清晰 */
.login-container::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(15, 23, 42, 0.75); /* 深邃的蓝黑色遮罩 */
  backdrop-filter: blur(3px);
}

.login-box {
  position: relative; /* 确保在遮罩之上 */
  width: 100%;
  max-width: 420px;
  background: rgba(255, 255, 255, 0.95); /* 几乎不透明的白色卡片 */
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); /* 更有质感的阴影 */
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
  padding: 14px 16px 14px 48px; /* 留出图标位置 */
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  font-size: 15px;
  color: #334155;
  background: #f8fafc;
  transition: all 0.3s;
  box-sizing: border-box;
}

/* 输入框聚焦时的效果 */
.input-wrapper input:focus {
  border-color: #3b82f6;
  background: white;
  outline: none;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
}

.input-wrapper input:focus + i {
  color: #3b82f6; /* 图标变色 */
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