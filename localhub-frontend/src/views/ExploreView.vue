<script setup>
import { computed, inject, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import PlaceDetailModal from '@/components/PlaceDetailModal.vue'
import { CATEGORIES, toLocationCategory } from '@/constants/categories'
import { getLocation, listLocations } from '@/api/locations'

const showIntegrationEvent = inject('showIntegrationEvent')
const route = useRoute()
const PAGE_SIZE = 12

const keywordInput = ref(typeof route.query.keyword === 'string' ? route.query.keyword : '')
const activeCategory = ref(
  typeof route.query.category === 'string' && CATEGORIES.includes(route.query.category)
    ? route.query.category
    : '',
)
const page = ref(1)
const viewMode = ref('grid')

const places = ref([])
const total = ref(0)
const isLoading = ref(true)
const loadError = ref('')

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / PAGE_SIZE)))

async function fetchPlaces() {
  isLoading.value = true
  loadError.value = ''
  try {
    const response = await listLocations({
      category: activeCategory.value ? toLocationCategory(activeCategory.value) : undefined,
      keyword: keywordInput.value.trim() || undefined,
      page: page.value,
      size: PAGE_SIZE,
    })
    places.value = response.items
    total.value = response.total
  } catch (error) {
    loadError.value = error.message || '장소를 불러오지 못했어요.'
  } finally {
    isLoading.value = false
  }
}

onMounted(fetchPlaces)

function isCategoryActive(category) {
  return category === '전체' ? activeCategory.value === '' : activeCategory.value === category
}

function selectCategory(category) {
  activeCategory.value = category === '전체' ? '' : category
  page.value = 1
  fetchPlaces()
}

function handleSearch() {
  page.value = 1
  fetchPlaces()
}

function goToPrevPage() {
  if (page.value === 1) return
  page.value -= 1
  fetchPlaces()
}

