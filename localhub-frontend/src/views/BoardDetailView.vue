<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const postId = route.params.id

interface Comment {
  id: number
  author: string
  content: string
  createdAt: string
}

interface Post {
  id: number
  title: string
  category: string
  rating: number
  author: string
  viewCount: number
  createdAt: string
  content: string
  images: string[]
}

const currentImageIndex = ref(0)
const commentText = ref('')

const post: Post = {
  id: 1,
  title: '대청호 벚꽃길 다녀왔어요 🌸',
  category: '관광지',
  rating: 4.0,
  author: '벚꽃사랑곡',
  viewCount: 1204,
  createdAt: '2026.07.11',
  content: `조차는 오전 9시 전에 도착하셨야 여유 있게 산책할 수 있고, 산책로는 왕복 1시
간 정도... (본문)`,
  images: ['image1', 'image2', 'image3']
}

const comments: Comment[] = [
  {
    id: 1,
    author: '지나가던춘천인',
    content: '정보 감사해요!',
    createdAt: '인'
  }
]

const commentAuthor = ref('')
const commentPassword = ref('')
const isShareModalOpen = ref(false)
const isLiked = ref(false)
const likeCount = ref(0)

const handleBack = () => {
  console.log('뒤로가기')
}

const handleDelete = () => {
  console.log('삭제')
}

const handleShare = () => {
  isShareModalOpen.value = true
}

const handleShareOption = (option: string) => {
  if (option === 'copy') {
    const url = window.location.href
    navigator.clipboard.writeText(url)
    alert('링크가 복사되었습니다.')
  } else {
    console.log('공유:', option)
  }
  isShareModalOpen.value = false
}

const closeShareModal = () => {
  isShareModalOpen.value = false
}

const prevImage = () => {
  if (currentImageIndex.value > 0) {
    currentImageIndex.value--
  }
}

const nextImage = () => {
  if (currentImageIndex.value < post.images.length - 1) {
    currentImageIndex.value++
  }
}

const submitComment = () => {
  if (commentText.value.trim()) {
    console.log('댓글 작성:', commentText.value)
    commentText.value = ''
  }
}

const toggleLike = () => {
  if (isLiked.value) {
    likeCount.value--
  } else {
    likeCount.value++
  }
  isLiked.value = !isLiked.value
}

const renderStars = (rating: number) => {
  const fullStars = Math.floor(rating)
  const hasHalf = rating % 1 !== 0
  return { full: fullStars, half: hasHalf ? 1 : 0, empty: 5 - fullStars - (hasHalf ? 1 : 0) }
}
</script>

