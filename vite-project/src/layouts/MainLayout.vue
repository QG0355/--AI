<template>
  <div class="main-page-wrapper">
    <nav class="navbar">
      <div class="nav-brand">
        <i class="fas fa-tools"></i>
        <span>IT 报修平台</span>
      </div>
      
      <div class="nav-menu">
        <RouterLink to="/dashboard" class="nav-btn">
          <i class="fas fa-home"></i> 首页(仪表盘)
        </RouterLink>

        <template v-if="authStore.isLoggedIn">
          <RouterLink to="/submit" class="nav-btn">
            <i class="fas fa-plus-circle"></i> 提交报修
          </RouterLink>
          <RouterLink to="/tickets" class="nav-btn">
            <i class="fas fa-ticket-alt"></i> 我的报修
          </RouterLink>
          <RouterLink v-if="['teacher','admin'].includes(authStore.currentUser?.role)" to="/oa" class="nav-btn">
            <i class="fas fa-tasks"></i> OA审批
          </RouterLink>
        </template>
      </div>

      <div class="nav-user">
        <template v-if="authStore.isLoggedIn">
          <span id="userInfo">欢迎，{{ authStore.currentUser?.name || '用户' }}</span>
          <button class="btn-logout" @click="handleLogout">
            <i class="fas fa-sign-out-alt"></i> 退出
          </button>
        </template>

        <template v-else>
          <RouterLink to="/login" class="btn-login">
            <i class="fas fa-user"></i> 登录
          </RouterLink>
        </template>
      </div>
    </nav>

    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
/* ... (保留之前的样式) ... */

/* 新增登录按钮样式 */
.btn-login {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 8px 20px;
  background: #667eea;
  color: white;
  border-radius: 6px;
  text-decoration: none;
  transition: all 0.3s ease;
}
.btn-login:hover {
  background: #5a6fd6;
  transform: translateY(-1px);
}

/* 复用之前的 navbar 样式 (确保你保留了 style.css 或者之前的 scoped style) */
.main-page-wrapper { min-height: 100vh; background: #f5f7fa; }
.navbar { background: white; box-shadow: 0 2px 10px rgba(0,0,0,0.1); padding: 0 30px; height: 70px; display: flex; justify-content: space-between; align-items: center; }
.nav-brand { font-size: 20px; font-weight: bold; color: #333; display: flex; align-items: center; gap: 10px; }
.nav-brand i { color: #667eea; }
.nav-menu { display: flex; gap: 10px; }
.nav-btn { padding: 10px 15px; color: #666; text-decoration: none; border-radius: 5px; display: flex; align-items: center; gap: 5px; }
.nav-btn:hover, .nav-btn.router-link-active { background: #f0f2f5; color: #667eea; }
.nav-user { display: flex; align-items: center; gap: 15px; }
.btn-logout { padding: 5px 10px; border: 1px solid #ddd; background: white; border-radius: 4px; cursor: pointer; }
.main-content { padding: 30px; }
</style>