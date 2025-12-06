<template>
  <div class="page-content">
    <div class="header-row">
      <h2><i class="fas fa-ticket-alt"></i> 我的报修记录</h2>
      <button @click="$router.push('/submit')" class="btn-primary">
        <i class="fas fa-plus"></i> 新建报修
      </button>
    </div>

    <div v-if="ticketStore.tickets.length === 0" class="empty-state">
      <p>暂无报修记录</p>
    </div>

    <div v-else class="ticket-list">
      <div v-for="ticket in ticketStore.tickets" :key="ticket.id" class="ticket-card">
        <div class="card-header">
          <span class="title">{{ ticket.title }}</span>
          <span :class="['status-tag', getStatusClass(ticket.status)]">
            {{ getStatusName(ticket.status) }}
          </span>
        </div>
        <div class="card-body">
          <p><strong>位置：</strong>{{ ticket.location }}</p>
          <p><strong>描述：</strong>{{ ticket.description }}</p>
          <p class="time">{{ formatDate(ticket.submitTime) }}</p>
          
          <div v-if="ticket.evaluation" class="eval-box">
            <strong>我的评价：</strong> {{ ticket.evaluation }} ({{ ticket.rating }}星)
          </div>
        </div>
        
        <div class="card-footer">
          <button v-if="ticket.status === 'pending_dispatch'" 
                  @click="deleteTicket(ticket.id)" 
                  class="btn-delete">
            撤销
          </button>

          <div v-if="ticket.status === 'finished'" class="eval-action">
             <input v-model="evalInputs[ticket.id]" placeholder="维修满意吗？" class="eval-input">
             <button @click="submitEval(ticket.id)" class="btn-primary small">提交评价</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useTicketStore } from '@/stores/ticketStore'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const ticketStore = useTicketStore()
const auth = useAuthStore()
const evalInputs = ref({}) // 存储评价内容

onMounted(() => {
  ticketStore.fetchTickets()
})

async function deleteTicket(id) {
  if(!confirm("确定要撤销此报修单吗？")) return;
  try {
    await axios.delete(`http://127.0.0.1:8000/api/tickets/${id}/`, {
      headers: { Authorization: `Token ${auth.token}` }
    })
    alert("已撤销")
    ticketStore.fetchTickets()
  } catch (e) {
    alert("撤销失败")
  }
}

// ⭐ 新增：提交评价函数
async function submitEval(id) {
  if (!evalInputs.value[id]) return alert("请填写评价内容")
  
  try {
    await axios.post(`http://127.0.0.1:8000/api/tickets/${id}/handle/`, {
      type: 'evaluate',
      comment: evalInputs.value[id],
      rating: 5
    }, {
      headers: { Authorization: `Token ${auth.token}` }
    })
    alert("评价成功！")
    ticketStore.fetchTickets() // 刷新列表
  } catch (e) {
    alert("评价失败：" + (e.response?.data?.error || "未知错误"))
  }
}

function getStatusClass(status) {
  const map = {
    'pending_dispatch': 'pending',
    'repairing': 'processing',
    'finished': 'completed',
    'closed': 'closed',
    'rejected': 'closed'
  }
  return map[status] || ''
}

function getStatusName(status) {
    const map = {
        'pending_dispatch': '待派单',
        'repairing': '维修中',
        'finished': '待评价',
        'closed': '已结单',
        'rejected': '已驳回'
    }
    return map[status] || status
}

function formatDate(iso) {
  return new Date(iso).toLocaleString('zh-CN', { hour12: false })
}
</script>

<style scoped>
.page-content { padding: 20px; max-width: 800px; margin: 0 auto; }
.header-row { display: flex; justify-content: space-between; margin-bottom: 20px; }
.ticket-list { display: flex; flex-direction: column; gap: 15px; }
.ticket-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); border-left: 4px solid #667eea; }
.card-header { display: flex; justify-content: space-between; font-weight: bold; margin-bottom: 10px; }

.status-tag { padding: 2px 8px; border-radius: 4px; font-size: 12px; color: white; background: #ccc;}
.status-tag.pending { background: #f1c40f; }
.status-tag.processing { background: #3498db; }
.status-tag.completed { background: #2ecc71; }
.status-tag.closed { background: #95a5a6; }

.card-body p { margin: 5px 0; color: #666; font-size: 14px; }
.time { font-size: 12px; color: #999; }
.eval-box { margin-top: 10px; padding: 8px; background: #e8f5e9; color: #2e7d32; border-radius: 4px; font-size: 13px; }

.card-footer { margin-top: 10px; display: flex; justify-content: flex-end; gap: 10px;}
.btn-primary { padding: 8px 15px; background: #667eea; color: white; border: none; border-radius: 4px; cursor: pointer; }
.btn-delete { padding: 5px 10px; background: white; border: 1px solid #ff4d4f; color: #ff4d4f; border-radius: 4px; cursor: pointer; }

/* 评价输入框样式 */
.eval-action { display: flex; gap: 5px; }
.eval-input { padding: 5px; border: 1px solid #ddd; border-radius: 4px; }
.small { padding: 5px 10px; font-size: 12px; }
</style>