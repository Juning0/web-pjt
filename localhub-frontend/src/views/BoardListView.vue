<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import PostDetailModal from '@/components/PostDetailModal.vue'
import PostWriteModal from '@/components/PostWriteModal.vue'
import { CATEGORIES } from '@/constants/categories'

const route = useRoute()
const PAGE_SIZE = 6

// 백엔드 CORS 허용 전까지 실 API(GET /api/posts) 대신 PostDetail과 동일한 모양의 mock 데이터로 표시
// (좋아요는 백엔드에 아예 없는 필드라 like_count/is_liked도 여기서만 관리한다)
const posts = ref([
  {
    id: 1,
    category: '관광지',
    title: '대청호 벚꽃길 다녀왔어요',
    content: '[활기찬 다람쥐] 대청호 벚꽃길 다녀왔어요! 주차는 오전 9시 전에 도착해야 여유롭고, 산책로는 왕복 1시간 정도 걸려요. 벚꽃 시즌엔 사람이 많으니 평일 방문을 추천합니다.',
    rating: 4,
    view_count: 1204,
    location_id: null,
    created_at: '2026-07-14T09:00:00',
    updated_at: '2026-07-14T09:00:00',
    comments: [
      { id: 101, post_id: 1, content: '[지나가던 수현민] 정보 감사해요!', created_at: '2026-07-14T20:00:00' },
      { id: 102, post_id: 1, content: '[든든한 너구리] 저도 이번 주말에 다녀와야겠어요', created_at: '2026-07-15T08:10:00' },
      { id: 103, post_id: 1, content: '[상냥한 펭귄] 사진 너무 예뻐요 ㅠㅠ', created_at: '2026-07-15T09:30:00' },
    ],
  },
  {
    id: 2,
    category: '문화시설',
    title: '국립중앙과학관 나들이',
    content: '[똑똑한 올빼미] 아이와 함께 다녀왔는데 체험 전시가 많아서 시간 가는 줄 몰랐어요. 주차는 무료였고 평일이라 한산했습니다.',
    rating: 5,
    view_count: 802,
    location_id: null,
    created_at: '2026-07-13T11:20:00',
    updated_at: '2026-07-13T11:20:00',
    comments: [
      { id: 104, post_id: 2, content: '[용감한 고래] 저희 애가 정말 좋아하던 곳이에요', created_at: '2026-07-13T15:00:00' },
    ],
  },
  {
    id: 3,
    category: '레포츠',
    title: '세종 호수공원 러닝 코스 추천',
    content: '[씩씩한 토끼] 호수 둘레길이 평탄해서 러닝하기 좋아요. 저녁엔 조명도 예쁘게 켜져서 야간 러닝도 추천합니다.',
    rating: 4,
    view_count: 455,
    location_id: null,
    created_at: '2026-07-12T18:40:00',
    updated_at: '2026-07-12T18:40:00',
    comments: [],
  },
  {
    id: 4,
    category: '쇼핑',
    title: '청주 수암골 카페 거리 후기',
    content: '[엉뚱한 감자] 골목마다 개성 있는 카페가 많아서 구경하는 재미가 쏠쏠해요. 주말엔 웨이팅이 좀 있는 편입니다.',
    rating: 4,
    view_count: 233,
    location_id: null,
    created_at: '2026-07-10T14:05:00',
    updated_at: '2026-07-10T14:05:00',
    comments: [],
  },
  {
    id: 5,
    category: '숙박',
    title: '유성 온천 힐링 숙소 후기',
    content: '[느긋한 수달] 온천 시설이 깨끗하고 조식도 맛있었어요. 다음에 또 이용하고 싶은 숙소입니다.',
    rating: 5,
    view_count: 610,
    location_id: null,
    created_at: '2026-07-09T20:15:00',
    updated_at: '2026-07-09T20:15:00',
    comments: [
      { id: 105, post_id: 5, content: '[발랄한 당근] 저도 다음 달에 예약해봐야겠어요', created_at: '2026-07-10T09:00:00' },
    ],
  },
  {
    id: 6,
    category: '음식점',
    title: '성심당 빵지순례 다녀왔습니다',
    content: '[유쾌한 호랑이] 튀김소보로는 역시 기본이고, 판타롱부추빵도 꼭 드셔보세요. 아침 일찍 가야 줄이 짧아요.',
    rating: 5,
    view_count: 980,
    location_id: null,
    created_at: '2026-07-15T08:30:00',
    updated_at: '2026-07-15T08:30:00',
    comments: [
      { id: 106, post_id: 6, content: '[멋진 수박] 저도 오늘 다녀왔는데 진짜 맛있어요', created_at: '2026-07-15T12:00:00' },
      { id: 107, post_id: 6, content: '[수줍은 고양이] 부추빵 추천 감사합니다', created_at: '2026-07-15T13:40:00' },
    ],
  },
  {
    id: 7,
    category: '여행코스',
    title: '계룡산 단풍 트레킹 코스',
    content: '[잘생긴 다람쥐] 동학사에서 시작하는 코스가 초보자도 무리 없이 즐길 수 있어서 좋았어요. 편한 신발은 필수입니다.',
    rating: 5,
    view_count: 320,
    location_id: null,
    created_at: '2026-07-08T10:00:00',
    updated_at: '2026-07-08T10:00:00',
    comments: [],
  },
  {
    id: 8,
    category: '문화시설',
    title: '한밭수목원 산책 기록',
    content: '[상냥한 토끼] 규모가 커서 다 둘러보는 데 두 시간 정도 걸렸어요. 그늘이 많아서 여름에도 걷기 괜찮았습니다.',
    rating: 4,
    view_count: 275,
    location_id: null,
    created_at: '2026-07-11T16:50:00',
    updated_at: '2026-07-11T16:50:00',
    comments: [],
  },
  {
    id: 9,
    category: '축제·행사',
    title: '대전 사이언스 페스티벌 다녀왔어요',
    content: '[든든한 호랑이] 체험 부스가 정말 많아서 아이들이 지루할 틈이 없었어요. 주말엔 사람이 많아 오픈런을 추천합니다.',
    rating: 4,
    view_count: 190,
    location_id: null,
    created_at: '2026-07-15T13:10:00',
    updated_at: '2026-07-15T13:10:00',
    comments: [],
  },
  {
    id: 10,
    category: '관광지',
    title: '장태산 휴양림 출렁다리 후기',
    content: '[씩씩한 수달] 출렁다리에서 보는 뷰가 정말 좋아요. 편의시설도 잘 되어 있어서 가족 나들이로 추천합니다.',
    rating: 5,
    view_count: 512,
    location_id: null,
    created_at: '2026-07-07T09:40:00',
    updated_at: '2026-07-07T09:40:00',
    comments: [],
  },
  {
    id: 11,
    category: '음식점',
    title: '중앙시장 튀김골목 탐방',
    content: '[용감한 감자] 골목 전체가 튀김 냄새로 가득해요. 가성비 좋은 맛집이 많아서 여러 곳 돌아다니는 재미가 있습니다.',
    rating: 4,
    view_count: 398,
    location_id: null,
    created_at: '2026-07-06T12:15:00',
    updated_at: '2026-07-06T12:15:00',
    comments: [],
  },
  {
    id: 12,
    category: '레포츠',
    title: '갑천 자전거 라이딩 코스',
    content: '[엉뚱한 펭귄] 강변 라이딩 코스가 잘 정비되어 있어요. 다만 주말 오후엔 유동인구가 많아 속도를 줄여야 합니다.',
    rating: 3,
    view_count: 164,
    location_id: null,
    created_at: '2026-07-05T17:30:00',
    updated_at: '2026-07-05T17:30:00',
    comments: [],
  },
  {
    id: 13,
    category: '숙박',
    title: '계룡산 근처 한옥 스테이 후기',
    content: '[느긋한 고래] 한옥 특유의 분위기가 정말 좋았고, 사장님이 친절하게 주변 맛집도 알려주셨어요.',
    rating: 5,
    view_count: 287,
    location_id: null,
    created_at: '2026-07-04T21:00:00',
    updated_at: '2026-07-04T21:00:00',
    comments: [],
  },
].map((post) => ({ ...post, like_count: Math.round(post.view_count / 6), is_liked: false })))

