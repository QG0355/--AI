<template>
  <div class="page-content">
    <h2><i class="fas fa-briefcase"></i> 工作台 (待处理任务)</h2>

    <div v-if="tasks.length === 0" class="empty-state">暂无待处理任务</div>

    <div class="task-list">
      <div v-for="t in tasks" :key="t.id" class="task-card">
        <div class="header">
          <span class="badge">{{ t.status }}</span>
          <h3>{{ t.title }}</h3>
        </div>
        <div class="info">
          <p><strong>提交人：</strong> {{ t.submitter_name }}</p>
          <p><strong>位置：</strong> {{ t.location }}</p>
          <p><strong>描述：</strong> {{ t.description }}</p>
        </div>

        <div class="actions">
          
          <template v-if="role === 'dorm_manager' && t.status === 'pending_dorm'">
            <button @click="handleTicket(t.id, 'approve_dorm')" class="btn-ok">通过(转派单)</button>
            <button @click="handleTicket(t.id, 'reject')" class="btn-no">驳回</button>
          </template>

          <template v-if="['repair_admin','admin'].includes(role) && t.status === 'pending_dispatch'">
            <select v-model="selectedWorker[t.id]" class="worker-select">
              <option value="">选择维修人员</option>
              <option v-for="w in workers" :key="w.id" :value="w.id">{{ w.name }}</option>
            </select>
            <button @click="assignTicket(t.id)" class="btn-ok">派单</button>
            <button @click="handleTicket(t.id, 'reject')" class="btn-no">无效报修(驳回)</button>
          </template>

          <template v-if="role === 'maintenance' && t.status === 'repairing'">
            <button @click="handleTicket(t.id, 'finish')" class="btn-ok">维修完成</button>
          </template>
          
          <template v-if="role === 'student' && t.status === 'finished'">
             <input v-model="evalText[t.id]" placeholder="输入评价..." />
             <button @click="evaluateTicket(t.id)" class="btn-ok">提交评价</button>
           </template>

        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const role = computed(() => auth.currentUser?.role)
const tasks = ref([])
const workers = ref([]) // 维修人员列表
const selectedWorker = ref({})
const evalText = ref({})

onMounted(() => {
  fetchTasks()
  if (['repair_admin', 'admin'].includes(role.value)) {
    fetchWorkers()
  }
})

async function fetchTasks() {
  // 复用 tickets 接口，后端 get_queryset 已经过滤好了
  const res = await axios.get('http://127.0.0.1:8000/api/tickets/', {
    headers: { Authorization: `Token ${auth.token}` }
  })
  // 前端再过滤一遍，只显示“需要我处理”的状态
  tasks.value = res.data.filter(t => {
    if (role.value === 'dorm_manager') return t.status === 'pending_dorm'
    if (['repair_admin','admin'].includes(role.value)) return t.status === 'pending_dispatch'
    if (role.value === 'maintenance') return t.status === 'repairing'
    if (role.value === 'student') return t.status === 'finished' // 学生只处理待评价的
    return false
  })
}

async function fetchWorkers() {
  // 这里需要写一个获取所有维修人员的接口，或者偷懒用 user 列表过滤
  // 暂时假设你有一个 api/users/?role=maintenance 的接口
  // 如果没有，可以先写死几个假数据测试
  workers.value = [
      {id: 5, name: '王师傅 (维修)'}, // 这里的 ID 需要是你数据库里真实的维修工 ID
      {id: 6, name: '李师傅 (维修)'}
  ]
}

async function handleTicket(id, type) {
  await axios.post(`http://127.0.0.1:8000/api/tickets/${id}/handle/`, { type }, {
    headers: { Authorization: `Token ${auth.token}` }
  })
  alert('操作成功')
  fetchTasks()
}

async function assignTicket(id) {
  const workerId = selectedWorker.value[id]
  if (!workerId) return alert('请选择维修人员')
  
  await axios.post(`http://127.0.0.1:8000/api/tickets/${id}/handle/`, { 
    type: 'assign', 
    worker_id: workerId 
  }, {
    headers: { Authorization: `Token ${auth.token}` }
  })
  alert('派单成功')
  fetchTasks()
}

async function evaluateTicket(id) {
    await axios.post(`http://127.0.0.1:8000/api/tickets/${id}/handle/`, { 
    type: 'evaluate', 
    comment: evalText.value[id],
    rating: 5
  }, {
    headers: { Authorization: `Token ${auth.token}` }
  })
  alert('评价成功，工单关闭')
  fetchTasks()
}
</script>

<style scoped>
/* 复用之前的卡片样式 */
.task-card { background: white; padding: 15px; margin-bottom: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
.header { display: flex; justify-content: space-between; border-bottom: 1px solid #eee; padding-bottom: 10px; margin-bottom: 10px; }
.badge { background: #ffeaa7; padding: 2px 8px; font-size: 12px; border-radius: 4px; }
.actions { margin-top: 15px; display: flex; gap: 10px; align-items: center;}
.btn-ok { background: #00b894; color: white; border:none; padding: 5px 15px; border-radius: 4px; cursor: pointer; }
.btn-no { background: #d63031; color: white; border:none; padding: 5px 15px; border-radius: 4px; cursor: pointer; }
.worker-select { padding: 5px; border: 1px solid #ccc; border-radius: 4px; }
</style>