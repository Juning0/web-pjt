<script setup lang="ts">
import { ref, computed } from 'vue'
import BoardHeader from '../components/BoardHeader.vue'
import SortBar from '../components/SortBar.vue'
import WriteButton from '../components/WriteButton.vue'

interface Post {
  id: number
  title: string
  category: string
  rating: number
  viewCount: number
  createdAt: string
}

const categories = [
  { id: 1, name: '전체' },
  { id: 2, name: '관광지' },
  { id: 3, name: '레포츠' },
  { id: 4, name: '문화시설' },
  { id: 5, name: '쇼핑' },
  { id: 6, name: '숙박' },
  { id: 7, name: '여행코스' },
  { id: 8, name: '축제행사' }
]

const selectedCategories = ref<Set<number>>(new Set([1]))
const currentPage = ref(1)
const postsPerPage = 6
const sortBy = ref('최신순')

const allPosts = ref<Post[]>([
  {
    id: 1,
    title: '대청호 벚꽃길 다녀왔어요',
    category: '관광지',
    rating: 4.0,
    viewCount: 1204,
    createdAt: '2026-07-14'
  },
  {
    id: 2,
    title: '국립충아과학관',
    category: '문화시설',
    rating: 4.8,
    viewCount: 802,
    createdAt: '2026-07-13'
  },
  {
    id: 3,
    title: '세종호 우공원 러닝',
    category: '레포츠',
    rating: 4.2,
    viewCount: 455,
    createdAt: '2026-07-12'
  },
  {
    id: 4,
    title: '천우 우앙굿 카페',
    category: '쇼핑',
    rating: 3.9,
    viewCount: 233,
    createdAt: '2026-07-11'
  },
  {
    id: 5,
    title: '대청호 벚꽃길 다녀왔어요',
    category: '관광지',
    rating: 4.0,
    viewCount: 1204,
    createdAt: '2026-07-10'
  },
  {
    id: 6,
    title: '국립충아과학관',
    category: '문화시설',
    rating: 4.8,
    viewCount: 802,
    createdAt: '2026-07-09'
  },
  {
    id: 7,
    title: '세종호 우공원 러닝',
    category: '레포츠',
    rating: 4.2,
    viewCount: 455,
    createdAt: '2026-07-08'
  },
  {
    id: 8,
    title: '천우 우앙굿 카페',
    category: '쇼핑',
    rating: 3.9,
    viewCount: 233,
    createdAt: '2026-07-07'
  },
  {
    id: 9,
    title: '대청호 벚꽃길 다녀왔어요',
    category: '관광지',
    rating: 4.0,
    viewCount: 1204,
    createdAt: '2026-07-06'
  },
  {
    id: 10,
    title: '국립충아과학관',
    category: '문화시설',
    rating: 4.8,
    viewCount: 802,
    createdAt: '2026-07-05'
  }
])

const totalCount = allPosts.value.length

const selectCategory = (categoryId: number) => {
  if (categoryId === 1) {
    selectedCategories.value.clear()
    selectedCategories.value.add(1)
  } else {
    if (selectedCategories.value.has(1)) {
      selectedCategories.value.delete(1)
    }
    if (selectedCategories.value.has(categoryId)) {
      selectedCategories.value.delete(categoryId)
    } else {
      selectedCategories.value.add(categoryId)
    }
  }
  currentPage.value = 1
}

const isCategorySelected = (categoryId: number) => {
  return selectedCategories.value.has(categoryId)
}

const filteredPosts = () => {
  if (selectedCategories.value.has(1)) {
    return allPosts.value
  }
  const selectedCategoryNames = Array.from(selectedCategories.value)
    .map(id => categories.find(c => c.id === id)?.name)
    .filter(Boolean)

  if (selectedCategoryNames.length === 0) {
    return allPosts.value
  }
  return allPosts.value.filter(p => selectedCategoryNames.includes(p.category))
}

const sortPosts = (postsToSort: Post[]) => {
  const sorted = [...postsToSort]
  if (sortBy.value === '최신순') {
    sorted.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
  } else if (sortBy.value === '조회순') {
    sorted.sort((a, b) => b.viewCount - a.viewCount)
  } else if (sortBy.value === '평점높은순') {
    sorted.sort((a, b) => b.rating - a.rating)
  }
  return sorted
}

const posts = computed(() => {
  const filtered = filteredPosts()
  const sorted = sortPosts(filtered)
  const startIndex = (currentPage.value - 1) * postsPerPage
  return sorted.slice(startIndex, startIndex + postsPerPage)
})

const totalPages = computed(() => {
  return Math.ceil(filteredPosts().length / postsPerPage)
})

const goToPage = (page: number) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

const renderStars = (rating: number) => {
  const fullStars = Math.floor(rating)
  const hasHalf = rating % 1 !== 0
  return { full: fullStars, half: hasHalf ? 1 : 0, empty: 5 - fullStars - (hasHalf ? 1 : 0) }
}
</script>

