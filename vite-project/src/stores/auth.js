// src/stores/auth.js
import { defineStore } from 'pinia'
import axios from 'axios'

const API_URL = 'http://127.0.0.1:8000/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    currentUser: null,
    token: localStorage.getItem('token') || null
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
    isAdmin: (state) => state.currentUser?.role === 'admin'
  },

  actions: {
    async login(username, password) {
      try {
        const response = await axios.post(`${API_URL}/login/`, { username, password })
        
        this.token = response.data.token
        this.currentUser = response.data.user
        localStorage.setItem('token', this.token)
        axios.defaults.headers.common['Authorization'] = `Token ${this.token}`
        
        // 登录成功，返回一个带 success 标记的对象
        return { success: true }

      } catch (error) {
        console.error('登录报错详情:', error.response) // 方便你在 F12 控制台看
        
        // --- ⭐ 核心修改：提取详细错误信息 ⭐ ---
        let errorMsg = "登录失败，请检查网络"
        
        if (error.response && error.response.data) {
            const data = error.response.data
            
            // 情况 1: Django 自带的错误 (比如 {"non_field_errors": ["无法使用提供的认证信息登录。"]})
            if (data.non_field_errors) {
                errorMsg = data.non_field_errors[0]
            } 
            // 情况 2: 我们自定义的错误 (比如 {"detail": "..."})
            else if (data.detail) {
                errorMsg = data.detail
            }
            // 情况 3: 字段错误 (比如 {"password": ["此字段是必填项。"]})
            else {
                // 把所有错误拼起来显示
                errorMsg = JSON.stringify(data)
            }
        }
        
        // 登录失败，返回 success: false 和具体的错误消息
        return { success: false, message: errorMsg }
      }
    },
    
    logout() {
      this.currentUser = null
      this.token = null
      localStorage.removeItem('token')
      delete axios.defaults.headers.common['Authorization']
    }
  }
})