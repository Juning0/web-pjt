<script setup lang="ts">
import { ref } from 'vue'

const isOpen = ref(false)
const messages = ref<{ type: 'bot' | 'user', content: string }[]>([
  { type: 'bot', content: '안녕하세요! 무엇을 도와드릴까요?' }
])
const inputText = ref('')

const toggleChat = () => {
  isOpen.value = !isOpen.value
  if (isOpen.value && messages.value.length === 1) {
    messages.value = [{ type: 'bot', content: '안녕하세요! 무엇을 도와드릴까요?' }]
  }
}

const handleOption = (option: string) => {
  messages.value.push({ type: 'user', content: option })
  setTimeout(() => {
    messages.value.push({ type: 'bot', content: option + '에 대해 도와드리겠습니다.' })
  }, 300)
}

const sendMessage = () => {
  if (!inputText.value.trim()) return
  messages.value.push({ type: 'user', content: inputText.value })
  const temp = inputText.value
  inputText.value = ''
  setTimeout(() => {
    messages.value.push({ type: 'bot', content: temp + '에 대해 답변해드렸습니다.' })
  }, 300)
}
</script>

<template>
  <div class="chatbot-container">
    <!-- 플로팅 버튼 -->
    <button v-if="!isOpen" class="float-button" @click="toggleChat">
      <span>💬</span>
    </button>

    <!-- 채팅 박스 -->
    <div v-if="isOpen" class="chat-box">
      <div class="chat-header">
        <h3>충청이 🤖</h3>
        <button class="close-btn" @click="toggleChat">✕</button>
      </div>

      <div class="chat-messages">
        <div v-for="(msg, idx) in messages" :key="idx" :class="['message', msg.type]">
          {{ msg.content }}
        </div>
      </div>

      <div class="chat-options">
        <button @click="handleOption('여행지/맛집 추천')">🍽️ 여행지/맛집 추천</button>
        <button @click="handleOption('제시굴 찾아주기')">🔍 제시굴 찾아주기</button>
        <button @click="handleOption('이용 안내 (FAQ)')">❓ 이용 안내 (FAQ)</button>
      </div>

      <div class="chat-input">
        <input
          v-model="inputText"
          type="text"
          placeholder="직접 입력..."
          @keyup.enter="sendMessage"
        />
        <button @click="sendMessage">전송</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chatbot-container {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 1000;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.float-button {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background-color: #333;
  color: white;
  border: none;
  font-size: 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  transition: 0.2s;
}

.float-button:hover {
  background-color: #555;
  transform: scale(1.1);
}

.chat-box {
  width: 360px;
  height: 600px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.chat-header {
  background-color: #f5f5f5;
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 2px solid #333;
}

.chat-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #333;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.message {
  padding: 10px 12px;
  border-radius: 8px;
  max-width: 80%;
  font-size: 14px;
  line-height: 1.4;
  word-wrap: break-word;
}

.message.bot {
  background-color: #e5e7eb;
  color: #333;
  align-self: flex-start;
}

.message.user {
  background-color: #333;
  color: white;
  align-self: flex-end;
}

.chat-options {
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  border-top: 1px solid #e5e7eb;
}

.chat-options button {
  padding: 12px;
  border: 2px solid #333;
  background: white;
  color: #333;
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: 0.2s;
}

.chat-options button:hover {
  background-color: #333;
  color: white;
}

.chat-input {
  padding: 12px 16px;
  display: flex;
  gap: 8px;
  border-top: 1px solid #e5e7eb;
}

.chat-input input {
  flex: 1;
  padding: 10px 12px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 13px;
  outline: none;
  transition: border-color 0.2s;
}

.chat-input input:focus {
  border-color: #333;
}

.chat-input button {
  padding: 10px 16px;
  background-color: #333;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
  transition: 0.2s;
}

.chat-input button:hover {
  background-color: #555;
}

@media (max-width: 640px) {
  .chat-box {
    width: calc(100vw - 32px);
    height: 70vh;
    max-height: 600px;
  }

  .message {
    max-width: 90%;
  }
}
</style>