const queryCategories = typeof route.query.category === 'string' ? route.query.category.split(',') : []
const selectedCategories = ref(queryCategories.filter((category) => CATEGORIES.includes(category)))
const keyword = ref(typeof route.query.keyword === 'string' ? route.query.keyword : '')
const isSearchOpen = ref(Boolean(keyword.value))
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
    isSearchOpen.value = Boolean(keyword.value)

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

function toggleSearch() {
  isSearchOpen.value = !isSearchOpen.value
  if (!isSearchOpen.value) keyword.value = ''
}

function starDisplay(rating) {
  return '★★★★★'.slice(0, rating).padEnd(5, '☆')
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

function showWriteToast(message) {
  writeToast.value = message
  window.clearTimeout(writeToastTimer)
  writeToastTimer = window.setTimeout(() => {
    writeToast.value = ''
  }, 2400)
}

const selectedPost = ref(null)
const isPostModalOpen = ref(false)

function openPost(post) {
  selectedPost.value = post
  isPostModalOpen.value = true
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
      <article
        v-for="post in pagedPosts"
        :key="post.id"
        class="post-card"
        @click="openPost(post)"
      >
        <div class="post-body">
          <span class="post-category">{{ post.category }}</span>
          <h3>{{ post.title }}</h3>
          <p class="post-rating">
            <span class="stars">{{ starDisplay(post.rating) }}</span>
            <span>{{ post.rating.toFixed(1) }}</span>
          </p>
          <small>조회 {{ post.view_count.toLocaleString() }} · {{ formatDate(post.created_at) }}</small>
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
      @close="closePostModal"
      @deleted="handlePostDeleted"
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
  padding: 16px;
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

.post-body h3 {
  margin: 8px 0 0;
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

  .post-body {
    padding: 12px 13px 14px;
  }

  .write-fab {
    right: 18px;
    bottom: max(90px, calc(env(safe-area-inset-bottom) + 90px));
  }
}
</style>