<template>
  <div class="board-detail-page">
    <div class="detail-header">
      <button class="back-btn" @click="handleBack">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 12H5M12 19l-7-7 7-7" />
        </svg>
      </button>
      <div class="header-right">
        <span class="author-badge">수정</span>
        <button class="delete-btn" @click="handleDelete">삭제</button>
      </div>
    </div>

    <div class="detail-content">
      <div class="content-wrapper">
        <div class="category-badge">{{ post.category }}</div>

        <div class="title-section">
          <h1 class="post-title">{{ post.title }}</h1>
        </div>

        <div class="rating-section">
          <div class="stars">
            <span v-for="_ in renderStars(post.rating).full" :key="`full`" class="star full">★</span>
            <span v-if="renderStars(post.rating).half" class="star half">★</span>
            <span v-for="_ in renderStars(post.rating).empty" :key="`empty`" class="star empty">★</span>
            <span class="rating-value">{{ post.rating.toFixed(1) }}</span>
          </div>
        </div>

        <div class="meta-info">
          <span class="author">{{ post.author }}</span>
          <span class="dot">·</span>
          <span class="view-count">조회 {{ post.viewCount }}</span>
          <span class="dot">·</span>
          <span class="date">{{ post.createdAt }}</span>
        </div>

        <div class="action-buttons">
          <button :class="['like-btn', { liked: isLiked }]" @click="toggleLike">
            <span class="heart">♥</span>
            <span v-if="likeCount > 0" class="like-count">{{ likeCount }}</span>
          </button>
          <button class="share-btn" @click="handleShare">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="18" cy="5" r="3"></circle>
              <circle cx="6" cy="12" r="3"></circle>
              <circle cx="18" cy="19" r="3"></circle>
              <path d="M8.59 13.51l6.83 3.98M15.41 6.51l-6.82 3.98"></path>
            </svg>
            <span>공유</span>
          </button>
        </div>

        <div class="image-carousel">
          <div class="carousel-container">
            <div class="carousel-image">
              <div class="image-placeholder">photo carousel ({{ currentImageIndex + 1 }}/{{ post.images.length }})</div>
            </div>
          </div>
          <div class="carousel-controls">
            <button class="carousel-btn prev-btn" @click="prevImage" :disabled="currentImageIndex === 0">
              ◀
            </button>
            <button class="carousel-btn next-btn" @click="nextImage" :disabled="currentImageIndex === post.images.length - 1">
              ▶
            </button>
          </div>
        </div>

        <div class="post-body">
          {{ post.content }}
        </div>

        <div class="comments-section">
          <div class="comments-header">
            <span class="comment-icon">💬</span>
            <span class="comment-count">댓글 {{ comments.length }}</span>
          </div>

          <div class="comments-list">
            <div v-for="comment in comments" :key="comment.id" class="comment-item">
              <div class="comment-author">{{ comment.author }}</div>
              <div v-if="comment.content" class="comment-content">{{ comment.content }}</div>
            </div>
          </div>

          <div class="comment-input-section">
            <div class="comment-inputs-row">
              <input
                v-model="commentAuthor"
                type="text"
                class="comment-author-input"
                placeholder="닉네임"
              />
              <input
                v-model="commentPassword"
                type="password"
                class="comment-password-input"
                placeholder="비밀번호 ••••"
              />
            </div>
            <textarea
              v-model="commentText"
              class="comment-input"
              placeholder="댓글을 입력하세요"
              rows="3"
            ></textarea>
            <button class="submit-comment-btn" @click="submitComment">댓글 남기기</button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="isShareModalOpen" class="share-modal-overlay" @click="closeShareModal">
      <div class="share-modal" @click.stop>
        <div class="share-modal-header">
          <h3>공유하기</h3>
          <button class="share-modal-close" @click="closeShareModal">✕</button>
        </div>
        <div class="share-options">
          <button class="share-option" @click="handleShareOption('instagram')">
            <span class="share-icon">📷</span>
            <span>인스타그램</span>
          </button>
          <button class="share-option" @click="handleShareOption('kakaotalk')">
            <span class="share-icon">💬</span>
            <span>카카오톡</span>
          </button>
          <button class="share-option" @click="handleShareOption('twitter')">
            <span class="share-icon">𝕏</span>
            <span>X</span>
          </button>
          <button class="share-option" @click="handleShareOption('copy')">
            <span class="share-icon">🔗</span>
            <span>링크 복사</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.board-detail-page {
  width: 100%;
  min-height: 100vh;
  background-color: #ffffff;
}

.detail-header {
  width: 100%;
  padding: 16px 20px;
  background-color: #ffffff;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.back-btn {
  width: 32px;
  height: 32px;
  min-width: 32px;
  border: none;
  background-color: transparent;
  color: #333;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s;
  padding: 0;
}

.back-btn:hover {
  color: #666;
}

.back-btn svg {
  width: 24px;
  height: 24px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.author-badge {
  padding: 6px 12px;
  border: 2px solid #333;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  color: #333;
  background-color: #ffffff;
}

.delete-btn {
  border: none;
  background-color: transparent;
  color: #999;
  font-size: 12px;
  cursor: pointer;
  padding: 0;
  transition: color 0.2s;
}

.delete-btn:hover {
  color: #333;
}

.detail-content {
  padding: 20px;
  background-color: #ffffff;
}

.content-wrapper {
  max-width: 800px;
  margin: 0 auto;
}

.category-badge {
  display: inline-block;
  padding: 6px 12px;
  border: 2px solid #333;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  color: #333;
  background-color: #ffffff;
  margin-bottom: 12px;
}

.title-section {
  margin-bottom: 16px;
}

.post-title {
  font-size: 24px;
  font-weight: 700;
  color: #333;
  margin: 0;
  line-height: 1.4;
}

.rating-section {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.action-buttons {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  margin-bottom: 20px;
}

.stars {
  display: inline-flex;
  align-items: center;
  gap: 3px;
}

.star {
  font-size: 18px;
  line-height: 1;
}

.star.full {
  color: #ffc107;
}

.star.half {
  color: #ffc107;
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
  margin-left: 4px;
}

.like-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border: 2px solid #e5e7eb;
  border-radius: 20px;
  background-color: #ffffff;
  color: #999;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.like-btn:hover {
  border-color: #e74c3c;
  color: #e74c3c;
}

.like-btn.liked {
  border-color: #e74c3c;
  color: #e74c3c;
  background-color: #fff5f3;
}

.heart {
  font-size: 14px;
}

.like-count {
  font-size: 11px;
  font-weight: 600;
}

.share-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border: 2px solid #e5e7eb;
  border-radius: 20px;
  background-color: #ffffff;
  color: #333;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.share-btn:hover {
  border-color: #333;
}

