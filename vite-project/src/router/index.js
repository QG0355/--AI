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
  
  // 1. 定义完全公开的页面 (不需要登录也能看)
  //    现在把 '/' (主页) 也加进去了
  const publicPages = ['/login', '/register', '/'] 
  
  const authRequired = !publicPages.includes(to.path)

  // 2. 如果去受保护页面且没登录 -> 去登录页
  if (authRequired && !authStore.isLoggedIn) {
    return next('/login')
  }

  // 3. 已登录但没绑定身份 -> 强制去绑定页 (除了注销操作)
  if (authStore.isLoggedIn && !authStore.currentUser?.is_identity_bound && to.path !== '/bind') {
    return next('/bind')
  }

  // 4. 绑定好了又想回绑定页 -> 去主页
  if (authStore.isLoggedIn && authStore.currentUser?.is_identity_bound && to.path === '/bind') {
    return next('/dashboard')
  }

  next()
})
export default router