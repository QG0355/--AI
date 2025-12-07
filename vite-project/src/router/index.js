import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  { path: '/login', component: () => import('@/views/LoginPage.vue') },
  { path: '/register', component: () => import('@/views/RegisterPage.vue') },
  // 1. 彻底删除了 /bind 路由
  { 
    path: '/', 
    component: () => import('@/layouts/MainLayout.vue'),
    children: [
      // 首页就是 Dashboard
      { path: '', component: () => import('@/views/Dashboard.vue') },
      { path: 'submit', component: () => import('@/views/SubmitTicket.vue') },
      { path: 'tickets', component: () => import('@/views/MyTickets.vue') },
      { path: 'workplace', component: () => import('@/views/Workplace.vue') }
    ]
  }
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  // 2. 允许未登录访问首页 '/'
  const publicPages = ['/login', '/register', '/']
  
  // 只有去非公共页面且没登录时，才跳登录页
  if (!publicPages.includes(to.path) && !authStore.isLoggedIn) {
    return next('/login')
  }

  // 3. 彻底删除了所有关于 "identity_bound" 的检查逻辑！
  // 只要登录了，就放行，不再跳什么绑定页。
  
  next()
})

export default router