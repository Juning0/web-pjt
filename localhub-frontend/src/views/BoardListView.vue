<script setup>
import { computed, inject, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import LocationSearchInput from '@/components/LocationSearchInput.vue'
import PostDetailModal from '@/components/PostDetailModal.vue'
import PostWriteModal from '@/components/PostWriteModal.vue'
import { CATEGORIES } from '@/constants/categories'
import { getPost, listAllPosts } from '@/api/posts'

const showIntegrationEvent = inject('showIntegrationEvent')
const route = useRoute()
const PAGE_SIZE = 6

// 목록 API(PostListItem)는 본문·댓글이 없어, 상세를 열 때 getPost로 채운 뒤 같은 배열 항목에 캐싱한다.
const posts = ref([])
const isLoading = ref(true)
const loadError = ref('')

async function fetchPosts() {
  isLoading.value = true
  loadError.value = ''
  try {
    posts.value = await listAllPosts()
  } catch (error) {
    loadError.value = error.message || '게시글을 불러오지 못했어요.'
  } finally {
    isLoading.value = false
  }
}

onMounted(fetchPosts)

const queryCategories = typeof route.query.category === 'string' ? route.query.category.split(',') : []
const selectedCategories = ref(queryCategories.filter((category) => CATEGORIES.includes(category)))
const keyword = ref(typeof route.query.keyword === 'string' ? route.query.keyword : '')
const selectedLocationFilter = ref(null)
const sortOption = ref('latest')

watch(
  () => [route.query.category, route.query.keyword],
  ([categoryQuery, keywordQuery]) => {
    const categories =
      typeof categoryQuery === 'string' ? categoryQuery.split(',') : []

    selectedCategories.value = categories.filter((category) =>
      CATEGORIES.includes(category),
    )

    keyword.value = typeof keywordQuery === 'string' ? keywordQuery : ''

    fetchPosts()
  },
)

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

function formatDate(value) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  return `${date.getFullYear()}.${String(date.getMonth() + 1).padStart(2, '0')}.${String(date.getDate()).padStart(2, '0')}`
}

