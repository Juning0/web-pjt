<script setup>
import { ref } from 'vue'
import ChatWidget from '@/components/ChatWidget.vue'
import PlaceDetailModal from '@/components/PlaceDetailModal.vue'

const toast = ref('')
let toastTimer

function showIntegrationEvent(source) {
  toast.value = `“${source.title}” 선택 이벤트가 전달되었습니다.`
  window.clearTimeout(toastTimer)
  toastTimer = window.setTimeout(() => {
    toast.value = ''
  }, 2800)
}

// 백엔드 CORS 허용 전까지 실 API 대신 mock 데이터로 표시
const places = ref([
  {
    content_id: 'mock-1',
    category: '관광지',
    title: '대전의 새로운 발견',
    addr1: '대전광역시 유성구 대덕대로 480',
    tel: '',
    lat: 36.3745,
    lng: 127.3845,
    first_image: '',
    avg_rating: 4.0,
    review_count: 128,
  },
  {
    content_id: 'mock-2',
    category: '음식점',
    title: '현지인이 찾는 맛집',
    addr1: '대전광역시 중구 대종로 480',
    tel: '',
    lat: 36.3255,
    lng: 127.4215,
    first_image: '',
    avg_rating: 4.6,
    review_count: 342,
  },
  {
    content_id: 'mock-3',
    category: '문화시설',
    title: '주말 문화 산책',
    addr1: '대전광역시 서구 둔산대로 116',
    tel: '',
    lat: 36.3505,
    lng: 127.3845,
    first_image: '',
    avg_rating: 3.8,
    review_count: 56,
  },
])

const CATEGORIES = ['관광지', '음식점', '숙박', '문화시설', '축제·행사']
const selectedCategories = ref([])

function isCategoryActive(category) {
  if (category === '전체') return selectedCategories.value.length === 0
  return selectedCategories.value.includes(category)
}

function toggleCategory(category) {
  if (category === '전체') {
    selectedCategories.value = []
    return
  }
  selectedCategories.value = isCategoryActive(category)
    ? selectedCategories.value.filter((item) => item !== category)
    : [...selectedCategories.value, category]
}

const selectedPlace = ref(null)
const isPlaceModalOpen = ref(false)

function openPlace(place) {
  selectedPlace.value = place
  isPlaceModalOpen.value = true
}

function closePlaceModal() {
  isPlaceModalOpen.value = false
}
</script>

<template>
  <div class="site-shell">
    <header class="site-header">
      <a class="site-logo" href="#" aria-label="LocalHub 홈">
        <span class="logo-pin" aria-hidden="true"></span>
        <strong>LocalHub</strong>
      </a>
      <nav aria-label="주요 메뉴">
        <a href="#explore">둘러보기</a>
        <a href="#recommend">추천</a>
        <a href="#community">커뮤니티</a>
      </nav>
    </header>

    <main>
      <section id="explore" class="hero-section">
        <p class="eyebrow">대전·충청 여행을 한곳에서</p>
        <h1>오늘은 어디로<br />떠나볼까요?</h1>
        <p class="hero-copy">지역의 장소와 사람들의 생생한 후기를 함께 찾아보세요.</p>
        <form class="search-bar" @submit.prevent>
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <circle cx="11" cy="11" r="6.5" />
            <path d="m16 16 4 4" />
          </svg>
          <input aria-label="지역 또는 장소 검색" placeholder="지역 또는 장소를 검색해 보세요" />
          <button type="submit">검색</button>
        </form>
        <div class="category-chips" aria-label="장소 카테고리 (중복 선택 가능)">
          <button
            type="button"
            :class="{ active: isCategoryActive('전체') }"
            @click="toggleCategory('전체')"
          >
            전체
          </button>
          <button
            v-for="category in CATEGORIES"
            :key="category"
            type="button"
            :class="{ active: isCategoryActive(category) }"
            :aria-pressed="isCategoryActive(category)"
            @click="toggleCategory(category)"
          >
            {{ category }}
          </button>
        </div>
      </section>

      <section id="recommend" class="content-section">
        <div class="section-heading">
          <div>
            <p class="eyebrow">LOCAL PICK</p>
            <h2>지금 둘러보기 좋은 장소</h2>
          </div>
          <button type="button">전체 보기 <span aria-hidden="true">→</span></button>
        </div>
        <div class="place-grid">
          <article
            v-for="place in places"
            :key="place.content_id"
            class="place-card"
            @click="openPlace(place)"
          >
            <div class="place-image">
              <img
                v-if="place.first_image"
                :src="place.first_image"
                :alt="`${place.title} 사진`"
                loading="lazy"
              />
              <span>{{ place.category }}</span>
            </div>
            <div class="place-body">
              <h3>{{ place.title }}</h3>
              <small>{{ place.addr1 }}</small>
            </div>
          </article>
        </div>
      </section>

      <section id="community" class="community-banner">
        <div>
          <p class="eyebrow">COMMUNITY</p>
          <h2>직접 다녀온 이야기를 나눠보세요</h2>
          <p>여행 후기와 별점을 남기고, 다른 지역 주민의 추천도 확인할 수 있어요.</p>
        </div>
        <button type="button">커뮤니티 둘러보기</button>
      </section>
    </main>

    <Transition name="toast">
      <p v-if="toast" class="event-toast" role="status">{{ toast }}</p>
    </Transition>

    <ChatWidget
      @select-location="showIntegrationEvent"
      @select-post="showIntegrationEvent"
    />

    <PlaceDetailModal
      :place="selectedPlace"
      :open="isPlaceModalOpen"
      @close="closePlaceModal"
      @select-location="showIntegrationEvent"
    />
  </div>
</template>
