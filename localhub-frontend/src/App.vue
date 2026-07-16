<script setup>
import { provide, ref } from 'vue'
import { useRouter } from 'vue-router'
import ChatWidget from '@/components/ChatWidget.vue'

const router = useRouter()
const toast = ref('')
let toastTimer

function showToast(message) {
  toast.value = message
  window.clearTimeout(toastTimer)
  toastTimer = window.setTimeout(() => {
    toast.value = ''
  }, 2800)
}

function showIntegrationEvent(source) {
  showToast(`“${source.title}” 선택 이벤트가 전달되었습니다.`)
}

function openLocationFromChat(source) {
  const latitude = source.latitude ?? source.lat
  const longitude = source.longitude ?? source.lng
  if (latitude == null || longitude == null) {
    showToast(`“${source.title}”의 지도 좌표가 없습니다.`)
    return
  }

  showIntegrationEvent(source)
  const query = {
    id: String(source.id ?? source.content_id ?? ''),
    title: source.title ?? '',
    category: source.category ?? '',
    address: source.address ?? source.addr1 ?? '',
    lat: String(latitude),
    lng: String(longitude),
  }
  if (source.rating != null || source.avg_rating != null) {
    query.rating = String(source.rating ?? source.avg_rating)
  }
  if (source.review_count != null) {
    query.reviews = String(source.review_count)
  }
  if (source.image_url || source.first_image) {
    query.image = source.image_url || source.first_image
  }
  router.push({ name: 'map', query })
}

function openPostFromChat(source) {
  showIntegrationEvent(source)
  router.push({ path: '/board', query: { keyword: source.title } })
}

provide('showIntegrationEvent', openLocationFromChat)
</script>

<template>
  <div class="site-shell">
    <header class="site-header">
      <RouterLink class="site-logo" to="/" aria-label="LocalHub 홈">
        <span class="logo-pin" aria-hidden="true"></span>
        <strong>LocalHub</strong>
      </RouterLink>
      <nav aria-label="주요 메뉴">
        <RouterLink to="/explore">둘러보기</RouterLink>
        <RouterLink to="/map">지도</RouterLink>
        <RouterLink to="/board">커뮤니티</RouterLink>
      </nav>
    </header>

    <div class="page-shell">
      <RouterView />
    </div>

    <Transition name="toast">
      <p v-if="toast" class="event-toast" role="status">{{ toast }}</p>
    </Transition>

    <ChatWidget
      @select-location="openLocationFromChat"
      @select-post="openPostFromChat"
    />
  </div>
</template>