<template>
  <div class="board-list-page">
    <BoardHeader />

    <div class="category-container">
      <div class="category-wrapper">
        <button
          v-for="category in categories"
          :key="category.id"
          :class="['category-btn', { active: isCategorySelected(category.id) }]"
          @click="selectCategory(category.id)"
        >
          {{ category.name }}
        </button>
      </div>
    </div>

    <SortBar :total-count="filteredPosts().length" @sort-change="(sort) => { sortBy = sort; currentPage = 1 }" />

    <div class="main-content">
      <div class="content-wrapper">
        <div class="posts-grid" v-if="posts.length">
          <div v-for="post in posts" :key="post.id" class="post-card">
            <div class="post-image">
              <div class="image-placeholder">photo</div>
            </div>
            <div class="post-content">
              <h3 class="post-title">{{ post.title }}</h3>
              <div class="post-meta">
                <div class="rating-section">
                  <span class="stars">
                    <span v-for="_ in renderStars(post.rating).full" :key="`full`" class="star full">★</span>
                    <span v-if="renderStars(post.rating).half" class="star half">★</span>
                    <span v-for="_ in renderStars(post.rating).empty" :key="`empty`" class="star empty">★</span>
                    <span class="rating-value">{{ post.rating.toFixed(1) }}</span>
                  </span>
                </div>
                <span class="view-count">조회 {{ post.viewCount }}</span>
                <span class="category">{{ post.category }}</span>
              </div>
              <div class="post-date">{{ post.createdAt }}</div>
            </div>
          </div>
        </div>

        <div v-if="posts.length" class="pagination">
          <button
            class="pagination-btn"
            :disabled="currentPage === 1"
            @click="goToPage(currentPage - 1)"
          >
            이전
          </button>

          <div class="page-numbers">
            <span class="page-info">
              {{ currentPage }}/{{ totalPages }}
            </span>
          </div>

          <button
            class="pagination-btn"
            :disabled="currentPage === totalPages"
            @click="goToPage(currentPage + 1)"
          >
            다음
          </button>
        </div>

        <div v-if="!posts.length" class="no-posts">
          게시글이 없습니다.
        </div>
      </div>
    </div>

    <WriteButton />
  </div>
</template>

<style scoped>
.board-list-page {
  width: 100%;
  min-height: 100vh;
  background-color: #ffffff;
}

.category-container {
  width: 100%;
  padding: 12px 20px;
  background-color: #ffffff;
  border-bottom: 1px solid #f0f0f0;
  overflow-x: auto;
  overflow-y: hidden;
  -webkit-overflow-scrolling: touch;
}

.category-container::-webkit-scrollbar {
  height: 4px;
}

.category-container::-webkit-scrollbar-track {
  background-color: transparent;
}

.category-container::-webkit-scrollbar-thumb {
  background-color: #ddd;
  border-radius: 2px;
}

.category-wrapper {
  display: flex;
  gap: 8px;
  padding: 0;
  min-width: min-content;
  margin: 0 auto;
}

.category-btn {
  padding: 8px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 20px;
  background-color: #ffffff;
  color: #666;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.category-btn:hover {
  border-color: #333;
  color: #333;
}

.category-btn.active {
  background-color: #333;
  color: #ffffff;
  border-color: #333;
}

.main-content {
  width: 100%;
  padding: 20px;
  background-color: #ffffff;
}

.content-wrapper {
  max-width: 1200px;
  margin: 0 auto;
}

.posts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.post-card {
  background-color: #ffffff;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.2s;
  cursor: pointer;
}

.post-card:hover {
  border-color: #333;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.post-image {
  width: 100%;
  aspect-ratio: 16 / 9;
  background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.image-placeholder {
  color: #ccc;
  font-size: 14px;
  font-weight: 500;
}

.post-content {
  padding: 16px;
}

.post-title {
  margin: 0 0 12px 0;
  font-size: 15px;
  font-weight: 600;
  color: #333;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.post-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #666;
  flex-wrap: wrap;
}

.rating-section {
  display: flex;
  align-items: center;
}

.stars {
  display: inline-flex;
  align-items: center;
  gap: 3px;
}

.star {
  font-size: 14px;
  line-height: 1;
}

.star.full {
  color: #ff9500;
}

.star.half {
  color: #ff9500;
  position: relative;
  overflow: hidden;
  width: 0.5em;
}

.star.empty {
  color: #e5e7eb;
}

.rating-value {
  font-size: 13px;
  font-weight: 600;
  color: #333;
  margin-left: 2px;
}

.view-count,
.category {
  color: #999;
  font-size: 12px;
}

.post-date {
  margin-top: 10px;
  font-size: 12px;
  color: #bbb;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 32px;
  padding: 20px 0;
}

.pagination-btn {
  padding: 8px 16px;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  background-color: #ffffff;
  color: #333;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.pagination-btn:hover:not(:disabled) {
  border-color: #333;
  background-color: #f9f9f9;
}

.pagination-btn:disabled {
  color: #ccc;
  border-color: #e5e7eb;
  cursor: not-allowed;
}

.page-numbers {
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-info {
  font-size: 13px;
  color: #666;
  font-weight: 500;
}

.no-posts {
  text-align: center;
  padding: 40px 20px;
  color: #999;
  font-size: 14px;
}

@media (max-width: 768px) {
  .category-container {
    padding: 12px 16px;
  }

  .main-content {
    padding: 16px;
  }

  .posts-grid {
    gap: 12px;
  }
}

@media (max-width: 640px) {
  .category-container {
    padding: 10px 12px;
    overflow-x: visible;
  }

  .category-wrapper {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
    min-width: auto;
    margin: 0;
  }

  .category-btn {
    padding: 6px 12px;
    font-size: 13px;
  }

  .main-content {
    padding: 12px;
  }

  .posts-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }

  .post-content {
    padding: 12px;
  }

  .post-title {
    font-size: 14px;
    margin-bottom: 8px;
  }

  .post-meta {
    gap: 6px;
    font-size: 12px;
  }
}
</style>
