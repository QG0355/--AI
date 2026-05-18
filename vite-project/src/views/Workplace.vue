<template>
  <div class="workspace-container">
    <div class="page-header">
      <h2 v-if="isDispatcher">📌 派单工作台</h2>
      <h2 v-else>🛠️ 维修师傅工作台</h2>
      <p>欢迎回来，{{ auth.currentUser?.name || auth.currentUser?.username }}</p>
    </div>

    <div class="search-box">
      <input 
        v-model="searchText" 
        type="text" 
        placeholder="🔍 搜索工单号、位置、描述..." 
        @keyup.enter="fetchData"
      />
      <button @click="fetchData" class="btn-search">搜索</button>
    </div>

    <div class="section" v-if="isDispatcher">
      <h3 class="section-title">📢 待派单工单</h3>
      <div v-if="pendingTickets.length === 0" class="empty-box">暂无待派单工单</div>
      <div v-else class="task-grid">
        <div v-for="t in pendingTickets" :key="t.id" class="task-card pending">
          <div class="card-top">
            <span class="tag">待派单</span>
            <span class="time">{{ formatDate(t.submitTime) }}</span>
          </div>
          <h4>{{ t.title }}</h4>
          <p class="desc">{{ t.description }}</p>
          <p class="loc"><i class="fas fa-map-marker-alt"></i> {{ t.location }}</p>

          <div class="dispatch-row">
            <select v-model="dispatchTo[t.id]" class="dispatch-select">
              <option value="">请选择维修人员</option>
              <option v-for="w in maintenanceUsers" :key="w.id" :value="w.id">
                {{ w.name }}{{ w.identity_id ? `（${w.identity_id}）` : '' }}
              </option>
            </select>
            <button @click="dispatchTicket(t.id)" class="btn-dispatch">派单</button>
          </div>
        </div>
      </div>
    </div>

    <div class="section" v-if="!isDispatcher">
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

    <div class="section" v-if="!isDispatcher">
      <h3 class="section-title">🕒 待评价工单（已完成）</h3>
      <div v-if="myFinishedTickets.length === 0" class="empty-box">暂无待评价工单</div>
      <div class="task-grid">
        <div v-for="t in myFinishedTickets" :key="t.id" class="task-card finished">
          <div class="card-top">
            <span class="tag green">待评价</span>
            <span class="assignee">负责人: 我</span>
          </div>
          <h4>{{ t.title }}</h4>
          <p class="loc"><i class="fas fa-map-marker-alt"></i> {{ t.location }}</p>
          <p class="contact"><i class="fas fa-phone"></i> {{ t.contact }}</p>
          <div class="hint">等待学生评价后自动结单</div>
        </div>
      </div>
    </div>

    <div class="section" v-if="!isDispatcher">
      <h3 class="section-title">⭐ 已结单工单（含评价）</h3>
      <div v-if="myClosedTickets.length === 0" class="empty-box">暂无已结单工单</div>
      <div class="task-grid">
        <div v-for="t in myClosedTickets" :key="t.id" class="task-card closed">
          <div class="card-top">
            <span class="tag gray">已结单</span>
            <span class="assignee">负责人: 我</span>
          </div>
          <h4>{{ t.title }}</h4>
          <p class="loc"><i class="fas fa-map-marker-alt"></i> {{ t.location }}</p>
          <p class="score" v-if="t.rating !== undefined && t.rating !== null">评分：{{ t.rating }}/5</p>
          <p class="eval" v-if="t.evaluation">{{ t.evaluation }}</p>
          <p class="eval empty" v-else>无评价内容</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import { apiUrl } from '@/config'

const auth = useAuthStore()
const allTickets = ref([])
const searchText = ref('') // 搜索变量
const maintenanceUsers = ref([])
const dispatchTo = ref({})

const isDispatcher = computed(() => ['admin', 'auditor'].includes(auth.currentUser?.role))

