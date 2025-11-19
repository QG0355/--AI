import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  { path: '/login', component: () => import('@/views/LoginPage.vue') },
  { path: '/register', component: () => import('@/views/RegisterPage.vue') },
  { 
    path: '/bind', 
    component: () => import('@/views/IdentityBind.vue'),
    meta: { requiresAuth: true } 
  },
  { 
    path: '/', 
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: 'dashboard' }, // 默认跳到 dashboard
      { path: 'dashboard', component: () => import('@/views/Dashboard.vue') },
      { path: 'submit', component: () => import('@/views/SubmitTicket.vue') },
      { path: 'tickets', component: () => import('@/views/MyTickets.vue') },
      { path: 'oa', component: () => import('@/views/OAApproval.vue') },
      { 
        path: 'admin', 
        component: () => import('@/views/AdminDashboard.vue'), 
        meta: { requiresAdmin: true } 
      }
    ]
  }
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  const publicPages = ['/login', '/register']
  const authRequired = !publicPages.includes(to.path)

  // 1. 没登录？直接踢回登录页 (除非是去注册)
  if (authRequired && !authStore.isLoggedIn) {
    return next('/login')
  }

  // 2. 登录了但没绑定？ -> 关进绑定页监狱
  // (注意：要排除注销操作，否则退出都退不掉)
  if (authStore.isLoggedIn && !authStore.currentUser?.is_identity_bound && to.path !== '/bind') {
    return next('/bind')
  }

  // 3. 绑定过了还想去绑定页？ -> 赶回主页
  if (authStore.isLoggedIn && authStore.currentUser?.is_identity_bound && to.path === '/bind') {
    return next('/dashboard')
  }
  
  // 4. 已登录且访问登录页 -> 赶回主页
  if (authStore.isLoggedIn && publicPages.includes(to.path)) {
      return next('/')
  }

  next()
})

export default router