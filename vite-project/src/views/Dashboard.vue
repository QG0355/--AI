<template>
  <div class="home-page">
    <section class="hero-section">
      <div class="hero-overlay">
        <div class="hero-main">
          <div class="hero-text">
            <h1>校园设备报修系统</h1>
            <p class="hero-en">Campus Facilities Repair Service</p>
            <p class="hero-desc">
              一站式在线报修平台，连接学生、审核员和维修师傅，让报修流程更加高效、透明、可追踪。
            </p>

            <div class="hero-actions">
              <template v-if="!authStore.isLoggedIn">
                <button class="btn-primary" @click="goLogin">
                  立即登录开始报修
                </button>
                <button class="btn-ghost" @click="goRegister">
                  注册新账号
                </button>
              </template>
              <template v-else>
                <button class="btn-primary" @click="handleMainBtnClick">
                  <i :class="isStudent ? 'fas fa-wrench' : 'fas fa-briefcase'"></i>
                  {{ isStudent ? '我要报修' : '进入工作台' }}
                </button>
                <button class="btn-ghost" @click="goTickets">
                  <i class="fas fa-list"></i>
                  我的报修记录
                </button>
              </template>
            </div>

            <div class="hero-tips">
              <span class="tip-badge">提醒</span>
              <span>请使用真实联系方式和报修地点，便于维修师傅快速联系和上门服务。</span>
            </div>
          </div>

          <div class="hero-side">
            <div class="stat-card">
              <div class="stat-label">今日报修</div>
              <div class="stat-value">—</div>
            </div>
            <div class="stat-card">
              <div class="stat-label">正在处理</div>
              <div class="stat-value">—</div>
            </div>
            <div class="stat-card">
              <div class="stat-label">平均处理时间</div>
              <div class="stat-value">—</div>
            </div>
            <p class="stat-note">以上数据为示意展示，可在后续按任务书要求接真实统计。</p>
          </div>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="section-header">
        <h2>常用入口</h2>
        <p>根据不同角色，快速进入对应功能页面</p>
      </div>
      <div class="entry-grid">
        <div class="entry-card" @click="goSubmit">
          <div class="entry-icon primary">
            <i class="fas fa-clipboard-list"></i>
          </div>
          <h3>提交报修</h3>
          <p>填写报修信息、上传故障描述，系统自动流转到相关老师和维修师傅。</p>
        </div>

        <div class="entry-card" @click="goTickets">
          <div class="entry-icon">
            <i class="fas fa-history"></i>
          </div>
          <h3>我的报修</h3>
          <p>随时查看每一条报修的受理进度、派单情况和最终处理结果。</p>
        </div>

        <div class="entry-card" @click="goAi">
          <div class="entry-icon warning">
            <i class="fas fa-robot"></i>
          </div>
          <h3>AI 报修助手</h3>
          <p>用自然语言咨询报修流程和注意事项，结果仅供参考，请以实际为准。</p>
        </div>
      </div>
    </section>

    <section class="section gray">
      <div class="section-header">
        <h2>报修流程示意</h2>
        <p>整体流程清晰可追踪，方便答辩时说明系统设计思路</p>
      </div>
      <div class="flow-steps">
        <div class="flow-item">
          <div class="step-index">1</div>
          <h3>线上提交</h3>
          <p>学生登录系统，选择报修类别，填写详细故障描述和联系方式。</p>
        </div>
        <div class="flow-item">
          <div class="step-index">2</div>
          <h3>审核与派单</h3>
          <p>审核员或管理员在线审核，并将工单分配给对应维修师傅。</p>
        </div>
        <div class="flow-item">
          <div class="step-index">3</div>
          <h3>上门维修与评价</h3>
          <p>维修完成后，学生在系统中进行评价，为“优秀维修之星”提供数据支撑。</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { computed } from 'vue'

const authStore = useAuthStore()
const router = useRouter()

const isStudent = computed(() => {
  return authStore.currentUser?.role === 'student'
})

function handleMainBtnClick() {
  if (isStudent.value) {
    if (!authStore.currentUser?.is_identity_bound) {
      if (confirm('您尚未绑定身份信息，绑定后即可报修。\n是否现在去绑定？')) {
        router.push('/bind')
      }
    } else {
      router.push('/submit')
    }
  } else {
    router.push('/workplace')
  }
}

function goLogin() {
  router.push('/login')
}

function goRegister() {
  router.push('/register')
}

