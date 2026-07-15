<script setup>
import { inject, ref } from 'vue'
import { useRouter } from 'vue-router'
import PlaceDetailModal from '@/components/PlaceDetailModal.vue'
import { CATEGORIES } from '@/constants/categories'
import { eventDateLabel } from '@/utils/date'

const showIntegrationEvent = inject('showIntegrationEvent')
const router = useRouter()
const searchKeyword = ref('')

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

const trendingPlaces = ref([
  {
    content_id: 'mock-trend-1',
    category: '음식점',
    title: '성심당 본점',
    addr1: '대전광역시 중구 대종로 480',
    tel: '',
    lat: 36.3266,
    lng: 127.4246,
    first_image: '',
    avg_rating: 4.8,
    review_count: 1204,
  },
  {
    content_id: 'mock-trend-2',
    category: '관광지',
    title: '대전오월드',
    addr1: '대전광역시 중구 사정공원로 70',
    tel: '',
    lat: 36.2873,
    lng: 127.4001,
    first_image: '',
    avg_rating: 4.7,
    review_count: 892,
  },
  {
    content_id: 'mock-trend-3',
    category: '문화시설',
    title: '한밭수목원',
    addr1: '대전광역시 서구 둔산대로 169',
    tel: '',
    lat: 36.3654,
    lng: 127.3868,
    first_image: '',
    avg_rating: 4.5,
    review_count: 543,
  },
  {
    content_id: 'mock-trend-4',
    category: '관광지',
    title: '대청호반 자전거길',
    addr1: '대전광역시 대덕구 대청로 618-136',
    tel: '',
    lat: 36.4744,
    lng: 127.4815,
    first_image: '',
    avg_rating: 4.6,
    review_count: 376,
  },
  {
    content_id: 'mock-trend-5',
    category: '숙박',
    title: '유성호텔',
    addr1: '대전광역시 유성구 온천로 76',
    tel: '',
    lat: 36.3546,
    lng: 127.3413,
    first_image: '',
    avg_rating: 4.3,
    review_count: 210,
  },
])

const weeklyEvents = ref([
  {
    content_id: 'mock-event-1',
    category: '축제·행사',
    title: '대전 사이언스 페스티벌',
    addr1: '대전광역시 유성구 대덕대로 480',
    tel: '',
    lat: 36.3745,
    lng: 127.3845,
    first_image: '',
    start_date: '20260715',
    end_date: '20260719',
  },
  {
    content_id: 'mock-event-2',
    category: '축제·행사',
    title: '유성 별빛 야시장',
    addr1: '대전광역시 유성구 온천로 12',
    tel: '',
    lat: 36.3548,
    lng: 127.3421,
    first_image: '',
    start_date: '20260717',
    end_date: '20260720',
  },
  {
    content_id: 'mock-event-3',
    category: '축제·행사',
    title: '대청호 반딧불이 축제',
    addr1: '대전광역시 대덕구 대청로 618-136',
    tel: '',
    lat: 36.4744,
    lng: 127.4815,
    first_image: '',
    start_date: '20260718',
    end_date: '20260718',
  },
  {
    content_id: 'mock-event-4',
    category: '축제·행사',
    title: '둔산 분수 음악회',
    addr1: '대전광역시 서구 둔산대로 100',
    tel: '',
    lat: 36.3527,
    lng: 127.3847,
    first_image: '',
    start_date: '20260716',
    end_date: '20260716',
  },
])

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

function searchInBoard() {
  const query = {}
  if (searchKeyword.value.trim()) query.keyword = searchKeyword.value.trim()
  if (selectedCategories.value.length) query.category = selectedCategories.value.join(',')
  router.push({ path: '/board', query })
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
  <main>
    <section id="explore" class="hero-section">
      <p class="eyebrow">대전·충청 여행을 한곳에서</p>
      <h1>오늘은 어디로<br />떠나볼까요?</h1>
      <p class="hero-copy">지역의 장소와 사람들의 생생한 후기를 함께 찾아보세요.</p>
      <form class="search-bar" @submit.prevent="searchInBoard">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <circle cx="11" cy="11" r="6.5" />
          <path d="m16 16 4 4" />
        </svg>
        <input
          v-model="searchKeyword"
          aria-label="지역 또는 장소 검색"
          placeholder="지역 또는 장소를 검색해 보세요"
        />
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

    <section id="trending" class="content-section">
      <div class="section-heading">
        <div>
          <p class="eyebrow">LIVE RANKING</p>
          <h2>실시간 인기 장소</h2>
        </div>
      </div>
      <ol class="trending-list">
        <li
          v-for="(place, index) in trendingPlaces"
          :key="place.content_id"
          class="trending-item"
          @click="openPlace(place)"
        >
          <span class="trending-rank" :class="{ top: index < 3 }">{{ index + 1 }}</span>
          <div class="trending-thumb">
            <img
              v-if="place.first_image"
              :src="place.first_image"
              :alt="`${place.title} 사진`"
              loading="lazy"
            />
          </div>
          <div class="trending-info">
            <span class="trending-category">{{ place.category }}</span>
            <h3>{{ place.title }}</h3>
            <small>{{ place.addr1 }}</small>
          </div>
          <div class="trending-rating">
            <span class="trending-stars">★</span>
            <span>{{ place.avg_rating.toFixed(1) }}</span>
            <small>{{ place.review_count }}건</small>
          </div>
        </li>
      </ol>
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

    <section id="events" class="content-section">
      <div class="section-heading">
        <div>
          <p class="eyebrow">THIS WEEK</p>
          <h2>이번 주 행사·축제</h2>
        </div>
      </div>
      <div class="event-scroll">
        <article
          v-for="event in weeklyEvents"
          :key="event.content_id"
          class="event-card"
          @click="openPlace(event)"
        >
          <div class="event-thumb">
            <img
              v-if="event.first_image"
              :src="event.first_image"
              :alt="`${event.title} 사진`"
              loading="lazy"
            />
            <span class="event-date-badge">{{ eventDateLabel(event) }}</span>
          </div>
          <div class="event-body">
            <h3>{{ event.title }}</h3>
            <small>{{ event.addr1 }}</small>
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
      <RouterLink to="/board" class="community-link-button">커뮤니티 둘러보기</RouterLink>
    </section>
  </main>

  <PlaceDetailModal
    :place="selectedPlace"
    :open="isPlaceModalOpen"
    @close="closePlaceModal"
    @select-location="showIntegrationEvent"
  />
</template>
