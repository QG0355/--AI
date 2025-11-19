// src/stores/auth.js
import { defineStore } from 'pinia'
import axios from 'axios'

// 1. (重要) 设置 Axios 默认请求 Django API 的地址
const API_URL = 'http://127.0.0.1:8000/api' // 你的 Django 后端地址

export const useAuthStore = defineStore('auth', {
  state: () => ({
    currentUser: null,
    token: localStorage.getItem('token') || null
  }),

  // getters 就像 Vue 的 "computed"
  getters: {
    isLoggedIn: (state) => !!state.token,
    isAdmin: (state) => state.currentUser?.role === 'admin'
  },

  actions: {
    async login(username, password) {
      try {
        // 1. 调用 Django API
        const response = await axios.post(`${API_URL}/login/`, { username, password })
        
        // 2. 保存 token 和用户信息
        this.token = response.data.token
        this.currentUser = response.data.user
        localStorage.setItem('token', this.token)
        
        // 3. 设置 axios 的默认 Header，之后所有请求都会带上 token
        axios.defaults.headers.common['Authorization'] = `Token ${this.token}`
        
        return true // 登录成功，返回 true
      } catch (error) {
        console.error('登录失败:', error)
        return false // 登录失败，返回 false
      }
    },
    
    logout() {
      // 替换 logout 函数
      this.currentUser = null
      this.token = null
      localStorage.removeItem('token')
      delete axios.defaults.headers.common['Authorization']
      // 路由跳转将由组件（例如 Navbar）处理
    }
  }
})