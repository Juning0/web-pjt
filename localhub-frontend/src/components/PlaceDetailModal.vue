<script setup>
import { computed, onUnmounted, ref, watch } from 'vue'
import { randomNickname } from '@/utils/nickname'
import { eventDateLabel } from '@/utils/date'
import { getLocation } from '@/api/locations'
import { createPost, getPost, listPosts } from '@/api/posts'
import PostContent from '@/components/PostContent.vue'

const props = defineProps({
  place: {
    type: Object,
    default: null,
  },
  open: {
    type: Boolean,
    default: false,
  },
  loading: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['close', 'select-location'])

// 이 장소에 대한 "리뷰"는 별도 API가 없고, location_id를 채운 게시글(Post)이 곧 리뷰다.
// 리뷰 등록 후에는 장소 상세를 다시 조회해 서버가 계산한 avg_rating/review_count를 반영한다.
const location = ref(null)

const isReviewFormOpen = ref(false)
const reviewTitle = ref('')
const reviewContent = ref('')
const reviewPassword = ref('')
const reviewRating = ref(5)
const isSubmitting = ref(false)
const submitError = ref('')
const submitSuccess = ref(false)
const reviewNickname = ref(randomNickname())

// 이 장소에 달린 리뷰(=location_id로 연결된 게시글) 최신순 미리보기 목록.
const reviews = ref([])
const isReviewsLoading = ref(false)

// null이면 장소 상세 화면, 값이 있으면 그 리뷰로 "드릴다운"한 화면 — 같은 모달 안에서 화면만 전환한다.
const selectedReview = ref(null)
const isReviewDetailLoading = ref(false)

const hasCoords = computed(() => Boolean(location.value?.lat && location.value?.lng))
const eventPeriod = computed(() => eventDateLabel(location.value))

const ratingLabel = computed(() => {
  if (!location.value || location.value.avg_rating == null) return '아직 등록된 리뷰가 없어요'
  return `${location.value.avg_rating.toFixed(1)} · 리뷰 ${location.value.review_count || 0}건`
})

const starDisplay = computed(() => {
  const rating = location.value?.avg_rating
  const filled = rating ? Math.round(rating) : 0
  return '★★★★★'.slice(0, filled).padEnd(5, '☆')
})

function resetReviewForm() {
  isReviewFormOpen.value = false
  reviewTitle.value = ''
  reviewContent.value = ''
  reviewPassword.value = ''
  reviewRating.value = 5
  isSubmitting.value = false
  submitError.value = ''
  submitSuccess.value = false
  reviewNickname.value = randomNickname()
}

function reviewStars(rating) {
  return '★★★★★'.slice(0, rating || 0).padEnd(5, '☆')
}

function formatReviewDate(value) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  return `${date.getFullYear()}.${String(date.getMonth() + 1).padStart(2, '0')}.${String(date.getDate()).padStart(2, '0')}`
}

async function fetchReviews(contentId) {
  isReviewsLoading.value = true
  try {
    const response = await listPosts({ locationId: contentId, sort: 'latest', size: 5 })
    reviews.value = response.items
  } catch {
    reviews.value = []
  } finally {
    isReviewsLoading.value = false
  }
}

async function openReview(item) {
  isReviewDetailLoading.value = true
  selectedReview.value = { id: item.id } // truthy placeholder: 헤더가 즉시 "뒤로가기" 화면으로 전환되게
  try {
    selectedReview.value = await getPost(item.id)
  } catch {
    selectedReview.value = null
  } finally {
    isReviewDetailLoading.value = false
  }
}

function backToPlace() {
  selectedReview.value = null
}

async function handleReviewDeleted(postId) {
  reviews.value = reviews.value.filter((review) => review.id !== postId)
  backToPlace()
  if (location.value) location.value = await getLocation(location.value.content_id)
}

watch(
  () => [props.open, props.place],
  ([isOpen, place]) => {
    if (isOpen && place) {
      resetReviewForm()
      backToPlace()
      location.value = { ...place }
      fetchReviews(place.content_id)
    }
  },
  { immediate: true },
)

function handleClose() {
  emit('close')
}

function handleKeydown(event) {
  if (event.key === 'Escape') handleClose()
}

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      window.addEventListener('keydown', handleKeydown)
    } else {
      window.removeEventListener('keydown', handleKeydown)
    }
  },
)

onUnmounted(() => window.removeEventListener('keydown', handleKeydown))

function handleViewOnMap() {
  if (!location.value) return
  emit('select-location', {
    type: 'location',
    id: location.value.content_id,
    title: location.value.title,
    lat: location.value.lat,
    lng: location.value.lng,
    address: location.value.addr1,
  })
}

