<template>
  <div class="main-page-wrapper">
    <nav class="navbar">
      <div class="nav-brand">
        <i class="fas fa-tools"></i>
        <span>校园报修平台</span>
      </div>
      
      <div class="nav-menu" v-if="authStore.isLoggedIn">
        <!-- 仅学生可见 -->
        <RouterLink v-if="authStore.currentUser?.role === 'student'" to="/" class="nav-btn">
          <i class="fas fa-plus-circle"></i> 提交报修
        </RouterLink>
        <RouterLink v-if="authStore.currentUser?.role === 'student'" to="/tickets" class="nav-btn">
          <i class="fas fa-ticket-alt"></i> 我的报修
        </RouterLink>
        <RouterLink v-if="authStore.currentUser?.role === 'student'" to="/ai-chat" class="nav-btn">
          <i class="fas fa-robot"></i> AI助手
        </RouterLink>

        <!-- 维修人员/审核员/管理员可见 -->
        <RouterLink v-if="['maintenance', 'repair_admin', 'admin'].includes(authStore.currentUser?.role)" to="/workplace" class="nav-btn">
          <i class="fas fa-briefcase"></i> 工作台
        </RouterLink>
        <RouterLink v-if="['admin', 'auditor'].includes(authStore.currentUser?.role)" to="/approval" class="nav-btn">
          <i class="fas fa-check-square"></i> 审核中心
        </RouterLink>
        
        <!-- 管理员可见 -->
        <RouterLink v-if="authStore.currentUser?.role === 'admin'" to="/admin" class="nav-btn">
          <i class="fas fa-cogs"></i> 管理后台
        </RouterLink>
      </div>

      <div class="nav-user">
        <template v-if="authStore.isLoggedIn">
          <div class="user-info-group">
            <span class="role-badge" :class="authStore.currentUser?.role">
              {{ getRoleName(authStore.currentUser?.role) }}
            </span>
            <span id="userInfo">
              <i class="fas fa-user-circle"></i> 
              {{ authStore.currentUser?.name || authStore.currentUser?.username || '用户' }}
            </span>
            <button class="btn-logout" @click="handleLogout">
              <i class="fas fa-sign-out-alt"></i> 退出
            </button>
          </div>
        </template>

        <template v-else>
          <div class="guest-actions">
            <RouterLink to="/login" class="btn-login">登录</RouterLink>
            <RouterLink to="/register" class="btn-register-nav">注册</RouterLink>
          </div>
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

function getRoleName(role) {
  const map = {
    'student': '学生',
    'admin': '管理员',
    'maintenance': '维修师傅',
    'auditor': '审核员',
    'repair_admin': '维修主管'
  }
  return map[role] || '用户'
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.main-page-wrapper { min-height: 100vh; background: #f5f7fa; }
.navbar { 
  background: white; 
  box-shadow: 0 2px 10px rgba(0,0,0,0.05); 
  padding: 0 20px; 
  height: 60px; 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  position: sticky; top: 0; z-index: 100;
}

.nav-brand { font-size: 18px; font-weight: bold; color: #333; display: flex; align-items: center; gap: 8px; }
.nav-brand i { color: #667eea; }

.nav-menu { display: flex; gap: 10px; }
.nav-btn { 
  padding: 8px 12px; color: #666; text-decoration: none; border-radius: 5px; 
  display: flex; align-items: center; gap: 5px; font-size: 14px;
}
.nav-btn:hover, .nav-btn.router-link-active { background: #f0f2f5; color: #667eea; font-weight: 500; }

.nav-user { display: flex; align-items: center; gap: 15px; font-size: 14px; }
.user-info-group { display: flex; align-items: center; gap: 10px; }
.role-badge { padding: 2px 6px; border-radius: 4px; font-size: 12px; color: white; background: #999; }
.role-badge.student { background: #48bb78; }
.role-badge.maintenance { background: #ed8936; }
.role-badge.admin { background: #f56565; }
.guest-actions { display: flex; gap: 10px; }

.btn-login { color: #666; text-decoration: none; font-weight: 500; }
.btn-register-nav { 
  background: #667eea; color: white; padding: 6px 15px; border-radius: 20px; 
  text-decoration: none; font-size: 13px; 
}
.btn-logout { 
  padding: 4px 8px; border: 1px solid #ddd; background: white; 
  border-radius: 4px; cursor: pointer; font-size: 12px; color: #666; 
}

/* --- 📱 手机端适配魔法 (Media Queries) --- */
@media (max-width: 768px) {
  .navbar { padding: 0 15px; }
  .nav-brand span { display: none; /* 手机上隐藏文字只留图标，省空间 */ }
  #userInfo { display: none; /* 手机上隐藏"欢迎xxx"，太长了 */ }
  
  .nav-menu { 
    position: fixed; bottom: 0; left: 0; width: 100%; 
    background: white; border-top: 1px solid #eee; 
    justify-content: space-around; padding: 10px 0;
    box-shadow: 0 -2px 10px rgba(0,0,0,0.05);
  }
  .nav-btn { flex-direction: column; font-size: 12px; gap: 2px; }
  
  .main-content { padding-bottom: 70px; /* 防止内容被底部菜单挡住 */ }
}
</style>
