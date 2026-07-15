<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { CATEGORIES } from '@/constants/categories'

const route = useRoute()
const PAGE_SIZE = 6

// 백엔드 CORS 허용 전까지 실 API(GET /api/posts) 대신 PostListItem과 동일한 모양의 mock 데이터로 표시
const posts = ref([
  { id: 1, category: '관광지', title: '대청호 벚꽃길 다녀왔어요', rating: 4, view_count: 1204, created_at: '2026-07-14T09:00:00' },
  { id: 2, category: '문화시설', title: '국립중앙과학관 나들이', rating: 5, view_count: 802, created_at: '2026-07-13T11:20:00' },
  { id: 3, category: '레포츠', title: '세종 호수공원 러닝 코스 추천', rating: 4, view_count: 455, created_at: '2026-07-12T18:40:00' },
  { id: 4, category: '쇼핑', title: '청주 수암골 카페 거리 후기', rating: 4, view_count: 233, created_at: '2026-07-10T14:05:00' },
  { id: 5, category: '숙박', title: '유성 온천 힐링 숙소 후기', rating: 5, view_count: 610, created_at: '2026-07-09T20:15:00' },
  { id: 6, category: '음식점', title: '성심당 빵지순례 다녀왔습니다', rating: 5, view_count: 980, created_at: '2026-07-15T08:30:00' },
  { id: 7, category: '여행코스', title: '계룡산 단풍 트레킹 코스', rating: 5, view_count: 320, created_at: '2026-07-08T10:00:00' },
  { id: 8, category: '문화시설', title: '한밭수목원 산책 기록', rating: 4, view_count: 275, created_at: '2026-07-11T16:50:00' },
  { id: 9, category: '축제·행사', title: '대전 사이언스 페스티벌 다녀왔어요', rating: 4, view_count: 190, created_at: '2026-07-15T13:10:00' },
  { id: 10, category: '관광지', title: '장태산 휴양림 출렁다리 후기', rating: 5, view_count: 512, created_at: '2026-07-07T09:40:00' },
  { id: 11, category: '음식점', title: '중앙시장 튀김골목 탐방', rating: 4, view_count: 398, created_at: '2026-07-06T12:15:00' },
  { id: 12, category: '레포츠', title: '갑천 자전거 라이딩 코스', rating: 3, view_count: 164, created_at: '2026-07-05T17:30:00' },
  { id: 13, category: '숙박', title: '계룡산 근처 한옥 스테이 후기', rating: 5, view_count: 287, created_at: '2026-07-04T21:00:00' },
])

const queryCategories = typeof route.query.category === 'string' ? route.query.category.split(',') : []
const selectedCategories = ref(queryCategories.filter((category) => CATEGORIES.includes(category)))
const keyword = ref(typeof route.query.keyword === 'string' ? route.query.keyword : '')
const isSearchOpen = ref(Boolean(keyword.value))
const sortOption = ref('latest')

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

function toggleSearch() {
  isSearchOpen.value = !isSearchOpen.value
  if (!isSearchOpen.value) keyword.value = ''
}

function starDisplay(rating) {
  return '★★★★★'.slice(0, rating).padEnd(5, '☆')
}

const filteredPosts = computed(() => {
  const trimmedKeyword = keyword.value.trim().toLowerCase()
  const filtered = posts.value.filter((post) => {
    const matchesCategory =
      selectedCategories.value.length === 0 || selectedCategories.value.includes(post.category)
    const matchesKeyword = !trimmedKeyword || post.title.toLowerCase().includes(trimmedKeyword)
    return matchesCategory && matchesKeyword
  })

  const sorted = [...filtered]
  if (sortOption.value === 'rating') {
    sorted.sort((a, b) => b.rating - a.rating)
  } else if (sortOption.value === 'views') {
    sorted.sort((a, b) => b.view_count - a.view_count)
  } else {
    sorted.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  }
  return sorted
})

const currentPage = ref(1)
const totalPages = computed(() => Math.max(1, Math.ceil(filteredPosts.value.length / PAGE_SIZE)))

const pagedPosts = computed(() => {
  const start = (currentPage.value - 1) * PAGE_SIZE
  return filteredPosts.value.slice(start, start + PAGE_SIZE)
})

watch(filteredPosts, () => {
  currentPage.value = 1
})

function goToPrevPage() {
  if (currentPage.value > 1) currentPage.value -= 1
}

function goToNextPage() {
  if (currentPage.value < totalPages.value) currentPage.value += 1
}

const writeToast = ref('')
let writeToastTimer

function handleWriteClick() {
  writeToast.value = '글쓰기 화면은 곧 추가될 예정이에요.'
  window.clearTimeout(writeToastTimer)
  writeToastTimer = window.setTimeout(() => {
    writeToast.value = ''
  }, 2400)
}
</script>