const filteredPosts = computed(() => {
  const trimmedKeyword = keyword.value.trim().toLowerCase()
  const filtered = posts.value.filter((post) => {
    const matchesCategory =
      selectedCategories.value.length === 0 || selectedCategories.value.includes(post.category)
    const matchesKeyword = !trimmedKeyword || post.title.toLowerCase().includes(trimmedKeyword)
    const matchesLocation =
      !selectedLocationFilter.value || post.location_id === selectedLocationFilter.value.content_id
    return matchesCategory && matchesKeyword && matchesLocation
  })

  const sorted = [...filtered]
  if (sortOption.value === 'views') {
    sorted.sort((a, b) => b.view_count - a.view_count)
  } else if (sortOption.value === 'rating') {
    // 평점 없는 글은 뒤로 밀린다.
    sorted.sort((a, b) => (b.rating ?? -1) - (a.rating ?? -1))
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

function showWriteToast(message) {
  writeToast.value = message
  window.clearTimeout(writeToastTimer)
  writeToastTimer = window.setTimeout(() => {
    writeToast.value = ''
  }, 2400)
}

const selectedPost = ref(null)
const isPostModalOpen = ref(false)
const isPostDetailLoading = ref(false)

async function openPost(post) {
  const index = posts.value.findIndex((item) => item.id === post.id)
  const cached = index === -1 ? null : posts.value[index]

  // 이미 상세(본문·댓글)를 불러온 적이 있으면 같은 객체를 재사용해 조회수 중복 증가를 피한다.
  // GET /api/posts/{id}는 호출할 때마다 조회수를 올린다.
  if (cached?.comments) {
    selectedPost.value = cached
    isPostModalOpen.value = true
    return
  }

  isPostModalOpen.value = true
  isPostDetailLoading.value = true
  selectedPost.value = null

  try {
    const detail = await getPost(post.id)
    if (index !== -1) posts.value[index] = detail
    selectedPost.value = detail
  } catch (error) {
    isPostModalOpen.value = false
    showWriteToast(error.message || '게시글을 불러오지 못했어요.')
  } finally {
    isPostDetailLoading.value = false
  }
}

function closePostModal() {
  isPostModalOpen.value = false
}

function handlePostDeleted(postId) {
  posts.value = posts.value.filter((post) => post.id !== postId)
  showWriteToast('게시글이 삭제되었어요.')
}

const isWriteModalOpen = ref(false)

function openWriteModal() {
  isWriteModalOpen.value = true
}

function closeWriteModal() {
  isWriteModalOpen.value = false
}

function handlePostCreated(newPost) {
  posts.value = [newPost, ...posts.value]
  isWriteModalOpen.value = false
  showWriteToast('게시글이 등록되었어요.')
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
      <span class="header-spacer" aria-hidden="true"></span>
    </header>

    <div class="board-search">
      <LocationSearchInput v-model="selectedLocationFilter" placeholder="장소명으로 검색해 보세요" />
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
        <option value="views">조회순</option>
        <option value="rating">평점순</option>
      </select>
    </div>

    <p v-if="isLoading" class="post-empty">게시글을 불러오는 중...</p>
    <p v-else-if="loadError" class="post-empty">{{ loadError }}</p>

    <div v-else class="post-grid">
      <article
        v-for="post in pagedPosts"
        :key="post.id"
        class="post-card"
        @click="openPost(post)"
      >
        <div class="post-body">
          <div class="post-pill-row">
            <span class="post-category">{{ post.category }}</span>
            <span v-if="post.location_title" class="post-location">📍 {{ post.location_title }}</span>
            <span v-if="post.rating != null" class="post-rating">★ {{ post.rating.toFixed(1) }}</span>
          </div>
          <h3>{{ post.title }}</h3>
          <small>조회 {{ post.view_count.toLocaleString() }} · {{ formatDate(post.created_at) }}</small>
        </div>
        <div v-if="post.location_image" class="post-thumb">
          <img :src="post.location_image" :alt="`${post.location_title} 사진`" loading="lazy" />
        </div>
      </article>
    </div>

    <p v-if="!isLoading && !loadError && filteredPosts.length === 0" class="post-empty">조건에 맞는 게시글이 없어요.</p>

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

    <button class="write-fab" type="button" @click="openWriteModal">
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path d="m16.5 3.5 4 4L8 20l-5 1 1-5Z" />
      </svg>
      글쓰기
    </button>

    <Transition name="toast">
      <p v-if="writeToast" class="event-toast" role="status">{{ writeToast }}</p>
    </Transition>

    <PostDetailModal
      :post="selectedPost"
      :open="isPostModalOpen"
      :loading="isPostDetailLoading"
      @close="closePostModal"
      @deleted="handlePostDeleted"
      @select-location="showIntegrationEvent"
    />

    <PostWriteModal
      :open="isWriteModalOpen"
      @close="closeWriteModal"
      @created="handlePostCreated"
    />
  </main>
</template>

<style scoped>
.board-page {
  position: relative;
  padding: 24px 0 90px;
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

.header-spacer {
  width: 38px;
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
  display: flex;
  margin-bottom: 16px;
  gap: 10px;
  flex-direction: column;
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
  display: flex;
  overflow: hidden;
  cursor: pointer;
  background: #fff;
  border: 1px solid #d7d4db;
  border-radius: 11px;
  transition: transform 180ms ease, box-shadow 180ms ease;
}

.post-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 15px 36px rgb(40 36 49 / 10%);
}

.post-body {
  min-width: 0;
  padding: 16px;
  flex: 1;
}

.post-thumb {
  overflow: hidden;
  width: 92px;
  flex: 0 0 auto;
  background-color: #f4f2f7;
}

.post-thumb img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.post-pill-row {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.post-category {
  display: inline-block;
  padding: 4px 10px;
  color: #7e66e2;
  font-size: 10px;
  font-weight: 750;
  background: #f1edff;
  border-radius: 999px;
}

.post-location {
  display: inline-block;
  max-width: 100%;
  padding: 4px 10px;
  overflow: hidden;
  color: #56515d;
  font-size: 10px;
  font-weight: 750;
  text-overflow: ellipsis;
  white-space: nowrap;
  background: #f4f2f7;
  border-radius: 999px;
}

.post-rating {
  display: inline-block;
  padding: 4px 10px;
  color: #a9760a;
  font-size: 10px;
  font-weight: 750;
  background: #fdf1dc;
  border-radius: 999px;
}

.post-body h3 {
  margin: 8px 0 0;
  overflow: hidden;
  color: #29272e;
  font-size: 14px;
  font-weight: 750;
  text-overflow: ellipsis;
  white-space: nowrap;
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
  .post-grid {
    gap: 10px;
  }

  .post-body {
    padding: 12px 13px 14px;
  }

  .write-fab {
    right: 18px;
    bottom: max(90px, calc(env(safe-area-inset-bottom) + 90px));
  }
}

@media (min-width: 761px) {
  .board-topbar h1 {
    font-size: 23px;
  }

  .board-meta > span {
    font-size: 14px;
  }

  .board-meta select {
    font-size: 13.5px;
  }

  .post-category,
  .post-location,
  .post-rating {
    font-size: 11.5px;
  }

  .post-body h3 {
    font-size: 16px;
  }

  .post-body small {
    font-size: 12px;
  }

  .post-empty {
    font-size: 14px;
  }

  .pagination-count {
    font-size: 14px;
  }

  .write-fab {
    font-size: 14px;
  }
}
</style>
