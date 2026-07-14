<script setup lang="ts">
import SearchBar from '../components/SearchBar.vue'
import CategoryFilter from '../components/CategoryFilter.vue'
import EventBanner from '../components/EventBanner.vue'
import PostCard from '../components/PostCard.vue'
import SideEventPanel from '../components/SideEventPanel.vue'
import { ref } from 'vue'

interface Post {
  id: number
  title: string
  category: string
  rating: number
  viewCount: number
}

const posts = ref<Post[]>([
  {
    id: 1,
    title: '대청호 벚꽃길 다녀왔어요',
    category: '관광지',
    rating: 4.0,
    viewCount: 1204
  },
  {
    id: 2,
    title: '성심당 뮤이팅 꿀팁',
    category: '쇼핑',
    rating: 5.0,
    viewCount: 987
  },
  {
    id: 3,
    title: '계족산 황툰길 맨발 트레킹',
    category: '레포츠',
    rating: 4.5,
    viewCount: 761
  },
  {
    id: 4,
    title: '단양 파괴골차이 닭',
    category: '숙박',
    rating: 5.0,
    viewCount: 1930
  }
])
</script>

<template>
  <div class="home-page">
    <SearchBar />
    <CategoryFilter />
    <EventBanner />

    <div class="main-content">
      <SideEventPanel class="side-panel-top" />

      <div class="posts-section">
        <div class="section-header">
          <h2 class="section-title">🔥 인기 게시글</h2>
        </div>

        <div class="posts-grid">
          <PostCard v-for="post in posts" :key="post.id" :post="post" />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-page {
  width: 100%;
  min-height: 100vh;
  background-color: #ffffff;
}

.main-content {
  width: 100%;
  padding: 16px 20px;
  background-color: #ffffff;
  max-width: 1200px;
  margin: 0 auto;
}

.side-panel-top {
  margin-bottom: 32px;
}

.posts-section {
  width: 100%;
}

.section-header {
  margin-bottom: 16px;
}

.section-title {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #333;
}

.posts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

@media (max-width: 768px) {
  .main-content {
    padding: 12px 16px;
  }

  .side-panel-top {
    margin-bottom: 20px;
  }

  .section-title {
    font-size: 16px;
  }

  .posts-grid {
    gap: 12px;
  }
}

@media (max-width: 640px) {
  .main-content {
    padding: 12px 12px;
  }

  .posts-grid {
    gap: 10px;
  }
}
</style>
