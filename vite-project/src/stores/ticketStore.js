import { defineStore } from 'pinia'
import axios from 'axios'

const API_URL = 'http://127.0.0.1:8000/api' // 你的 Django 后端地址

export const useTicketStore = defineStore('ticket', {
  state: () => ({
    tickets: [], // 替换全局变量 tickets
    currentTicket: null, // 用于详情页
    loading: false
  }),
  
  actions: {
    // 1. 获取所有报修单 (对应 loadMyTickets / loadAdminDashboard)
    async fetchTickets() {
      this.loading = true
      try {
        // 假设 Django 的 API 地址是 /api/tickets/
        const response = await axios.get(`${API_URL}/tickets/`) 
        this.tickets = response.data
      } catch (error) {
        console.error('获取报修单失败:', error)
      } finally {
        this.loading = false
      }
    },

    // 2. 提交新报修单 (对应 handleTicketSubmit)
    async createTicket(ticketData) {
      try {
        // ticketData 是一个对象，包含 title, category, description 等
        const response = await axios.post(`${API_URL}/tickets/`, ticketData)
        
        // 成功后，把新工单添加到 state 列表的开头
        this.tickets.unshift(response.data)
        return true // 返回成功
      } catch (error) {
        console.error('提交失败:', error)
        return false // 返回失败
      }
    },
    
    // 3. 更新报修单状态 (对应 updateTicketStatus)
    async updateTicketStatus(ticketId, newStatus) {
      try {
        // Django REST Framework 通常使用 PATCH 来局部更新
        const response = await axios.patch(`${API_URL}/tickets/${ticketId}/`, { status: newStatus })
        
        // 更新本地 state 列表中的数据
        const index = this.tickets.findIndex(t => t.id === ticketId)
        if (index !== -1) {
          this.tickets[index] = response.data
        }
      } catch (error) {
        console.error('更新状态失败:', error)
      }
    }
    
    // 你还可以添加 fetchTicketById (获取单个详情), addComment 等 actions
  }
})