function goTickets() {
  if (!authStore.isLoggedIn) {
    router.push('/login')
    return
  }
  router.push('/tickets')
}

function goSubmit() {
  if (!authStore.isLoggedIn) {
    router.push('/login')
    return
  }
  handleMainBtnClick()
}

function goAi() {
  if (!authStore.isLoggedIn) {
    router.push('/login')
    return
  }
  router.push('/ai-chat')
}
</script>

<style scoped>
.home-page {
  background: #f6f3f7;
}

.hero-section {
  background-image:
    linear-gradient(120deg, rgba(176, 50, 91, 0.82), rgba(255, 188, 188, 0.75)),
    url('https://images.pexels.com/photos/373488/pexels-photo-373488.jpeg?auto=compress&cs=tinysrgb&w=1600');
  background-size: cover;
  background-position: center;
  color: #fff;
}

.hero-overlay {
  backdrop-filter: blur(2px);
  padding: 48px 32px 40px;
}

.hero-main {
  max-width: 1100px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 40px;
  align-items: center;
}

.hero-text h1 {
  font-size: 32px;
  letter-spacing: 1px;
  margin: 0 0 8px;
}

.hero-en {
  font-size: 13px;
  opacity: 0.9;
  margin-bottom: 18px;
  text-transform: uppercase;
}

.hero-desc {
  font-size: 15px;
  line-height: 1.8;
  max-width: 520px;
  margin-bottom: 24px;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 18px;
}

.btn-primary {
  padding: 10px 26px;
  border-radius: 999px;
  border: none;
  background: #ffe5f0;
  color: #b0325b;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-ghost {
  padding: 10px 22px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.7);
  background: transparent;
  color: #fff;
  font-size: 14px;
  cursor: pointer;
}

.hero-tips {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  background: rgba(255, 255, 255, 0.12);
  padding: 8px 10px;
  border-radius: 999px;
  max-width: 520px;
}

.tip-badge {
  background: rgba(255, 255, 255, 0.26);
  padding: 2px 10px;
  border-radius: 999px;
  font-size: 11px;
}

.hero-side {
  background: rgba(255, 255, 255, 0.14);
  border-radius: 16px;
  padding: 18px 18px 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 12px;
  padding: 10px 12px;
  color: #80304e;
}

.stat-label {
  font-size: 12px;
  opacity: 0.8;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
}

.stat-note {
  margin: 4px 2px 0;
  font-size: 11px;
  color: #fdf3f6;
}

.section {
  max-width: 1100px;
  margin: 0 auto;
  padding: 28px 20px 32px;
}

.section.gray {
  margin-top: 4px;
}

.section-header h2 {
  margin: 0;
  font-size: 20px;
  color: #333;
}

.section-header p {
  margin: 6px 0 18px;
  font-size: 13px;
  color: #888;
}

.entry-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 18px;
}

.entry-card {
  background: #fff;
  border-radius: 16px;
  padding: 16px 18px;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.04);
  cursor: pointer;
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.entry-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 26px rgba(0, 0, 0, 0.06);
}

.entry-icon {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f2ecff;
  color: #5b4bd4;
  margin-bottom: 10px;
}

.entry-icon.primary {
  background: #ffe5f0;
  color: #b0325b;
}

.entry-icon.warning {
  background: #fff4e5;
  color: #d97706;
}

.entry-card h3 {
  margin: 0 0 6px;
  font-size: 16px;
  color: #333;
}

.entry-card p {
  margin: 0;
  font-size: 13px;
  color: #666;
  line-height: 1.7;
}

.flow-steps {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 18px;
}

.flow-item {
  background: #fff;
  border-radius: 16px;
  padding: 16px 18px;
  box-shadow: 0 5px 16px rgba(0, 0, 0, 0.04);
}

.step-index {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: #ffe5f0;
  color: #b0325b;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 14px;
  margin-bottom: 8px;
}

.flow-item h3 {
  margin: 0 0 6px;
  font-size: 15px;
  color: #333;
}

.flow-item p {
  margin: 0;
  font-size: 13px;
  color: #666;
  line-height: 1.7;
}

@media (max-width: 768px) {
  .hero-overlay {
    padding: 32px 18px 24px;
  }

  .hero-main {
    grid-template-columns: 1fr;
    gap: 22px;
  }

  .hero-text h1 {
    font-size: 24px;
  }

  .hero-desc {
    font-size: 14px;
  }
}
</style>
