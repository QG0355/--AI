<template>
  <div class="page-content">
    <h2><i class="fas fa-wrench"></i> 提交报修单</h2>
    
    <div class="form-card">
      <form @submit.prevent="submitTicket">
        <div class="form-row">
          <div class="form-group half">
            <label>标题</label>
            <input v-model="form.title" placeholder="例如：302宿舍空调漏水" required>
          </div>
          <div class="form-group half">
            <label>故障位置</label>
            <input v-model="form.location" placeholder="例如：宿舍楼6栋302宿舍" required>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group half">
            <label>故障类型</label>
            <select v-model="form.category" required>
              <option value="">请选择类型</option>
              <option value="设备故障">设备故障</option>
              <option value="水电问题">水电问题</option>
              <option value="网络连接">网络连接</option>
              <option value="柜子损坏">柜子损坏</option>
              <option value="门窗损坏">门窗损坏</option>
              <option value="其他">其他</option>
            </select>
          </div>
          
          <div class="form-group half">
            <label>优先级</label>
            <select v-model="form.priority" required>
              <option value="低">低 - 不影响使用</option>
              <option value="中">中 - 影响部分功能</option>
              <option value="高">高 - 无法工作</option>
              <option value="紧急">紧急 - 安全隐患</option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label>联系电话</label>
          <input v-model="form.contact" placeholder="请填写手机号，方便联系" required>
        </div>

        <div class="form-group">
          <label>故障详细描述</label>
          <textarea v-model="form.description" rows="4" placeholder="请详细描述故障现象..." required></textarea>
        </div>

        <button class="btn-primary" :disabled="loading">
          {{ loading ? '提交中...' : '提交报修单' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()
const loading = ref(false)

const form = ref({
  title: '',
  location: '', 
  category: '',
  priority: '中',
  description: '',
  contact: ''
})

async function submitTicket() {
  loading.value = true
  try {
    await axios.post('http://127.0.0.1:8000/api/tickets/', {
      title: form.value.title,
      category: form.value.category,
      priority: form.value.priority,
      description: form.value.description,
      location: form.value.location,
      contact: form.value.contact
    }, { 
      headers: { Authorization: `Token ${auth.token}` } 
    })
    
    alert("报修成功！")
    router.push('/tickets')
  } catch (e) {
    console.error(e.response?.data)
    alert("提交失败：" + JSON.stringify(e.response?.data))
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.page-content { padding: 20px; max-width: 800px; margin: 0 auto; }
.form-card { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
.form-group { margin-bottom: 20px; }
.form-row { display: flex; gap: 20px; }
.half { flex: 1; }
.form-group label { display: block; margin-bottom: 8px; font-weight: bold; color: #333; }
.form-group input, select, textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-size: 14px; box-sizing: border-box; }
.btn-primary { width: 100%; padding: 12px; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; margin-top: 10px;}
.btn-primary:disabled { background: #ccc; }
</style>