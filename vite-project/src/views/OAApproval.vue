<template>
  <div class="page-content">
    <h2>OA 审批中心</h2>
    <div v-if="list.length === 0">暂无待办任务</div>
    <div v-else class="oa-list">
      <div v-for="item in list" :key="item.id" class="oa-card">
        <div class="head">
          <strong>{{ item.requester_name }}</strong> ({{ item.requester_role }})
          申请: {{ item.target_area }}
        </div>
        <div class="body">理由: {{ item.reason }}</div>
        <div class="foot">
          <button @click="review(item.id, 'approve')" class="btn-ok">同意</button>
          <button @click="review(item.id, 'reject')" class="btn-no">拒绝</button>
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

onMounted(async () => {
  const res = await axios.get('http://127.0.0.1:8000/api/oa/', {
    headers: { Authorization: `Token ${auth.token}` }
  })
  list.value = res.data
})

async function review(id, action) {
  await axios.post(`http://127.0.0.1:8000/api/oa/${id}/review/`, { action }, {
    headers: { Authorization: `Token ${auth.token}` }
  })
  alert("操作成功")
  // 刷新列表
  list.value = list.value.filter(i => i.id !== id)
}
</script>

<style scoped>
.oa-card { background: white; padding: 15px; margin-bottom: 15px; border-left: 4px solid #667eea; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
.foot { margin-top: 10px; display: flex; gap: 10px; }
.btn-ok { background: #00b894; color: white; border:none; padding: 5px 15px; cursor: pointer; }
.btn-no { background: #d63031; color: white; border:none; padding: 5px 15px; cursor: pointer; }
</style>