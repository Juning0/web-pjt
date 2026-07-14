<script setup lang="ts">
interface Post {
  id: number
  title: string
  category: string
  rating: number
  viewCount: number
  imageUrl?: string
}

defineProps<{
  post: Post
}>()

const renderStars = (rating: number) => {
  const fullStars = Math.floor(rating)
  const hasHalf = rating % 1 !== 0
  const emptyStars = 5 - fullStars - (hasHalf ? 1 : 0)

  return {
    full: fullStars,
    half: hasHalf ? 1 : 0,
    empty: emptyStars
  }
}
</script>

<template>
  <div class="post-card">
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
    </div>
  </div>
</template>

<style scoped>
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

@media (max-width: 640px) {
  .post-card {
    border-radius: 8px;
  }

  .post-image {
    aspect-ratio: 4 / 3;
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