<template>
  <main class="board-page">
    <header class="board-topbar">
      <RouterLink to="/" class="icon-button" aria-label="뒤로가기">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="m15 5-7 7 7 7" />
        </svg>
      </RouterLink>
      <h1>게시판</h1>
      <button
        class="icon-button"
        type="button"
        aria-label="검색"
        :aria-pressed="isSearchOpen"
        @click="toggleSearch"
      >
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <circle cx="11" cy="11" r="6.5" />
          <path d="m16 16 4 4" />
        </svg>
      </button>
    </header>

    <div v-if="isSearchOpen" class="board-search">
      <input
        v-model="keyword"
        type="search"
        placeholder="게시글 제목을 검색해 보세요"
        aria-label="게시글 검색"
        autofocus
      />
    </div>

    <div class="category-chips" aria-label="게시글 카테고리 (중복 선택 가능)">
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

    <div class="board-meta">
      <span>총 {{ filteredPosts.length }}건</span>
      <select v-model="sortOption" aria-label="정렬 방식">
        <option value="latest">최신순</option>
        <option value="rating">평점순</option>
        <option value="views">조회순</option>
      </select>
    </div>

    <div class="post-grid">
      <article v-for="post in pagedPosts" :key="post.id" class="post-card">
        <div class="post-image">
          <span>photo</span>
        </div>
        <div class="post-body">
          <h3>{{ post.title }}</h3>
          <p class="post-rating">
            <span class="stars">{{ starDisplay(post.rating) }}</span>
            <span>{{ post.rating.toFixed(1) }}</span>
          </p>
          <small>조회 {{ post.view_count.toLocaleString() }} · {{ post.category }}</small>
        </div>
      </article>
    </div>

    <p v-if="filteredPosts.length === 0" class="post-empty">조건에 맞는 게시글이 없어요.</p>

    <nav v-if="totalPages > 1" class="pagination" aria-label="게시글 페이지 이동">
      <button
        class="pagination-arrow"
        type="button"
        aria-label="이전 페이지"
        :disabled="currentPage === 1"
        @click="goToPrevPage"
      >
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="m15 5-7 7 7 7" />
        </svg>
      </button>
      <span class="pagination-count">{{ currentPage }} / {{ totalPages }}</span>
      <button
        class="pagination-arrow"
        type="button"
        aria-label="다음 페이지"
        :disabled="currentPage === totalPages"
        @click="goToNextPage"
      >
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="m9 5 7 7-7 7" />
        </svg>
      </button>
    </nav>

    <button class="write-fab" type="button" @click="handleWriteClick">
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path d="m16.5 3.5 4 4L8 20l-5 1 1-5Z" />
      </svg>
      글쓰기
    </button>

    <Transition name="toast">
      <p v-if="writeToast" class="event-toast" role="status">{{ writeToast }}</p>
    </Transition>
  </main>
</template>

<style scoped>
.board-page {
  position: relative;
  width: min(1120px, calc(100% - 40px));
  padding: 24px 0 90px;
  margin: 0 auto;
}

.board-topbar {
  display: flex;
  margin-bottom: 18px;
  align-items: center;
  gap: 12px;
}

.board-topbar h1 {
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
  background: #f4f2f7;
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

.board-search {
  margin-bottom: 16px;
}

.board-search input {
  width: 100%;
  min-height: 46px;
  padding: 0 16px;
  color: #29272e;
  font: inherit;
  font-size: 13px;
  background: #fff;
  border: 1px solid #cbc8d0;
  border-radius: 10px;
  outline: 0;
}

.board-search input:focus {
  border-color: #7e66e2;
}

.board-page .category-chips {
  justify-content: flex-start;
  margin-bottom: 20px;
}

.board-meta {
  display: flex;
  margin-bottom: 16px;
  align-items: center;
  justify-content: space-between;
}

.board-meta > span {
  color: #56515d;
  font-size: 12.5px;
  font-weight: 650;
}

.board-meta select {
  padding: 7px 10px;
  color: #56515d;
  font: inherit;
  font-size: 12px;
  font-weight: 650;
  background: #fff;
  border: 1px solid #d7d4db;
  border-radius: 8px;
  cursor: pointer;
}

.post-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(2, 1fr);
}

.post-card {
  overflow: hidden;
  background: #fff;
  border: 1px solid #d7d4db;
  border-radius: 11px;
}

.post-image {
  display: grid;
  height: 150px;
  background-color: #e9e7eb;
  background-image:
    linear-gradient(135deg, rgb(255 255 255 / 46%) 25%, transparent 25%),
    linear-gradient(225deg, rgb(255 255 255 / 46%) 25%, transparent 25%);
  background-position: 0 0, 0 0;
  background-size: 24px 24px;
  place-items: center;
}

.post-image span {
  color: #a19da6;
  font-size: 12px;
  font-weight: 650;
}

.post-body {
  padding: 14px 16px 16px;
}

.post-body h3 {
  margin: 0;
  overflow: hidden;
  color: #29272e;
  font-size: 14px;
  font-weight: 750;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.post-rating {
  display: flex;
  margin: 8px 0 0;
  gap: 6px;
  align-items: center;
  color: #29272e;
  font-size: 12px;
  font-weight: 700;
}

.post-rating .stars {
  color: #e9a900;
  letter-spacing: 1px;
}

.post-body small {
  display: block;
  margin-top: 7px;
  color: #9b97a0;
  font-size: 10.5px;
}

.post-empty {
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
  border: 1px solid #d7d4db;
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

.write-fab {
  position: fixed;
  right: 28px;
  bottom: 100px;
  z-index: 60;
  display: inline-flex;
  padding: 0 20px;
  gap: 7px;
  color: #fff;
  font: inherit;
  font-size: 13px;
  font-weight: 750;
  background: #7e66e2;
  border: 0;
  border-radius: 999px;
  box-shadow: 0 14px 32px rgb(126 102 226 / 38%);
  cursor: pointer;
  align-items: center;
  min-height: 48px;
  transition: transform 180ms ease, box-shadow 180ms ease;
}

.write-fab:hover {
  transform: translateY(-3px);
  box-shadow: 0 18px 36px rgb(126 102 226 / 44%);
}

.write-fab svg {
  width: 18px;
  height: 18px;
  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 2;
}

@media (max-width: 760px) {
  .board-page {
    width: min(100% - 28px, 1120px);
  }

  .post-grid {
    gap: 10px;
  }

  .post-image {
    height: 110px;
  }

  .post-body {
    padding: 10px 11px 12px;
  }

  .write-fab {
    right: 18px;
    bottom: max(90px, calc(env(safe-area-inset-bottom) + 90px));
  }
}
</style>