function goToNextPage() {
  if (page.value === totalPages.value) return
  page.value += 1
  fetchPlaces()
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
  <main class="explore-page">
    <header class="explore-topbar">
      <RouterLink to="/" class="icon-button" aria-label="뒤로가기">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="m15 5-7 7 7 7" />
        </svg>
      </RouterLink>
      <h1>둘러보기</h1>
      <span class="icon-button-spacer" aria-hidden="true"></span>
    </header>

    <form class="search-bar" @submit.prevent="handleSearch">
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <circle cx="11" cy="11" r="6.5" />
        <path d="m16 16 4 4" />
      </svg>
      <input
        v-model="keywordInput"
        aria-label="찾고 싶은 장소 검색"
        placeholder="찾고 싶은 장소를 검색해 보세요"
      />
      <button type="submit">검색</button>
    </form>

    <div class="category-chips" aria-label="장소 카테고리">
      <button
        type="button"
        :class="{ active: isCategoryActive('전체') }"
        @click="selectCategory('전체')"
      >
        전체
      </button>
      <button
        v-for="category in CATEGORIES"
        :key="category"
        type="button"
        :class="{ active: isCategoryActive(category) }"
        :aria-pressed="isCategoryActive(category)"
        @click="selectCategory(category)"
      >
        {{ category }}
      </button>
    </div>

    <div class="explore-meta">
      <span>총 {{ total }}건</span>
      <div class="view-toggle" role="group" aria-label="보기 방식">
        <button
          type="button"
          class="view-toggle-btn"
          :class="{ active: viewMode === 'grid' }"
          aria-label="그리드로 보기"
          :aria-pressed="viewMode === 'grid'"
          @click="viewMode = 'grid'"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <rect x="3.5" y="3.5" width="7" height="7" rx="1.5" />
            <rect x="13.5" y="3.5" width="7" height="7" rx="1.5" />
            <rect x="3.5" y="13.5" width="7" height="7" rx="1.5" />
            <rect x="13.5" y="13.5" width="7" height="7" rx="1.5" />
          </svg>
        </button>
        <button
          type="button"
          class="view-toggle-btn"
          :class="{ active: viewMode === 'list' }"
          aria-label="리스트로 보기"
          :aria-pressed="viewMode === 'list'"
          @click="viewMode = 'list'"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M4 7h16" />
            <path d="M4 12h16" />
            <path d="M4 17h16" />
          </svg>
        </button>
      </div>
    </div>

    <p v-if="isLoading" class="place-empty">장소를 불러오는 중...</p>
    <p v-else-if="loadError" class="place-empty">{{ loadError }}</p>

    <div v-else-if="viewMode === 'grid'" class="place-grid">
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
          <div v-else class="no-image" aria-hidden="true">
            <svg viewBox="0 0 24 24">
              <path d="M4 18V6a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v12H4Zm0-3 4-4 3 3 2-2 5 5M15.5 9a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3Z" />
            </svg>
            <p>이미지가 제공되지 않는 장소입니다.</p>
          </div>
          <span>{{ place.category }}</span>
        </div>
        <div class="place-body">
          <h3>{{ place.title }}</h3>
          <small>{{ place.addr1 }}</small>
        </div>
      </article>
    </div>

    <ol v-else class="trending-list">
      <li
        v-for="place in places"
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
          <div v-else class="no-image" aria-hidden="true">
            <svg viewBox="0 0 24 24">
              <path d="M4 18V6a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v12H4Zm0-3 4-4 3 3 2-2 5 5M15.5 9a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3Z" />
            </svg>
          </div>
        </div>
        <div class="trending-info">
          <span class="trending-category">{{ place.category }}</span>
          <h3>{{ place.title }}</h3>
          <small>{{ place.addr1 }}</small>
        </div>
      </li>
    </ol>

    <p v-if="!isLoading && !loadError && places.length === 0" class="place-empty">
      조건에 맞는 장소가 없어요.
    </p>

    <nav v-if="totalPages > 1" class="pagination" aria-label="장소 페이지 이동">
      <button
        class="pagination-arrow"
        type="button"
        aria-label="이전 페이지"
        :disabled="page === 1"
        @click="goToPrevPage"
      >
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="m15 5-7 7 7 7" />
        </svg>
      </button>
      <span class="pagination-count">{{ page }} / {{ totalPages }}</span>
      <button
        class="pagination-arrow"
        type="button"
        aria-label="다음 페이지"
        :disabled="page === totalPages"
        @click="goToNextPage"
      >
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="m9 5 7 7-7 7" />
        </svg>
      </button>
    </nav>
  </main>

  <PlaceDetailModal
    :place="selectedPlace"
    :open="isPlaceModalOpen"
    :loading="isPlaceDetailLoading"
    @close="closePlaceModal"
    @select-location="showIntegrationEvent"
  />
</template>

<style scoped>
.explore-page {
  position: relative;
  padding: 24px 0 90px;
}

.explore-topbar {
  display: flex;
  margin-bottom: 18px;
  align-items: center;
  gap: 12px;
}

.explore-topbar h1 {
  margin: 0;
  color: #29272e;
  font-size: 20px;
  font-weight: 780;
  flex: 1;
  text-align: center;
}

.icon-button {
  display: grid;
  width: 38px;
  height: 38px;
  padding: 0;
  color: #29272e;
  background: transparent;
  border: 0;
  border-radius: 8px;
  cursor: pointer;
  place-items: center;
}

.icon-button:hover {
  background: #fafafa;
}

.icon-button svg {
  width: 20px;
  height: 20px;
  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 1.8;
}

.icon-button-spacer {
  width: 38px;
  height: 38px;
}

.explore-page .search-bar {
  width: 100%;
  margin: 0 0 16px;
}

.explore-page .category-chips {
  justify-content: flex-start;
  margin-bottom: 20px;
}

.explore-meta {
  display: flex;
  margin-bottom: 16px;
  align-items: center;
  justify-content: space-between;
}

.explore-meta > span {
  color: #56515d;
  font-size: 12.5px;
  font-weight: 650;
}

.view-toggle {
  display: flex;
  padding: 3px;
  gap: 2px;
  background: #f4f4f5;
  border-radius: 9px;
}

.view-toggle-btn {
  display: grid;
  width: 30px;
  height: 30px;
  padding: 0;
  color: #9b97a0;
  background: transparent;
  border: 0;
  border-radius: 7px;
  cursor: pointer;
  place-items: center;
  transition: background-color 160ms ease, color 160ms ease;
}

.view-toggle-btn:hover {
  color: #56515d;
}

.view-toggle-btn.active {
  color: #29272e;
  background: #fff;
  box-shadow: 0 1px 3px rgb(24 24 27 / 10%);
}

.view-toggle-btn svg {
  width: 16px;
  height: 16px;
  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 1.8;
}

.place-empty {
  padding: 60px 0;
  color: #9b97a0;
  font-size: 13px;
  text-align: center;
}

.pagination {
  display: flex;
  margin-top: 28px;
  gap: 18px;
  align-items: center;
  justify-content: center;
}

.pagination-arrow {
  display: grid;
  width: 36px;
  height: 36px;
  padding: 0;
  color: #29272e;
  background: #fff;
  border: 1px solid #ececef;
  border-radius: 50%;
  cursor: pointer;
  place-items: center;
  transition: border-color 160ms ease, color 160ms ease;
}

.pagination-arrow:hover:not(:disabled) {
  color: #7e66e2;
  border-color: #7e66e2;
}

.pagination-arrow:disabled {
  color: #d0cdd4;
  cursor: not-allowed;
}

.pagination-arrow svg {
  width: 18px;
  height: 18px;
  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 2;
}

.pagination-count {
  min-width: 48px;
  color: #29272e;
  font-size: 13px;
  font-weight: 700;
  text-align: center;
}

</style>
