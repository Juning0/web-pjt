<script setup>
import { inject, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import PlaceDetailModal from '@/components/PlaceDetailModal.vue'
import { CATEGORIES, toLocationCategory } from '@/constants/categories'
import { getLocation, listLocations } from '@/api/locations'

const showIntegrationEvent = inject('showIntegrationEvent')
const router = useRouter()
const searchKeyword = ref('')

// 실제 공공데이터(GET /api/locations)를 보여준다. 목록 API는 avg_rating/review_count,
// 행사 날짜(start_date/end_date)를 제공하지 않아 해당 정보는 표시하지 않는다.
const places = ref([])
const trendingPlaces = ref([])
const weeklyEvents = ref([])

onMounted(async () => {
  try {
    const [recommend, trending, events] = await Promise.all([
      listLocations({ size: 3 }),
      listLocations({ category: toLocationCategory('음식점'), size: 5 }),
      listLocations({ category: toLocationCategory('축제·행사'), size: 4 }),
    ])
    places.value = recommend.items
    trendingPlaces.value = trending.items
    weeklyEvents.value = events.items
  } catch {
    // 홈 화면 추천 섹션은 부가 정보라 실패해도 조용히 비워둔다.
  }
})

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
const isPlaceDetailLoading = ref(false)

async function openPlace(place) {
  isPlaceModalOpen.value = true
  isPlaceDetailLoading.value = true
  selectedPlace.value = null
  try {
    selectedPlace.value = await getLocation(place.content_id)
  } catch {
    selectedPlace.value = place
  } finally {
    isPlaceDetailLoading.value = false
  }
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
          <p class="eyebrow">LOCAL FOOD</p>
          <h2>요즘 찾는 음식점</h2>
        </div>
      </div>
      <ol class="trending-list">
        <li
          v-for="place in trendingPlaces"
          :key="place.content_id"
          class="trending-item"
          @click="openPlace(place)"
        >
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
    :loading="isPlaceDetailLoading"
    @close="closePlaceModal"
    @select-location="showIntegrationEvent"
  />
</template>
