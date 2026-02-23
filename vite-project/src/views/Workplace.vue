<template>
  <div class="workspace-container">
    <div class="page-header">
      <h2>🛠️ 维修师傅工作台</h2>
      <p>欢迎回来，{{ auth.currentUser?.name || auth.currentUser?.username }}</p>
    </div>

    <StudentStarCarousel />

    <div class="search-box">
      <input 
        v-model="searchText" 
        type="text" 
        placeholder="🔍 搜索工单号、位置、描述..." 
        @keyup.enter="fetchData"
      >
      <button @click="fetchData" class="btn-search">搜索</button>
    </div>

    <div class="section">
      <h3 class="section-title">📢 待接单大厅 (抢单池)</h3>
      <div v-if="pendingTickets.length === 0" class="empty-box">暂无新报修</div>
      <div class="task-grid">
        <div v-for="t in pendingTickets" :key="t.id" class="task-card pending">
          <div class="card-top">
            <span class="tag">待接单</span>
            <span class="time">{{ formatDate(t.submitTime) }}</span>
          </div>
          <h4>{{ t.title }}</h4>
          <p class="desc">{{ t.description }}</p>
          <p class="loc"><i class="fas fa-map-marker-alt"></i> {{ t.location }}</p>
          <button @click="takeOrder(t.id)" class="btn-take">🚀 我要接单</button>
        </div>
      </div>
    </div>

    <div class="section">
      <h3 class="section-title">🔧 我的维修任务</h3>
      <div v-if="myRepairingTickets.length === 0" class="empty-box">您当前没有正在进行的维修</div>
      <div class="task-grid">
        <div v-for="t in myRepairingTickets" :key="t.id" class="task-card repairing">
          <div class="card-top">
            <span class="tag blue">维修中</span>
            <span class="assignee">负责人: 我</span>
          </div>
          <h4>{{ t.title }}</h4>
          <p class="loc"><i class="fas fa-map-marker-alt"></i> {{ t.location }}</p>
          <p class="contact"><i class="fas fa-phone"></i> {{ t.contact }}</p>
          <button @click="finishOrder(t.id)" class="btn-finish">✅ 维修完成</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import StudentStarCarousel from '@/components/StudentStarCarousel.vue'

const auth = useAuthStore()
const allTickets = ref([])
const searchText = ref('') // 搜索变量

const pendingTickets = computed(() => allTickets.value.filter(t => t.status === 'pending_dispatch'))
const myRepairingTickets = computed(() => allTickets.value.filter(t => t.status === 'repairing' && t.assignee === auth.currentUser?.id))

onMounted(() => { fetchData() })

async function fetchData() {
  try {
    // 搜索参数传给后端
    const res = await axios.get('http://127.0.0.1:8000/api/tickets/', {
       headers: { Authorization: `Token ${auth.token}` },
       params: { search: searchText.value } 
    })
    allTickets.value = res.data
  } catch (e) {
    console.error(e)
  }
}

async function takeOrder(ticketId) {
  if(!confirm("确定接单？")) return;
  try {
    await axios.post(`http://127.0.0.1:8000/api/tickets/${ticketId}/handle/`, {
      type: 'assign', worker_id: auth.currentUser.id 
    }, { headers: { Authorization: `Token ${auth.token}` } })
    alert("接单成功！")
    fetchData()
  } catch (e) { alert("接单失败") }
}

async function finishOrder(ticketId) {
  if(!confirm("确认完成？")) return;
  try {
    await axios.post(`http://127.0.0.1:8000/api/tickets/${ticketId}/handle/`, {
      type: 'finish'
    }, { headers: { Authorization: `Token ${auth.token}` } })
    alert("操作成功！")
    fetchData()
  } catch (e) { alert("操作失败") }
}

function formatDate(iso) {
  return new Date(iso).toLocaleString('zh-CN', {month:'2-digit', day:'2-digit', hour:'2-digit', minute:'2-digit'})
}
</script>

<style scoped>
.workspace-container { max-width: 1200px; margin: 0 auto; padding: 20px; }
.page-header { margin-bottom: 30px; }
.section { margin-bottom: 40px; }
.section-title { font-size: 18px; border-left: 5px solid #667eea; padding-left: 10px; margin-bottom: 20px; color: #333; }
.search-box { display: flex; gap: 10px; margin-bottom: 30px; max-width: 600px; }
.search-box input { flex: 1; padding: 10px 15px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; }
.btn-search { padding: 0 25px; background: #667eea; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; }
.task-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }
.empty-box { background: #f9f9f9; padding: 20px; text-align: center; color: #999; border-radius: 8px; }
.task-card { background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); border: 1px solid #eee; display: flex; flex-direction: column; }
.task-card.pending { border-top: 4px solid #f39c12; }
.task-card.repairing { border-top: 4px solid #3498db; }
.card-top { display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 12px; color: #888; }
.tag { background: #f39c12; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
.tag.blue { background: #3498db; }
h4 { margin: 0 0 10px 0; font-size: 16px; color: #333; }
.desc { color: #666; font-size: 14px; margin-bottom: 10px; flex: 1; }
.loc, .contact { font-size: 13px; color: #555; margin: 5px 0; }
.contact { color: #e74c3c; font-weight: bold; }
.btn-take { margin-top: 15px; width: 100%; padding: 10px; background: #667eea; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; transition: background 0.2s;}
.btn-finish { margin-top: 15px; width: 100%; padding: 10px; background: #2ecc71; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; }
</style>
