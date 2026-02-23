<template>
  <div class="star-section">
    <div class="star-header">
      <h2>优秀维修之星</h2>
      <p>展示在报修服务中责任心强、响应及时、服务态度优秀的维修师傅</p>
    </div>

    <div class="star-carousel" v-if="stars.length">
      <div class="star-track">
        <div
          v-for="(s, index) in stars"
          :key="s.id || index"
          class="star-card"
          :class="{ active: index === activeIndex }"
        >
          <div class="avatar-wrapper">
            <img :src="s.avatar_url || s.fallbackAvatar" alt="维修师傅头像" />
          </div>
          <h3 class="star-name">{{ s.name }}</h3>
          <p class="star-meta">
            <span v-if="s.grade">{{ s.grade }}</span>
            <span v-if="s.major">{{ s.major }}</span>
          </p>
          <p class="star-honor" v-if="s.honor">{{ s.honor }}</p>
          <p class="star-desc">{{ s.description }}</p>
        </div>
      </div>

      <div class="star-dots">
        <button
          v-for="(s, index) in stars"
          :key="index"
          class="dot"
          :class="{ active: index === activeIndex }"
          @click="setActive(index)"
        ></button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import axios from 'axios'

const stars = ref([])
const activeIndex = ref(0)
let timer = null

const fallbackStars = [
  {
    name: '陈师傅',
    grade: '后勤维修组',
    major: '水电维护',
    honor: '本月抢单王',
    description: '响应报修及时，处理水电设施故障经验丰富，多次在教学高峰期保障教学秩序。',
    fallbackAvatar: 'https://images.pexels.com/photos/614810/pexels-photo-614810.jpeg?auto=compress&cs=tinysrgb&w=600'
  },
  {
    name: '黄师傅',
    grade: '综合维修组',
    major: '宿舍设施维护',
    honor: '服务之星',
    description: '对学生态度耐心细致，帮助解决宿舍门窗、家具等多类问题，获多次学生表扬。',
    fallbackAvatar: 'https://images.pexels.com/photos/733872/pexels-photo-733872.jpeg?auto=compress&cs=tinysrgb&w=600'
  },
  {
    name: '梁师傅',
    grade: '网络运维组',
    major: '网络与多媒体设备',
    honor: '技术能手',
    description: '熟悉校园网络与多媒体设备，快速排查教室网络和投影问题，保障课堂正常进行。',
    fallbackAvatar: 'https://images.pexels.com/photos/927022/pexels-photo-927022.jpeg?auto=compress&cs=tinysrgb&w=600'
  }
]

function startAutoPlay() {
  stopAutoPlay()
  if (!stars.value.length) return
  timer = setInterval(() => {
    activeIndex.value = (activeIndex.value + 1) % stars.value.length
  }, 6000)
}

function stopAutoPlay() {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
}

function setActive(index) {
  activeIndex.value = index
  startAutoPlay()
}

onMounted(async () => {
  try {
    const res = await axios.get('http://127.0.0.1:8000/api/student-stars/')
    if (Array.isArray(res.data) && res.data.length) {
      stars.value = res.data.map((s, idx) => ({
        ...s,
        fallbackAvatar: fallbackStars[idx % fallbackStars.length].fallbackAvatar
      }))
    } else {
      stars.value = fallbackStars
    }
  } catch (e) {
    stars.value = fallbackStars
  }
  startAutoPlay()
})

onBeforeUnmount(() => {
  stopAutoPlay()
})
</script>

<style scoped>
.star-section {
  margin-top: 40px;
  padding: 24px 28px 32px;
  border-radius: 20px;
  background: linear-gradient(135deg, #ffe4ec 0%, #fdf2ff 40%, #ffffff 100%);
  box-shadow: 0 12px 30px rgba(255, 192, 203, 0.35);
}

.star-header h2 {
  margin: 0;
  font-size: 22px;
  color: #b0325b;
}

.star-header p {
  margin: 6px 0 20px;
  font-size: 13px;
  color: #a45c7b;
}

.star-carousel {
  position: relative;
}

.star-track {
  display: flex;
  overflow: hidden;
}

.star-card {
  flex: 0 0 100%;
  opacity: 0;
  transform: translateX(20px);
  transition: all 0.6s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.star-card.active {
  opacity: 1;
  transform: translateX(0);
}

.avatar-wrapper {
  width: 96px;
  height: 96px;
  border-radius: 50%;
  padding: 4px;
  background: linear-gradient(135deg, #ff9a9e, #fecfef);
  margin-bottom: 12px;
}

.avatar-wrapper img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
}

.star-name {
  margin: 6px 0 2px;
  font-size: 18px;
  color: #b0325b;
}

.star-meta {
  margin: 0 0 4px;
  font-size: 13px;
  color: #a45c7b;
}

.star-meta span + span {
  margin-left: 8px;
}

.star-honor {
  margin: 4px 0 10px;
  font-size: 14px;
  color: #d2436b;
  font-weight: 600;
}

.star-desc {
  margin: 0;
  font-size: 14px;
  line-height: 1.7;
  color: #6b4356;
}

.star-dots {
  margin-top: 18px;
  text-align: center;
}

.dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  border: none;
  margin: 0 4px;
  background: rgba(176, 50, 91, 0.25);
  cursor: pointer;
  padding: 0;
}

.dot.active {
  background: #b0325b;
}

@media (max-width: 600px) {
  .star-section {
    padding: 18px 16px 22px;
  }
}
</style>

