<template>
  <div class="ai-page">
    <div class="ai-card">
      <div class="ai-header">
        <h2>智能报修助手</h2>
        <p>通过自然语言提问，快速了解报修流程和常见问题处理建议</p>
      </div>

      <div class="warning-banner">
        <i class="fas fa-exclamation-triangle"></i>
        <div class="warning-text">
          <p>AI 仅供参考，请以实际为主，不能盲目相信。</p>
          <p>涉及设备安全、维修操作等问题，请以学校正式通知和专业维修人员意见为准。</p>
        </div>
      </div>

      <div class="chat-box">
        <div class="messages" ref="messageList">
          <div
            v-for="(m, index) in messages"
            :key="index"
            class="message-row"
            :class="m.role"
          >
            <div class="avatar" v-if="m.role === 'assistant'">
              <i class="fas fa-robot"></i>
            </div>
            <div class="avatar user" v-else>
              <i class="fas fa-user"></i>
            </div>
            <div class="bubble">
              <p>{{ m.content }}</p>
            </div>
          </div>

          <div v-if="loading" class="message-row assistant">
            <div class="avatar">
              <i class="fas fa-robot"></i>
            </div>
            <div class="bubble typing">
              <span></span><span></span><span></span>
            </div>
          </div>
        </div>

        <div v-if="error" class="error-text">
          <i class="fas fa-info-circle"></i> {{ error }}
        </div>

        <form class="input-area" @submit.prevent="handleSend">
          <textarea
            v-model="input"
            rows="3"
            placeholder="请输入你想咨询的内容，例如：空调不制冷应该怎么报修？"
          ></textarea>
          <div class="input-actions">
            <span class="hint">本功能面向已登录学生使用，问题越具体，AI 解答越有参考价值。</span>
            <button type="submit" :disabled="loading || !input.trim()">
              {{ loading ? '正在思考...' : '发送' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

const messages = ref([
  {
    role: 'assistant',
    content:
      '你好，我是校园报修智能助手，可以帮助你了解报修流程和常见处理建议。请注意：AI 仅供参考，请以学校实际流程和老师、维修人员的意见为准，不能盲目相信。'
  }
])

const input = ref('')
const loading = ref(false)
const error = ref('')
const messageList = ref(null)

function scrollToBottom() {
  nextTick(() => {
    if (messageList.value) {
      messageList.value.scrollTop = messageList.value.scrollHeight
    }
  })
}

async function handleSend() {
  const content = input.value.trim()
  if (!content) return

  if (!auth.isLoggedIn) {
    error.value = '使用智能对话前请先登录系统。'
    return
  }

  error.value = ''
  messages.value.push({ role: 'user', content })
  input.value = ''
  scrollToBottom()

  loading.value = true
  try {
    const res = await axios.post(
      'http://127.0.0.1:8000/api/ai-chat/',
      { message: content },
      {
        headers: {
          Authorization: `Token ${auth.token}`
        }
      }
    )
    const reply = res.data.reply || '当前暂时无法获取回答，请稍后再试。'
    messages.value.push({ role: 'assistant', content: reply })
    scrollToBottom()
  } catch (e) {
    error.value =
      e.response?.data?.detail ||
      '对话暂时不可用，请检查后端服务或稍后再试。'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.ai-page {
  padding: 24px;
  display: flex;
  justify-content: center;
}

.ai-card {
  width: 100%;
  max-width: 960px;
  background: #ffffff;
  border-radius: 20px;
  padding: 24px 26px 20px;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.08);
}

.ai-header h2 {
  margin: 0;
  font-size: 22px;
  color: #b0325b;
}

.ai-header p {
  margin: 6px 0 14px;
  font-size: 13px;
  color: #8c435f;
}

.warning-banner {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  background: #fff3f5;
  border-radius: 10px;
  padding: 10px 12px;
  border: 1px solid #ffc9d4;
  color: #b0325b;
  font-size: 13px;
}

.warning-banner i {
  margin-top: 2px;
}

.warning-text p {
  margin: 0;
  line-height: 1.6;
}

.warning-text p + p {
  margin-top: 2px;
}

.chat-box {
  margin-top: 16px;
  border-radius: 14px;
  border: 1px solid #f1e2ea;
  background: #fff9fb;
  display: flex;
  flex-direction: column;
  height: 520px;
}

.messages {
  flex: 1;
  padding: 12px 16px;
  overflow-y: auto;
}

.message-row {
  display: flex;
  align-items: flex-start;
  margin-bottom: 10px;
}

.message-row.assistant {
  flex-direction: row;
}

.message-row.user {
  flex-direction: row-reverse;
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 8px;
  background: linear-gradient(135deg, #ff9a9e, #fecfef);
  color: #ffffff;
}

.avatar.user {
  background: linear-gradient(135deg, #667eea, #764ba2);
}

.bubble {
  max-width: 70%;
  padding: 8px 12px;
  border-radius: 14px;
  font-size: 14px;
  line-height: 1.6;
}

.assistant .bubble {
  background: #ffffff;
  border: 1px solid #f1d1dd;
  color: #60394c;
}

.user .bubble {
  background: #667eea;
  color: #ffffff;
}

.bubble.typing {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.bubble.typing span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #b0325b;
  animation: blink 1.2s infinite ease-in-out;
}

.bubble.typing span:nth-child(2) {
  animation-delay: 0.15s;
}

.bubble.typing span:nth-child(3) {
  animation-delay: 0.3s;
}

@keyframes blink {
  0%,
  80%,
  100% {
    opacity: 0.2;
  }
  40% {
    opacity: 1;
  }
}

.error-text {
  padding: 0 16px 4px;
  font-size: 13px;
  color: #d14343;
  display: flex;
  align-items: center;
  gap: 6px;
}

.input-area {
  border-top: 1px solid #f1d1dd;
  padding: 10px 14px;
  background: #ffffff;
  border-radius: 0 0 14px 14px;
}

.input-area textarea {
  width: 100%;
  resize: none;
  border: 1px solid #e4c5d5;
  border-radius: 10px;
  padding: 8px 10px;
  font-size: 14px;
  box-sizing: border-box;
  outline: none;
}

.input-area textarea:focus {
  border-color: #b0325b;
  box-shadow: 0 0 0 2px rgba(176, 50, 91, 0.1);
}

.input-actions {
  margin-top: 6px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.hint {
  font-size: 12px;
  color: #a45c7b;
}

.input-actions button {
  padding: 6px 20px;
  border-radius: 18px;
  border: none;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #ffffff;
  font-size: 14px;
  cursor: pointer;
}

.input-actions button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .ai-page {
    padding: 12px;
  }

  .ai-card {
    padding: 16px 14px 12px;
  }

  .chat-box {
    height: 460px;
  }
}
</style>

