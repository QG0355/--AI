<template>
  <div class="page-content">
    <h2>提交报修单</h2>
    
    <div class="form-card">
      <div class="form-group">
        <label>报修区域 *</label>
        <select v-model="area" @change="checkPerm">
          <option value="">请选择</option>
          <option value="dorm">学生宿舍</option>
          <option value="office">教师办公室</option>
          <option value="teaching_building">教学楼</option>
          <option value="public">宿舍公共区域</option>
        </select>
        
        <div v-if="status === 'denied'" class="alert error">
          无权报修此区域 (您的身份: {{ roleName }})
          <button @click="showOA = true" class="btn-xs">申请权限</button>
        </div>
        <div v-if="status === 'allowed'" class="alert success">权限验证通过</div>
      </div>

      <form v-if="status === 'allowed'" @submit.prevent="submitTicket">
        <div class="form-group">
          <label>标题</label>
          <input v-model="ticket.title" required>
        </div>
        <div class="form-group">
          <label>类型</label>
          <select v-model="ticket.category">
            <option>硬件故障</option>
            <option>网络连接</option>
            <option>其他</option>
            
          </select>
        </div>
        <div class="form-group">
          <label>描述</label>
          <textarea v-model="ticket.description" rows="3"></textarea>
        </div>
        <button class="btn-primary">提交</button>
      </form>
    </div>

    <div v-if="showOA" class="modal">
      <div class="modal-box">
        <h3>申请报修权限: {{ areaName }}</h3>
        <textarea v-model="oaReason" placeholder="申请理由..." rows="3"></textarea>
        <div class="btns">
          <button @click="showOA=false">取消</button>
          <button @click="submitOA" class="btn-primary">提交申请</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const user = auth.currentUser
const router = useRouter()

const area = ref('')
const status = ref('')
const showOA = ref(false)
const oaReason = ref('')
const ticket = ref({ title: '', category: '硬件故障', description: '', priority: '中' })

const roleName = computed(() => {
  const map = { student:'学生', teacher:'老师', admin:'管理员' }
  return map[user.role] || user.role
})
const areaName = computed(() => area.value)

function checkPerm() {
  const role = user.role
  const extras = user.extra_permissions || []
  let allow = false

  if (role === 'admin') allow = true
  else if (role === 'student' && area.value === 'dorm') allow = true
  else if (role === 'teacher' && area.value === 'office') allow = true
  else if (role === 'dorm_manager' && ['dorm','public'].includes(area.value)) allow = true
  else if (extras.includes(area.value)) allow = true

  status.value = allow ? 'allowed' : 'denied'
}

async function submitOA() {
  await axios.post('http://127.0.0.1:8000/api/oa/', {
    target_area: area.value,
    reason: oaReason.value
  }, { headers: { Authorization: `Token ${auth.token}` } })
  alert("申请已提交，请等待审批！")
  showOA.value = false
}

async function submitTicket() {
  await axios.post('http://127.0.0.1:8000/api/tickets/', {
    ...ticket.value, 
    location: area.value
  }, { headers: { Authorization: `Token ${auth.token}` } })
  alert("报修成功！")
  router.push('/tickets')
}
</script>

<style scoped>
.page-content { padding: 20px; }
.form-card { background: white; padding: 20px; border-radius: 8px; }
.form-group { margin-bottom: 15px; }
.form-group input, select, textarea { width: 100%; padding: 8px; border: 1px solid #ccc; }
.alert { padding: 10px; margin-top: 5px; border-radius: 4px; font-size: 14px; }
.error { background: #ffecec; color: #d63031; }
.success { background: #e3fcef; color: #00b894; }
.btn-xs { margin-left: 10px; padding: 2px 8px; cursor: pointer; }
.modal { position: fixed; top:0; left:0; width:100%; height:100%; background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; }
.modal-box { background: white; padding: 20px; width: 300px; border-radius: 8px; }
.btns { margin-top: 15px; display: flex; justify-content: flex-end; gap: 10px; }
</style>