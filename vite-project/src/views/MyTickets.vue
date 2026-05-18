<template>
  <div class="page-content">
    <div class="header-row">
      <h2><i class="fas fa-ticket-alt"></i> 我的报修记录</h2>
      <button v-if="auth.currentUser?.role === 'student'" 
              @click="$router.push('/submit')" 
              class="btn-primary">
        <i class="fas fa-plus"></i> 新建报修
      </button>
    </div>

    <div class="search-box">
      <input 
        v-model="searchText" 
        type="text" 
        placeholder="🔍 搜索标题、位置或单号..." 
        @keyup.enter="doSearch"
      >
      <button @click="doSearch" class="btn-search">搜索</button>
    </div>
    <div v-if="ticketStore.tickets.length === 0" class="empty-state">
      <div class="empty-icon"><i class="fas fa-inbox"></i></div>
      <p>暂无相关记录</p>
    </div>

    <div v-else class="ticket-grid">
      <div v-for="ticket in ticketStore.tickets" :key="ticket.id" class="ticket-card">
        
        <div class="card-header">
          <span class="ticket-id">#{{ ticket.id }}</span>
          <span :class="['status-badge', getStatusClass(ticket.status)]">
            {{ getStatusName(ticket.status) }}
          </span>
        </div>

        <h3 class="ticket-title">{{ ticket.title }}</h3>
        
        <div class="card-info">
          <p><i class="fas fa-map-marker-alt"></i> {{ ticket.location }}</p>
          <p><i class="fas fa-clock"></i> {{ formatDate(ticket.submitTime) }}</p>
        </div>

        <div class="reject-box" v-if="ticket.status === 'rejected'">
          <div class="reject-title">驳回原因</div>
          <div class="reject-reason">{{ ticket.rejected_reason || '未填写驳回理由' }}</div>
        </div>

        <div class="card-actions" v-if="(ticket.attachments?.length || 0) > 0">
          <button @click="openAttachments(ticket.attachments)" class="btn-text-primary">查看附件（{{ ticket.attachments.length }}）</button>
        </div>

        <div class="card-actions" v-if="ticket.status === 'pending_dorm' && auth.currentUser?.role === 'student'">
          <button @click="deleteTicket(ticket.id)" class="btn-text-danger">撤销工单</button>
        </div>

        <div class="card-actions" v-if="ticket.status === 'finished' && auth.currentUser?.role === 'student'">
          <button @click="openEvaluate(ticket.id)" class="btn-text-primary">评价并结单</button>
        </div>

        <div class="card-actions" v-if="ticket.status === 'rejected' && auth.currentUser?.role === 'student'">
          <button @click="editRejected(ticket.id)" class="btn-text-primary">重新编辑并提交</button>
        </div>
      </div>
    </div>

    <div v-if="evaluateModal.open" class="modal-mask" @click.self="closeEvaluate">
      <div class="modal">
        <div class="modal-title">评价本次维修</div>
        <div class="field">
          <div class="label">评分</div>
          <div class="stars">
            <button
              v-for="n in 5"
              :key="n"
              type="button"
              class="star"
              :class="{ active: n <= evaluateModal.rating }"
              @click="evaluateModal.rating = n"
            >
              ★
            </button>
          </div>
        </div>

        <div class="field">
          <div class="label">评价内容（可选）</div>
          <textarea v-model="evaluateModal.text" rows="4" placeholder="说说你的感受..."></textarea>
        </div>

        <label class="anon-row">
          <input type="checkbox" v-model="evaluateModal.anonymous">
          <span>匿名评价</span>
        </label>

        <div class="modal-actions">
          <button class="btn-cancel" type="button" @click="closeEvaluate">取消</button>
          <button class="btn-confirm" type="button" @click="submitEvaluate" :disabled="evaluateModal.submitting">
            {{ evaluateModal.submitting ? '提交中...' : '提交评价' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="attachmentsModal.open" class="modal-mask" @click.self="closeAttachments">
      <div class="modal">
        <div class="modal-title">附件预览</div>
        <div v-if="attachmentsModal.items.length" class="attach-grid">
          <div v-for="a in attachmentsModal.items" :key="a.id" class="attach-item">
            <img v-if="a.media_type === 'image'" :src="a.url" alt="图片" />
            <video v-else controls :src="a.url"></video>
            <div class="attach-name">{{ a.original_name || a.url }}</div>
          </div>
        </div>
        <div v-else class="empty-attach">暂无附件</div>
        <div class="modal-actions">
          <button class="btn-cancel" type="button" @click="closeAttachments">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useTicketStore } from '@/stores/ticketStore'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { apiUrl } from '@/config'

const ticketStore = useTicketStore()
const auth = useAuthStore()
const router = useRouter()
const evaluateModal = ref({ open: false, ticketId: null, rating: 5, text: '', anonymous: true, submitting: false })
const attachmentsModal = ref({ open: false, items: [] })

// 2. 定义搜索变量
const searchText = ref('')

// 3. 定义搜索函数
function doSearch() {
  ticketStore.fetchTickets(searchText.value)
}

onMounted(() => {
  if (auth.isLoggedIn) {
    ticketStore.fetchTickets() // 默认加载全部
  }
})

// 撤销功能
async function deleteTicket(id) {
  // if(!confirm("确定要撤销此报修单吗？")) return;
  try {
    await axios.delete(apiUrl(`tickets/${id}/`), {
      headers: { Authorization: `Token ${auth.token}` }
    })
    // alert("已撤销")
    // 撤销后重新刷新列表，保留当前的搜索条件
    ticketStore.fetchTickets(searchText.value)
  } catch (e) {
    // alert("撤销失败")
  }
}

function openEvaluate(id) {
  evaluateModal.value.open = true
  evaluateModal.value.ticketId = id
  evaluateModal.value.rating = 5
  evaluateModal.value.text = ''
  evaluateModal.value.anonymous = true
  evaluateModal.value.submitting = false
}

function closeEvaluate() {
  evaluateModal.value.open = false
  evaluateModal.value.ticketId = null
  evaluateModal.value.submitting = false
}

function openAttachments(items) {
  attachmentsModal.value.open = true
  attachmentsModal.value.items = Array.isArray(items) ? items : []
}

function closeAttachments() {
  attachmentsModal.value.open = false
  attachmentsModal.value.items = []
}

async function submitEvaluate() {
  const id = evaluateModal.value.ticketId
  if (!id) return
  const rating = Number(evaluateModal.value.rating)
  if (!Number.isFinite(rating) || rating < 1 || rating > 5) {
    alert('评分需为 1-5')
    return
  }
  evaluateModal.value.submitting = true
  try {
    await axios.post(apiUrl(`tickets/${id}/handle/`), {
      type: 'evaluate',
      rating: Math.round(rating),
      evaluation: evaluateModal.value.text,
      is_anonymous: evaluateModal.value.anonymous
    }, {
      headers: { Authorization: `Token ${auth.token}` }
    })
    // alert('已提交评价并结单')
    ticketStore.fetchTickets(searchText.value)
    closeEvaluate()
  } catch (e) {
    // alert('提交评价失败')
    evaluateModal.value.submitting = false
  }
}

function editRejected(id) {
  router.push({ path: '/submit', query: { edit: id } })
}

// 状态样式映射
function getStatusClass(status) {
  const map = {
    'pending_dorm': 'pending',
    'pending_dispatch': 'pending',
    'repairing': 'processing',
    'finished': 'completed',
    'closed': 'closed',
    'rejected': 'closed'
  }
  return map[status] || ''
}

// 状态文字映射
function getStatusName(status) {
    const map = {
        'pending_dorm': '待审核',
        'pending_dispatch': '正在处理',
        'repairing': '维修中',
        'finished': '已完成', 
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
.page-content { 
  max-width: var(--app-page-max-width); 
  margin: 0 auto; 
  padding: 30px 20px; 
}

.header-row { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  margin-bottom: 25px; 
  border-bottom: 2px solid #f0f2f5;
  padding-bottom: 15px;
}

/* 👇👇👇 新增的搜索框样式 👇👇👇 */
.search-box {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.search-box input {
  flex: 1; 
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
}

.btn-search {
  padding: 0 25px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
}
.btn-search:hover {
  background: #5a6fd6;
}
/* 👆👆👆 新增样式结束 👆👆👆 */

.ticket-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.ticket-card { 
  background: white; 
  border-radius: 12px; 
  padding: 20px; 
  box-shadow: 0 4px 12px rgba(0,0,0,0.04); 
  border: 1px solid #f0f0f0;
  transition: transform 0.2s;
  display: flex;
  flex-direction: column;
}

.ticket-card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(0,0,0,0.08); }

.card-header { display: flex; justify-content: space-between; margin-bottom: 12px; font-size: 13px; color: #888;}

.status-badge { 
  padding: 4px 10px; 
  border-radius: 6px; 
  font-size: 12px; 
  font-weight: 600; 
}
.status-badge.pending { background: #fff7e6; color: #fa8c16; }
.status-badge.processing { background: #e6f7ff; color: #1890ff; }
.status-badge.completed { background: #f6ffed; color: #52c41a; }
.status-badge.closed { background: #f5f5f5; color: #d9d9d9; }

.ticket-title { margin: 0 0 15px 0; font-size: 16px; color: #333; line-height: 1.4; }

.card-info p { margin: 5px 0; color: #666; font-size: 13px; display: flex; align-items: center; gap: 8px;}

.card-actions { margin-top: auto; padding-top: 15px; text-align: right; }

.btn-primary { padding: 8px 20px; background: #1890ff; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 14px;}
.btn-text-danger { background: none; border: none; color: #ff4d4f; cursor: pointer; font-size: 13px; }
.btn-text-danger:hover { text-decoration: underline; }
.btn-text-primary { background: none; border: none; color: #1890ff; cursor: pointer; font-size: 13px; }
.btn-text-primary:hover { text-decoration: underline; }

.reject-box { margin-top: 10px; padding: 10px 12px; background: #fff7ed; border: 1px solid #fed7aa; border-radius: 8px; }
.reject-title { font-size: 12px; font-weight: 800; color: #c2410c; margin-bottom: 4px; }
.reject-reason { font-size: 13px; color: #9a3412; line-height: 1.6; word-break: break-word; }

.modal-mask { position: fixed; inset: 0; background: rgba(15, 23, 42, 0.5); display: flex; align-items: center; justify-content: center; padding: 16px; z-index: 200; }
.modal { width: 100%; max-width: 520px; background: white; border-radius: 14px; border: 1px solid #e2e8f0; box-shadow: 0 30px 60px rgba(15, 23, 42, 0.25); padding: 16px; }
.modal-title { font-size: 16px; font-weight: 900; color: #0f172a; margin-bottom: 12px; }
.field { margin-bottom: 12px; }
.label { font-size: 13px; font-weight: 800; color: #334155; margin-bottom: 6px; }
.stars { display: flex; gap: 6px; }
.star { border: none; background: #e2e8f0; color: #64748b; padding: 6px 10px; border-radius: 10px; cursor: pointer; font-size: 16px; line-height: 1; }
.star.active { background: #2563eb; color: white; }
.modal textarea { width: 100%; border: 1px solid #e2e8f0; border-radius: 10px; padding: 10px 12px; box-sizing: border-box; font-size: 14px; resize: vertical; }
.anon-row { display: flex; align-items: center; gap: 8px; font-size: 13px; color: #334155; margin: 6px 0 12px; }
.modal-actions { display: flex; justify-content: flex-end; gap: 10px; }
.btn-cancel { background: #e2e8f0; border: none; border-radius: 10px; padding: 10px 12px; cursor: pointer; font-weight: 800; color: #334155; }
.btn-confirm { background: #2563eb; border: none; border-radius: 10px; padding: 10px 12px; cursor: pointer; font-weight: 900; color: white; }
.btn-confirm:disabled { opacity: 0.7; cursor: not-allowed; }
.attach-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 12px; margin-top: 10px; }
.attach-item { border: 1px solid #e2e8f0; border-radius: 12px; padding: 10px; background: #f8fafc; display: flex; flex-direction: column; gap: 8px; }
.attach-item img, .attach-item video { width: 100%; border-radius: 10px; background: #000; }
.attach-name { font-size: 12px; color: #334155; word-break: break-all; }
.empty-attach { padding: 18px 0; text-align: center; color: #94a3b8; font-size: 13px; }

.empty-state { text-align: center; padding: 60px; color: #bbb; }
.empty-icon { font-size: 48px; margin-bottom: 10px; opacity: 0.5; }
</style>
