<template>
  <div class="page-content">
    <h2>报修审核中心</h2>
    <p class="subtitle">审核员 / 管理员可以在此对学生提交的报修进行审核与驳回</p>

    <div v-if="list.length === 0" class="empty">
      当前没有需要审核的报修工单。
    </div>

    <div v-else class="oa-list">
      <div v-for="item in list" :key="item.id" class="oa-card">
        <div class="head">
          <div class="title">{{ item.title }}</div>
          <div class="meta">
            <span>报修人：{{ item.submitter_name || '学生' }}</span>
            <span v-if="item.location">地点：{{ item.location }}</span>
          </div>
        </div>
        <div class="body">
          <p>类别：{{ item.category }}（优先级：{{ item.priority }}）</p>
          <p>描述：{{ item.description || '未填写详细描述' }}</p>
        </div>
        <div class="foot">
          <button @click="review(item.id, 'approve')" class="btn-ok">通过并进入派单</button>
          <button @click="review(item.id, 'reject')" class="btn-no">驳回该报修</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const list = ref([])

async function fetchList() {
  const res = await axios.get('http://127.0.0.1:8000/api/tickets/', {
    headers: { Authorization: `Token ${auth.token}` },
    params: { status: 'pending_dorm' }
  })
  list.value = res.data
}

onMounted(fetchList)

async function review(id, decision) {
  await axios.post(
    `http://127.0.0.1:8000/api/tickets/${id}/review/`,
    { decision },
    { headers: { Authorization: `Token ${auth.token}` } }
  )
  alert('操作成功')
  list.value = list.value.filter(i => i.id !== id)
}
</script>

<style scoped>
.page-content {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
}

h2 {
  margin-bottom: 4px;
}

.subtitle {
  margin: 0 0 16px;
  font-size: 13px;
  color: #777;
}

.empty {
  padding: 40px 0;
  text-align: center;
  color: #aaa;
  font-size: 14px;
}

.oa-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.oa-card {
  background: white;
  padding: 16px 18px;
  border-left: 4px solid #667eea;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border-radius: 10px;
}

.head {
  margin-bottom: 8px;
}

.title {
  font-weight: 600;
  margin-bottom: 4px;
}

.meta {
  font-size: 12px;
  color: #666;
  display: flex;
  gap: 12px;
}

.body {
  font-size: 13px;
  color: #555;
  line-height: 1.7;
}

.body p {
  margin: 2px 0;
}

.foot {
  margin-top: 10px;
  display: flex;
  gap: 10px;
}

.btn-ok {
  background: #00b894;
  color: white;
  border: none;
  padding: 5px 15px;
  cursor: pointer;
  border-radius: 5px;
  font-size: 13px;
}

.btn-no {
  background: #d63031;
  color: white;
  border: none;
  padding: 5px 15px;
  cursor: pointer;
  border-radius: 5px;
  font-size: 13px;
}
</style>