.share-btn svg {
  width: 16px;
  height: 16px;
}

.meta-info {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #999;
  margin-bottom: 12px;
}

.dot {
  color: #ddd;
}

.image-carousel {
  position: relative;
  margin-bottom: 20px;
}

.carousel-container {
  width: 100%;
  aspect-ratio: 16 / 9;
  background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%);
  border-radius: 12px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.carousel-image {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: fadeInImage 0.3s ease-in-out;
}

@keyframes fadeInImage {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.image-placeholder {
  color: #ccc;
  font-size: 14px;
  font-weight: 500;
}

.carousel-controls {
  position: absolute;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  pointer-events: none;
  top: 0;
}

.carousel-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1px solid #e5e7eb;
  background-color: rgba(255, 255, 255, 0.9);
  color: #333;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  pointer-events: auto;
}

.carousel-btn:hover:not(:disabled) {
  background-color: #ffffff;
  border-color: #333;
}

.carousel-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.post-body {
  font-size: 14px;
  line-height: 1.6;
  color: #333;
  margin-bottom: 24px;
  padding: 16px;
  background-color: #fafafa;
  border-radius: 8px;
}

.comments-section {
  border-top: 1px solid #f0f0f0;
  padding-top: 24px;
}

.comments-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.comment-icon {
  font-size: 16px;
}

.comment-count {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.comments-list {
  margin-bottom: 20px;
}

.comment-item {
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.comment-author {
  font-size: 13px;
  font-weight: 600;
  color: #333;
  margin-bottom: 6px;
}

.comment-content {
  font-size: 13px;
  color: #666;
  line-height: 1.5;
}

.comment-input-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.comment-inputs-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.comment-author-input,
.comment-password-input {
  padding: 12px 14px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-family: inherit;
  font-size: 13px;
  color: #333;
  transition: border-color 0.2s;
}

.comment-author-input:focus,
.comment-password-input:focus {
  outline: none;
  border-color: #333;
}

.comment-author-input::placeholder,
.comment-password-input::placeholder {
  color: #999;
}

.comment-input {
  padding: 12px 14px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-family: inherit;
  font-size: 13px;
  color: #333;
  resize: vertical;
  transition: border-color 0.2s;
}

.comment-input:focus {
  outline: none;
  border-color: #333;
}

.comment-input::placeholder {
  color: #999;
}

.submit-comment-btn {
  align-self: flex-end;
  padding: 8px 16px;
  background-color: #333;
  color: #ffffff;
  border: none;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.submit-comment-btn:hover {
  background-color: #555;
}

@media (max-width: 768px) {
  .detail-header {
    padding: 14px 16px;
  }

  .detail-content {
    padding: 16px;
  }

  .post-title {
    font-size: 20px;
  }

  .rating-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}

@media (max-width: 640px) {
  .detail-header {
    padding: 12px 16px;
  }

  .detail-content {
    padding: 16px 12px;
  }

  .post-title {
    font-size: 18px;
  }

  .carousel-btn {
    width: 32px;
    height: 32px;
    font-size: 12px;
  }

  .comment-author-input,
  .comment-password-input,
  .comment-input {
    font-size: 13px;
    padding: 10px 12px;
  }
}

.share-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: flex-end;
  z-index: 100;
}

.share-modal {
  width: 100%;
  background-color: #ffffff;
  border-radius: 12px 12px 0 0;
  padding: 20px;
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    transform: translateY(100%);
  }
  to {
    transform: translateY(0);
  }
}

.share-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.share-modal-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.share-modal-close {
  background-color: transparent;
  border: none;
  font-size: 20px;
  color: #999;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.share-modal-close:hover {
  color: #333;
}

.share-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.share-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 16px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  background-color: #ffffff;
  cursor: pointer;
  transition: all 0.2s;
}

.share-option:hover {
  border-color: #333;
  background-color: #f9f9f9;
}

.share-icon {
  font-size: 24px;
}

.share-option span:last-child {
  font-size: 13px;
  font-weight: 500;
  color: #333;
}
</style>