async function submitReview() {
  if (!location.value || isSubmitting.value) return
  if (!reviewTitle.value.trim() || !reviewContent.value.trim() || !reviewPassword.value.trim()) {
    submitError.value = '제목, 내용, 비밀번호를 모두 입력해 주세요.'
    return
  }

  isSubmitting.value = true
  submitError.value = ''

  try {
    // 이 장소의 리뷰는 별도 API가 없고, location_id를 채운 게시글이 곧 리뷰다.
    await createPost({
      category: location.value.category,
      title: reviewTitle.value.trim(),
      content: `[${reviewNickname.value.trim()}] ${reviewContent.value.trim()}`,
      password: reviewPassword.value.trim(),
      rating: reviewRating.value,
      location_id: location.value.content_id,
    })

    // avg_rating/review_count는 서버가 계산하므로 등록 후 상세를 다시 조회한다.
    location.value = await getLocation(location.value.content_id)
    fetchReviews(location.value.content_id)

    submitSuccess.value = true
    isReviewFormOpen.value = false
    reviewTitle.value = ''
    reviewContent.value = ''
    reviewPassword.value = ''
    reviewRating.value = 5
    reviewNickname.value = randomNickname()
  } catch (error) {
    submitError.value = error.message || '리뷰 등록에 실패했어요.'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="open" class="modal-backdrop" @click.self="handleClose">
        <section
          class="place-modal"
          role="dialog"
          aria-modal="true"
          :aria-label="location?.title || '장소 상세'"
        >
          <header class="modal-header">
            <button
              v-if="selectedReview"
              class="icon-button"
              type="button"
              aria-label="장소로 돌아가기"
              @click="backToPlace"
            >
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="m15 5-7 7 7 7" />
              </svg>
            </button>
            <span v-else class="icon-button-spacer" aria-hidden="true"></span>
            <button class="icon-button" type="button" aria-label="닫기" @click="handleClose">
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="m6 6 12 12M18 6 6 18" />
              </svg>
            </button>
          </header>

          <div class="modal-body">
            <template v-if="selectedReview">
              <PostContent
                :post="selectedReview"
                :loading="isReviewDetailLoading"
                @deleted="handleReviewDeleted"
                @select-location="(payload) => emit('select-location', payload)"
              />
            </template>
            <p v-else-if="loading" class="loading-text">불러오는 중...</p>
            <template v-else-if="location">
              <span class="category-pill">{{ location.category }}</span>
              <h2 class="place-title">{{ location.title }}</h2>

              <div class="rating-row">
                <span class="stars">{{ starDisplay }}</span>
                <span class="rating-label">{{ ratingLabel }}</span>
              </div>

              <div class="photo-frame">
                <img
                  v-if="location.first_image"
                  :src="location.first_image"
                  :alt="`${location.title} 사진`"
                  loading="lazy"
                />
                <div v-else class="photo-placeholder" aria-hidden="true">
                  <svg viewBox="0 0 24 24">
                    <path
                      d="M4 18V6a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v12H4Zm0-3 4-4 3 3 2-2 5 5M15.5 9a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3Z"
                    />
                  </svg>
                  <p>이미지가 제공되지 않는 장소입니다.</p>
                </div>
              </div>

              <dl class="info-list">
                <div v-if="eventPeriod" class="info-row">
                  <dt>기간</dt>
                  <dd>{{ eventPeriod }}</dd>
                </div>
                <div class="info-row">
                  <dt>주소</dt>
                  <dd>{{ location.addr1 || '주소 정보 없음' }}</dd>
                </div>
                <div v-if="location.tel" class="info-row">
                  <dt>전화</dt>
                  <dd>{{ location.tel }}</dd>
                </div>
              </dl>

              <button
                v-if="hasCoords"
                class="map-button"
                type="button"
                @click="handleViewOnMap"
              >
                지도에서 보기
              </button>

              <div class="reviews-list-section">
                <h3 class="reviews-heading">리뷰 {{ location.review_count || 0 }}건</h3>
                <p v-if="isReviewsLoading" class="reviews-empty">리뷰를 불러오는 중...</p>
                <ul v-else-if="reviews.length" class="reviews-list">
                  <li
                    v-for="review in reviews"
                    :key="review.id"
                    class="review-item"
                    @click="openReview(review)"
                  >
                    <div class="review-item-top">
                      <span class="review-stars">{{ reviewStars(review.rating) }}</span>
                      <span class="review-date">{{ formatReviewDate(review.created_at) }}</span>
                    </div>
                    <p class="review-item-title">{{ review.title }}</p>
                  </li>
                </ul>
                <p v-else class="reviews-empty">아직 등록된 리뷰가 없어요.</p>
              </div>

              <div class="review-section">
                <button
                  class="review-toggle"
                  type="button"
                  @click="isReviewFormOpen = !isReviewFormOpen"
                >
                  {{ isReviewFormOpen ? '리뷰 작성 취소' : '리뷰 작성하기' }}
                </button>

                <form v-if="isReviewFormOpen" class="review-form" @submit.prevent="submitReview">
                  <div class="rating-picker" role="radiogroup" aria-label="별점 선택">
                    <button
                      v-for="value in 5"
                      :key="value"
                      type="button"
                      :class="['star-button', { filled: value <= reviewRating }]"
                      :aria-pressed="value <= reviewRating"
                      :aria-label="`${value}점`"
                      @click="reviewRating = value"
                    >★</button>
                  </div>

                  <input
                    v-model="reviewTitle"
                    class="text-input"
                    maxlength="200"
                    placeholder="한 줄 제목"
                    required
                  />
                  <textarea
                    v-model="reviewContent"
                    class="text-area"
                    placeholder="다녀온 경험을 남겨주세요"
                    required
                  ></textarea>
                  <input
                    v-model="reviewPassword"
                    class="text-input"
                    type="password"
                    placeholder="비밀번호 (수정·삭제 시 필요)"
                    required
                  />

                  <div class="nickname-row">
                    <input
                      v-model="reviewNickname"
                      class="text-input nickname-input"
                      maxlength="20"
                      placeholder="닉네임"
                      required
                    />
                    <button
                      class="nickname-suggest"
                      type="button"
                      title="닉네임 추천 받기"
                      @click="reviewNickname = randomNickname()"
                    >
                      추천
                    </button>
                  </div>

                  <button class="submit-button" type="submit" :disabled="isSubmitting">
                    {{ isSubmitting ? '등록 중...' : '리뷰 등록' }}
                  </button>

                  <p v-if="submitError" class="form-error">{{ submitError }}</p>
                </form>

                <p v-if="submitSuccess" class="submit-success">리뷰가 등록되었어요!</p>
              </div>
            </template>
          </div>
        </section>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.modal-backdrop,
.place-modal,
.place-modal * {
  box-sizing: border-box;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 1200;
  display: grid;
  padding: 24px;
  background: rgb(28 26 33 / 46%);
  place-items: center;
}

.place-modal {
  --ink: #28262f;
  --muted: #716e78;
  --line: #dedce3;
  --soft: #f7f6f8;
  --purple: #7e66e2;
  --purple-soft: #f1edff;
  --star: #e9a900;
  display: flex;
  width: min(480px, 100%);
  max-height: min(760px, calc(100dvh - 48px));
  overflow: hidden;
  color: var(--ink);
  font-family: Pretendard, Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 30px 70px rgb(24 20 32 / 30%);
  flex-direction: column;
}

.modal-header {
  display: flex;
  min-height: 52px;
  padding: 8px 10px;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--line);
}

.icon-button {
  display: grid;
  width: 34px;
  height: 34px;
  padding: 0;
  color: var(--ink);
  background: transparent;
  border: 0;
  border-radius: 8px;
  cursor: pointer;
  place-items: center;
}

.icon-button-spacer {
  width: 34px;
  height: 34px;
}

.icon-button:hover {
  background: var(--soft);
}

.icon-button svg {
  width: 20px;
  height: 20px;
  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 2;
}

.modal-body {
  padding: 18px 20px 24px;
  overflow-y: auto;
}

.loading-text {
  padding: 40px 0;
  color: var(--muted);
  font-size: 12.5px;
  text-align: center;
}

.category-pill {
  display: inline-block;
  padding: 5px 11px;
  color: var(--purple);
  font-size: 11px;
  font-weight: 750;
  background: var(--purple-soft);
  border-radius: 999px;
}

.place-title {
  margin: 12px 0 0;
  font-size: 21px;
  font-weight: 800;
  letter-spacing: -0.02em;
}

.rating-row {
  display: flex;
  margin-top: 8px;
  gap: 8px;
  align-items: center;
}

.stars {
  color: var(--star);
  font-size: 15px;
  letter-spacing: 1px;
}

.rating-label {
  color: var(--muted);
  font-size: 12px;
  font-weight: 650;
}

.photo-frame {
  width: 100%;
  height: 220px;
  margin-top: 16px;
  overflow: hidden;
  background: var(--soft);
  border-radius: 12px;
}

.photo-frame img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.photo-placeholder {
  display: flex;
  width: 100%;
  height: 100%;
  gap: 8px;
  color: #aaa6b0;
  align-items: center;
  flex-direction: column;
  justify-content: center;
}

.photo-placeholder svg {
  width: 34px;
  height: 34px;
  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 1.5;
}

.photo-placeholder p {
  margin: 0;
  color: #98949e;
  font-size: 12px;
  font-weight: 600;
}

.info-list {
  margin: 16px 0 0;
  padding: 0;
}

.info-row {
  display: flex;
  margin-top: 6px;
  gap: 10px;
  font-size: 12.5px;
}

.info-row dt {
  flex: 0 0 34px;
  color: var(--muted);
  font-weight: 650;
}

.info-row dd {
  margin: 0;
  color: var(--ink);
}

.map-button {
  width: 100%;
  min-height: 42px;
  margin-top: 16px;
  color: var(--ink);
  font: inherit;
  font-size: 12.5px;
  font-weight: 700;
  background: #fff;
  border: 1px solid #cbc8d1;
  border-radius: 9px;
  cursor: pointer;
}

.map-button:hover {
  border-color: #9a95a2;
}

.reviews-list-section {
  padding-top: 18px;
  margin-top: 18px;
  border-top: 1px solid var(--line);
}

.reviews-heading {
  margin: 0 0 10px;
  color: var(--ink);
  font-size: 13px;
  font-weight: 750;
}

.reviews-empty {
  margin: 0;
  padding: 10px 0;
  color: var(--muted);
  font-size: 12px;
}

.reviews-list {
  display: flex;
  padding: 0;
  margin: 0;
  gap: 4px;
  list-style: none;
  flex-direction: column;
}

.review-item {
  padding: 10px 8px;
  cursor: pointer;
  border-radius: 8px;
  transition: background-color 160ms ease;
}

.review-item:hover {
  background: var(--soft);
}

.review-item-top {
  display: flex;
  gap: 8px;
  align-items: center;
  justify-content: space-between;
}

.review-stars {
  color: var(--star);
  font-size: 12px;
  letter-spacing: 1px;
}

.review-date {
  color: var(--muted);
  font-size: 10.5px;
}

.review-item-title {
  margin: 4px 0 0;
  overflow: hidden;
  color: var(--ink);
  font-size: 12.5px;
  font-weight: 650;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.review-section {
  padding-top: 18px;
  margin-top: 18px;
  border-top: 1px solid var(--line);
}

.review-toggle {
  width: 100%;
  min-height: 42px;
  color: #fff;
  font: inherit;
  font-size: 12.5px;
  font-weight: 750;
  background: var(--ink);
  border: 0;
  border-radius: 9px;
  cursor: pointer;
}

.review-form {
  display: flex;
  margin-top: 14px;
  gap: 9px;
  flex-direction: column;
}

.rating-picker {
  display: flex;
  gap: 4px;
}

.star-button {
  width: 30px;
  height: 30px;
  padding: 0;
  color: #d8d5db;
  font-size: 20px;
  background: transparent;
  border: 0;
  cursor: pointer;
}

.star-button.filled {
  color: var(--star);
}

.text-input,
.text-area {
  width: 100%;
  padding: 10px 11px;
  color: var(--ink);
  font: inherit;
  font-size: 12.5px;
  background: #fff;
  border: 1px solid #cbc8d0;
  border-radius: 9px;
}

.text-area {
  min-height: 84px;
  resize: vertical;
}

.nickname-row {
  display: flex;
  gap: 8px;
}

.nickname-input {
  flex: 1;
}

.nickname-suggest {
  padding: 0 14px;
  color: var(--purple);
  font: inherit;
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
  background: var(--purple-soft);
  border: 1px solid transparent;
  border-radius: 9px;
  cursor: pointer;
}

.nickname-suggest:hover {
  border-color: var(--purple);
}

.submit-button {
  min-height: 42px;
  color: #fff;
  font: inherit;
  font-size: 12.5px;
  font-weight: 750;
  background: var(--purple);
  border: 0;
  border-radius: 9px;
  cursor: pointer;
}

.submit-button:disabled {
  background: #c8bdf0;
  cursor: not-allowed;
}

.form-error {
  margin: 0;
  color: #9b2f2f;
  font-size: 11.5px;
}

.submit-success {
  margin: 14px 0 0;
  color: #2f8f5b;
  font-size: 12px;
  font-weight: 650;
}

.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 160ms ease;
}

.modal-fade-enter-active .place-modal,
.modal-fade-leave-active .place-modal {
  transition: transform 180ms ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-from .place-modal,
.modal-fade-leave-to .place-modal {
  transform: translateY(10px) scale(0.98);
}

@media (prefers-reduced-motion: reduce) {
  .modal-fade-enter-active,
  .modal-fade-leave-active,
  .modal-fade-enter-active .place-modal,
  .modal-fade-leave-active .place-modal {
    transition: none;
  }
}
</style>