const pendingTickets = computed(() => allTickets.value.filter(t => t.status === 'pending_dispatch'))
const myRepairingTickets = computed(() => allTickets.value.filter(t => t.status === 'repairing' && t.assignee === auth.currentUser?.id))
const myFinishedTickets = computed(() => allTickets.value.filter(t => t.status === 'finished' && t.assignee === auth.currentUser?.id))
const myClosedTickets = computed(() => allTickets.value.filter(t => t.status === 'closed' && t.assignee === auth.currentUser?.id))

onMounted(async () => {
  await fetchData()
})

watch(
  () => isDispatcher.value,
  async (val) => {
    if (val) {
      await fetchMaintenanceUsers()
    }
  },
  { immediate: true }
)

async function fetchData() {
  try {
    // 搜索参数传给后端
    const res = await axios.get(apiUrl('tickets/'), {
       headers: { Authorization: `Token ${auth.token}` },
       params: { search: searchText.value } 
    })
    allTickets.value = res.data
  } catch (e) {
    console.error(e)
  }
}

async function fetchMaintenanceUsers() {
  try {
    const res = await axios.get(apiUrl('maintenance-users/'), {
      headers: { Authorization: `Token ${auth.token}` }
    })
    maintenanceUsers.value = Array.isArray(res.data) ? res.data : []
  } catch (e) {
    maintenanceUsers.value = []
  }
}

async function dispatchTicket(ticketId) {
  const workerId = dispatchTo.value?.[ticketId]
  if (!workerId) {
    alert('请选择维修人员')
    return
  }
  try {
    await axios.post(apiUrl(`tickets/${ticketId}/handle/`), {
      type: 'assign',
      worker_id: workerId
    }, { headers: { Authorization: `Token ${auth.token}` } })
    await fetchData()
  } catch (e) {
    alert('派单失败')
  }
}

async function finishOrder(ticketId) {
  // if(!confirm("确认完成？")) return;
  try {
    await axios.post(apiUrl(`tickets/${ticketId}/handle/`), {
      type: 'finish'
    }, { headers: { Authorization: `Token ${auth.token}` } })
    // alert("操作成功！")
    fetchData()
  } catch (e) { /* alert("操作失败") */ }
}

function formatDate(iso) {
  return new Date(iso).toLocaleString('zh-CN', {month:'2-digit', day:'2-digit', hour:'2-digit', minute:'2-digit'})
}
</script>

<style scoped>
.workspace-container { max-width: var(--app-page-max-width); margin: 0 auto; padding: 20px; }
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
.task-card.finished { border-top: 4px solid #2ecc71; }
.task-card.closed { border-top: 4px solid #9ca3af; }
.card-top { display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 12px; color: #888; }
.tag { background: #f39c12; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
.tag.blue { background: #3498db; }
.tag.green { background: #2ecc71; }
.tag.gray { background: #9ca3af; }
h4 { margin: 0 0 10px 0; font-size: 16px; color: #333; }
.desc { color: #666; font-size: 14px; margin-bottom: 10px; flex: 1; }
.loc, .contact { font-size: 13px; color: #555; margin: 5px 0; }
.contact { color: #e74c3c; font-weight: bold; }
.hint { margin-top: 10px; font-size: 12px; color: #6b7280; }
.score { margin: 8px 0 6px; font-size: 13px; color: #374151; font-weight: 700; }
.eval { margin: 0; font-size: 13px; color: #4b5563; line-height: 1.5; }
.eval.empty { color: #9ca3af; }
.btn-take { margin-top: 15px; width: 100%; padding: 10px; background: #667eea; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; transition: background 0.2s;}
.btn-finish { margin-top: 15px; width: 100%; padding: 10px; background: #2ecc71; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; }
.dispatch-row { display: flex; gap: 10px; margin-top: 12px; }
.dispatch-select { flex: 1; padding: 10px 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; background: white; }
.btn-dispatch { width: 92px; padding: 10px; background: #667eea; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; }
</style>
