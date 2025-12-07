<template>
  <div class="welcome-container">
    <div class="content-box">
      <div class="icon-wrapper">
        <i class="fas fa-school"></i>
      </div>
      <h1>欢迎使用校园报修平台</h1>
      <p class="subtitle">Campus Repair Service Platform</p>
      
      <p class="desc">
        高效 · 便捷 · 透明<br>
        为您提供最优质的校园后勤保障服务
      </p>

      <div class="actions">
        <div v-if="!authStore.isLoggedIn" class="guest-btns">
          <button @click="$router.push('/login')" class="btn-primary">立即登录</button>
          <button @click="$router.push('/register')" class="btn-outline">注册账号</button>
        </div>

        <div v-else class="user-btns">
          <button 
            @click="handleMainBtnClick" 
            class="btn-primary"
          >
            <i :class="isStudent ? 'fas fa-wrench' : 'fas fa-briefcase'"></i> 
            {{ isStudent ? '我要报修' : '进入工作台' }}
          </button>

          <button @click="$router.push('/tickets')" class="btn-outline">
            <i class="fas fa-list"></i> 查看记录
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { computed } from 'vue' // 1. 必须引入 computed

const authStore = useAuthStore()
const router = useRouter()

// 2. 必须定义 isStudent
const isStudent = computed(() => {
  return authStore.currentUser?.role === 'student'
})

function handleMainBtnClick() {
  if (isStudent.value) {
    // 学生 -> 填单子
    if (!authStore.currentUser?.is_identity_bound) {
      if(confirm("您尚未绑定身份信息，绑定后即可报修。\n是否现在去绑定？")) {
        router.push('/bind')
      }
    } else {
      router.push('/submit')
    }
  } else {
    // 维修员 -> 去工作台
    router.push('/workplace')
  }
}
</script>

<style scoped>
.welcome-container {
  display: flex; justify-content: center; align-items: center;
  min-height: 80vh; text-align: center; background: #f5f7fa;
}
.content-box {
  background: white; padding: 50px; border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.05); max-width: 500px; width: 90%;
  transition: transform 0.3s;
}
.content-box:hover { transform: translateY(-5px); }
.icon-wrapper { font-size: 64px; color: #667eea; margin-bottom: 20px; }
h1 { font-size: 28px; color: #333; margin-bottom: 5px; }
.subtitle { color: #888; letter-spacing: 1px; margin-bottom: 30px; font-size: 14px; text-transform: uppercase; }
.desc { color: #555; line-height: 1.8; margin-bottom: 40px; font-size: 16px; }
.actions { display: flex; justify-content: center; gap: 15px; }
.btn-primary {
  padding: 12px 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white; border: none; border-radius: 8px; font-size: 16px; cursor: pointer;
  display: flex; align-items: center; gap: 8px; transition: opacity 0.2s;
}
.btn-primary:hover { opacity: 0.9; }
.btn-outline {
  padding: 12px 30px; background: white; color: #667eea; border: 1px solid #667eea;
  border-radius: 8px; font-size: 16px; cursor: pointer;
  display: flex; align-items: center; gap: 8px; transition: background 0.2s;
}
.btn-outline:hover { background: #f0f4ff; }
</style>