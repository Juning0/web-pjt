<script setup>
import { provide, ref } from 'vue'
import ChatWidget from '@/components/ChatWidget.vue'

const toast = ref('')
let toastTimer

function showIntegrationEvent(source) {
  toast.value = `“${source.title}” 선택 이벤트가 전달되었습니다.`
  window.clearTimeout(toastTimer)
  toastTimer = window.setTimeout(() => {
    toast.value = ''
  }, 2800)
}

provide('showIntegrationEvent', showIntegrationEvent)
</script>

<template>
  <div class="site-shell">
    <header class="site-header">
      <RouterLink class="site-logo" to="/" aria-label="LocalHub 홈">
        <span class="logo-pin" aria-hidden="true"></span>
        <strong>LocalHub</strong>
      </RouterLink>
      <nav aria-label="주요 메뉴">
        <RouterLink to="/#explore">둘러보기</RouterLink>
        <RouterLink to="/#recommend">추천</RouterLink>
        <RouterLink to="/board">커뮤니티</RouterLink>
      </nav>
    </header>

    <RouterView />

    <Transition name="toast">
      <p v-if="toast" class="event-toast" role="status">{{ toast }}</p>
    </Transition>

    <ChatWidget
      @select-location="showIntegrationEvent"
      @select-post="showIntegrationEvent"
    />
  </div>
</template>
