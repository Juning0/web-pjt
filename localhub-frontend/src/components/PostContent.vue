<script setup>
import { computed, ref, watch } from 'vue'
import { parseAuthoredContent, randomNickname } from '@/utils/nickname'
import { createComment, deleteComment, deletePost, updatePost } from '@/api/posts'
import { getLocation } from '@/api/locations'

const props = defineProps({
  post: {
    type: Object,
    default: null,
  },
  loading: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['deleted', 'select-location'])

// 좋아요는 백엔드에 없는 필드라 이 컴포넌트 안에서만 관리한다(post.like_count/is_liked).
// 나머지(본문·댓글·수정·삭제)는 실제 API를 호출한다.
const post = ref(null)

// location_id가 있는 게시글은 특정 장소에 대한 리뷰다. 목록 응답엔 장소 정보가 없어 따로 조회한다.
const reviewedPlace = ref(null)
const isPlaceLoading = ref(false)

const isDeleteConfirmOpen = ref(false)
const deletePassword = ref('')
const deleteError = ref('')

const commentContent = ref('')
const commentPassword = ref('')
const commentNickname = ref(randomNickname())
const isSubmittingComment = ref(false)
const commentFormError = ref('')

const activeCommentDeleteId = ref(null)
const commentDeletePassword = ref('')
const commentDeleteError = ref('')
const isDeletingComment = ref(false)

const isEditFormOpen = ref(false)
const editTitle = ref('')
const editContent = ref('')
const editRating = ref(0)
const editPassword = ref('')
const editFormError = ref('')
const isSavingEdit = ref(false)
const isDeletingPost = ref(false)

function resetInteractionState() {
  isDeleteConfirmOpen.value = false
  deletePassword.value = ''
  deleteError.value = ''
  isDeletingPost.value = false
  commentContent.value = ''
  commentPassword.value = ''
  commentNickname.value = randomNickname()
  isSubmittingComment.value = false
  commentFormError.value = ''
  activeCommentDeleteId.value = null
  commentDeletePassword.value = ''
  commentDeleteError.value = ''
  isDeletingComment.value = false
  isEditFormOpen.value = false
  editTitle.value = ''
  editContent.value = ''
  editRating.value = 0
  editPassword.value = ''
  editFormError.value = ''
  isSavingEdit.value = false
}

async function fetchReviewedPlace(locationId) {
  if (!locationId) {
    reviewedPlace.value = null
    return
  }
  isPlaceLoading.value = true
  try {
    reviewedPlace.value = await getLocation(locationId)
  } catch {
    reviewedPlace.value = null
  } finally {
    isPlaceLoading.value = false
  }
}

watch(
  () => props.post,
  (nextPost) => {
    if (!nextPost) return
    resetInteractionState()
    // 부모가 들고 있는 같은 객체를 그대로 참조해서, 댓글·좋아요 변경이 다시 열어도 유지되게 한다.
    post.value = nextPost
    fetchReviewedPlace(nextPost.location_id)
  },
  { immediate: true },
)

function handleViewPlaceOnMap() {
  if (!reviewedPlace.value) return
  emit('select-location', {
    type: 'location',
    id: reviewedPlace.value.content_id,
    title: reviewedPlace.value.title,
    lat: reviewedPlace.value.lat,
    lng: reviewedPlace.value.lng,
    address: reviewedPlace.value.addr1,
  })
}

function toggleLike() {
  if (!post.value) return
  if (post.value.is_liked) {
    post.value.like_count = Math.max(0, (post.value.like_count || 0) - 1)
    post.value.is_liked = false
  } else {
    post.value.like_count = (post.value.like_count || 0) + 1
    post.value.is_liked = true
  }
}

const authorContent = computed(() => parseAuthoredContent(post.value?.content))

const ratingLabel = computed(() => {
  if (!post.value || post.value.rating == null) return '평점 없음'
  return `${post.value.rating.toFixed(1)}`
})

const starDisplay = computed(() => {
  const rating = post.value?.rating || 0
  return '★★★★★'.slice(0, rating).padEnd(5, '☆')
})

const metaLabel = computed(() => {
  if (!post.value) return ''
  const date = new Date(post.value.created_at)
  const formatted = Number.isNaN(date.getTime())
    ? post.value.created_at
    : `${date.getFullYear()}.${String(date.getMonth() + 1).padStart(2, '0')}.${String(date.getDate()).padStart(2, '0')}`
  return `조회 ${(post.value.view_count || 0).toLocaleString()} · ${formatted}`
})

function formatRelativeTime(value) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  const diffMs = Date.now() - date.getTime()
  const minutes = Math.floor(diffMs / 60000)
  if (minutes < 1) return '방금 전'
  if (minutes < 60) return `${minutes}분 전`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}시간 전`
  const days = Math.floor(hours / 24)
  return `${days}일 전`
}

function openEditForm() {
  isDeleteConfirmOpen.value = false
  editTitle.value = post.value.title
  editContent.value = authorContent.value.body
  editRating.value = post.value.rating || 0
  editPassword.value = ''
  editFormError.value = ''
  isEditFormOpen.value = true
}

function cancelEditForm() {
  isEditFormOpen.value = false
  editTitle.value = ''
  editContent.value = ''
  editRating.value = 0
  editPassword.value = ''
  editFormError.value = ''
}

async function saveEdit() {
  if (!editTitle.value.trim() || !editContent.value.trim()) {
    editFormError.value = '제목과 내용을 입력해 주세요.'
    return
  }
  if (!editPassword.value.trim()) {
    editFormError.value = '비밀번호를 입력해 주세요.'
    return
  }
  if (isSavingEdit.value) return

  isSavingEdit.value = true
  editFormError.value = ''
  try {
    const updated = await updatePost(post.value.id, {
      password: editPassword.value.trim(),
      title: editTitle.value.trim(),
      content: `[${authorContent.value.nickname}] ${editContent.value.trim()}`,
      rating: editRating.value || null,
    })
    // like_count/is_liked는 서버 응답에 없는 클라이언트 전용 필드라 그대로 유지된다.
    Object.assign(post.value, updated)
    cancelEditForm()
  } catch (error) {
    editFormError.value = error.message || '수정에 실패했어요.'
  } finally {
    isSavingEdit.value = false
  }
}

function openDeleteConfirm() {
  isEditFormOpen.value = false
  isDeleteConfirmOpen.value = true
}

function cancelDeleteConfirm() {
  isDeleteConfirmOpen.value = false
  deletePassword.value = ''
  deleteError.value = ''
}

async function confirmDelete() {
  if (!deletePassword.value.trim()) {
    deleteError.value = '비밀번호를 입력해 주세요.'
    return
  }
  if (isDeletingPost.value) return

  isDeletingPost.value = true
  deleteError.value = ''
  try {
    await deletePost(post.value.id, deletePassword.value.trim())
    emit('deleted', post.value.id)
  } catch (error) {
    deleteError.value = error.message || '삭제에 실패했어요.'
  } finally {
    isDeletingPost.value = false
  }
}

function openCommentDeleteConfirm(commentId) {
  activeCommentDeleteId.value = commentId
  commentDeletePassword.value = ''
  commentDeleteError.value = ''
}

function cancelCommentDelete() {
  activeCommentDeleteId.value = null
  commentDeletePassword.value = ''
  commentDeleteError.value = ''
}

async function confirmCommentDelete(commentId) {
  if (!commentDeletePassword.value.trim()) {
    commentDeleteError.value = '비밀번호를 입력해 주세요.'
    return
  }
  if (isDeletingComment.value) return

  isDeletingComment.value = true
  commentDeleteError.value = ''
  try {
    await deleteComment(commentId, commentDeletePassword.value.trim())
    post.value.comments = post.value.comments.filter((comment) => comment.id !== commentId)
    cancelCommentDelete()
  } catch (error) {
    commentDeleteError.value = error.message || '삭제에 실패했어요.'
  } finally {
    isDeletingComment.value = false
  }
}

async function submitComment() {
  if (!post.value || isSubmittingComment.value) return
  if (!commentContent.value.trim() || !commentPassword.value.trim() || !commentNickname.value.trim()) return

  isSubmittingComment.value = true
  commentFormError.value = ''
  try {
    const created = await createComment(post.value.id, {
      content: `[${commentNickname.value.trim()}] ${commentContent.value.trim()}`,
      password: commentPassword.value.trim(),
    })
    post.value.comments.push(created)
    commentContent.value = ''
    commentPassword.value = ''
    commentNickname.value = randomNickname()
  } catch (error) {
    commentFormError.value = error.message || '댓글 등록에 실패했어요.'
  } finally {
    isSubmittingComment.value = false
  }
}
</script>

<template>
  <p v-if="loading" class="loading-text">불러오는 중...</p>
  <template v-else-if="post">
    <template v-if="!isEditFormOpen">
      <div class="content-topbar">
        <span class="category-pill">{{ post.category }}</span>
        <div class="header-actions">
          <button class="text-action" type="button" @click="openEditForm">수정</button>
          <span class="header-divider" aria-hidden="true"></span>
          <button class="text-action danger" type="button" @click="openDeleteConfirm">삭제</button>
        </div>
      </div>
      <h2 class="post-title">{{ post.title }}</h2>

      <div class="rating-row">
        <span class="stars">{{ starDisplay }}</span>
        <span class="rating-label">{{ ratingLabel }}</span>
      </div>

      <p class="meta-line">{{ metaLabel }}</p>

      <p v-if="post.location_id && isPlaceLoading" class="place-chip-loading">
        장소 정보를 불러오는 중...
      </p>
      <button
        v-else-if="reviewedPlace"
        type="button"
        class="place-chip"
        @click="handleViewPlaceOnMap"
      >
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M12 21s-7-6.2-7-11a7 7 0 0 1 14 0c0 4.8-7 11-7 11Z" />
          <circle cx="12" cy="10" r="2.5" />
        </svg>
        <span class="place-chip-text">
          <span class="place-chip-label">이 장소에 대한 리뷰예요</span>
          <span class="place-chip-title">{{ reviewedPlace.title }}</span>
        </span>
        <span class="place-chip-action">지도에서 보기 →</span>
      </button>

      <button
        type="button"
        class="like-button"
        :class="{ liked: post.is_liked }"
        :aria-pressed="post.is_liked"
        @click="toggleLike"
      >
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path
            d="M12 20.5s-7.5-4.6-10-9.3C.5 8 2 4.5 5.5 4c2-.3 3.8.6 5 2.3C11.7 4.6 13.5 3.7 15.5 4c3.5.5 5 4 3.5 7.2-2.5 4.7-10 9.3-10 9.3Z"
          />
        </svg>
        좋아요 {{ post.like_count || 0 }}
      </button>

      <p class="author-line">
        <span class="author-badge">{{ authorContent.nickname }}</span>
      </p>
      <p class="post-content">{{ authorContent.body }}</p>

      <div v-if="isDeleteConfirmOpen" class="delete-confirm">
        <p>정말 삭제할까요? 비밀번호를 입력해 주세요.</p>
        <input
          v-model="deletePassword"
          type="password"
          class="text-input"
          placeholder="비밀번호"
        />
        <div class="delete-confirm-actions">
          <button type="button" class="ghost-button" @click="cancelDeleteConfirm">취소</button>
          <button
            type="button"
            class="danger-button"
            :disabled="isDeletingPost"
            @click="confirmDelete"
          >
            {{ isDeletingPost ? '삭제 중...' : '삭제' }}
          </button>
        </div>
        <p v-if="deleteError" class="form-error">{{ deleteError }}</p>
      </div>
    </template>

    <div v-else class="edit-form">
      <span class="category-pill">{{ post.category }}</span>

      <div class="rating-picker" role="radiogroup" aria-label="별점 선택">
        <button
          v-for="value in 5"
          :key="value"
          type="button"
          :class="['star-button', { filled: value <= editRating }]"
          :aria-pressed="value <= editRating"
          :aria-label="`${value}점`"
          @click="editRating = value"
        >★</button>
      </div>

      <input
        v-model="editTitle"
        class="text-input"
        maxlength="200"
        placeholder="제목"
      />
      <textarea
        v-model="editContent"
        class="text-area"
        placeholder="내용을 입력하세요..."
      ></textarea>
      <input
        v-model="editPassword"
        type="password"
        class="text-input"
        placeholder="비밀번호"
      />

      <p v-if="editFormError" class="form-error">{{ editFormError }}</p>

      <div class="edit-form-actions">
        <button type="button" class="ghost-button" @click="cancelEditForm">취소</button>
        <button
          type="button"
          class="submit-button"
          :disabled="isSavingEdit"
          @click="saveEdit"
        >
          {{ isSavingEdit ? '저장 중...' : '저장' }}
        </button>
      </div>
    </div>

    <div v-if="!isEditFormOpen" class="comment-section">
      <h3 class="comment-heading">댓글 {{ post.comments.length }}</h3>

      <ul v-if="post.comments.length" class="comment-list">
        <li v-for="comment in post.comments" :key="comment.id" class="comment-item">
          <div class="comment-topline">
            <span class="comment-nickname">
              {{ parseAuthoredContent(comment.content).nickname }}
            </span>
            <span class="comment-topline-right">
              <span class="comment-time">{{ formatRelativeTime(comment.created_at) }}</span>
              <button
                type="button"
                class="comment-delete"
                @click="openCommentDeleteConfirm(comment.id)"
              >
                삭제
              </button>
            </span>
          </div>
          <p class="comment-body">{{ parseAuthoredContent(comment.content).body }}</p>

          <div v-if="activeCommentDeleteId === comment.id" class="comment-delete-confirm">
            <input
              v-model="commentDeletePassword"
              type="password"
              class="text-input"
              placeholder="비밀번호"
            />
            <div class="comment-delete-actions">
              <button type="button" class="ghost-button-sm" @click="cancelCommentDelete">
                취소
              </button>
              <button
                type="button"
                class="danger-button-sm"
                :disabled="isDeletingComment"
                @click="confirmCommentDelete(comment.id)"
              >
                {{ isDeletingComment ? '삭제 중...' : '삭제' }}
              </button>
            </div>
            <p v-if="commentDeleteError" class="form-error">{{ commentDeleteError }}</p>
          </div>
        </li>
      </ul>
      <p v-else class="comment-empty">아직 댓글이 없어요.</p>

      <form class="comment-form" @submit.prevent="submitComment">
        <textarea
          v-model="commentContent"
          class="text-area"
          placeholder="댓글을 남겨보세요"
          required
        ></textarea>
        <div class="comment-form-row">
          <input
            v-model="commentNickname"
            class="text-input nickname-input"
            maxlength="20"
            placeholder="닉네임"
            required
          />
          <button
            type="button"
            class="nickname-suggest"
            title="닉네임 추천 받기"
            @click="commentNickname = randomNickname()"
          >
            추천
          </button>
        </div>
        <input
          v-model="commentPassword"
          type="password"
          class="text-input"
          placeholder="비밀번호"
          required
        />
        <button class="submit-button" type="submit" :disabled="isSubmittingComment">
          {{ isSubmittingComment ? '등록 중...' : '댓글 남기기' }}
        </button>
        <p v-if="commentFormError" class="form-error">{{ commentFormError }}</p>
      </form>
    </div>
  </template>
</template>

<style scoped>
.loading-text {
  padding: 40px 0;
  color: var(--muted);
  font-size: 12.5px;
  text-align: center;
}

.content-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
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

.header-actions {
  display: flex;
  gap: 9px;
  align-items: center;
}

.text-action {
  padding: 4px 2px;
  color: #56515d;
  font: inherit;
  font-size: 12px;
  font-weight: 700;
  background: transparent;
  border: 0;
  cursor: pointer;
}

.text-action:hover {
  color: var(--ink);
}

.text-action.danger:hover {
  color: #c0392b;
}

.header-divider {
  width: 1px;
  height: 12px;
  background: var(--line);
}

.post-title {
  margin: 12px 0 0;
  font-size: 20px;
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

.meta-line {
  margin: 8px 0 0;
  color: var(--muted);
  font-size: 11.5px;
}

.place-chip-loading {
  margin: 12px 0 0;
  color: var(--muted);
  font-size: 11.5px;
}

.place-chip {
  display: flex;
  width: 100%;
  padding: 10px 12px;
  margin-top: 12px;
  gap: 10px;
  text-align: left;
  background: var(--soft);
  border: 1px solid var(--line);
  border-radius: 10px;
  cursor: pointer;
  align-items: center;
  transition: border-color 160ms ease;
}

.place-chip:hover {
  border-color: var(--purple);
}

.place-chip svg {
  width: 18px;
  height: 18px;
  color: var(--purple);
  flex: 0 0 auto;
  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 1.8;
}

.place-chip-text {
  display: flex;
  min-width: 0;
  flex: 1;
  flex-direction: column;
}

.place-chip-label {
  color: var(--muted);
  font-size: 10px;
  font-weight: 650;
}

.place-chip-title {
  overflow: hidden;
  color: var(--ink);
  font-size: 12.5px;
  font-weight: 750;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.place-chip-action {
  color: var(--purple);
  font-size: 11px;
  font-weight: 700;
  white-space: nowrap;
  flex: 0 0 auto;
}

.like-button {
  display: inline-flex;
  padding: 7px 14px;
  margin-top: 12px;
  gap: 6px;
  color: #56515d;
  font: inherit;
  font-size: 12px;
  font-weight: 700;
  background: #fff;
  border: 1px solid #d7d4db;
  border-radius: 999px;
  cursor: pointer;
  align-items: center;
  transition: color 160ms ease, background-color 160ms ease, border-color 160ms ease;
}

.like-button:hover {
  border-color: var(--purple);
}

.like-button svg {
  width: 16px;
  height: 16px;
  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 1.8;
}

.like-button.liked {
  color: var(--purple);
  background: var(--purple-soft);
  border-color: var(--purple);
}

.like-button.liked svg {
  fill: currentColor;
}

.author-line {
  margin: 16px 0 0;
}

.author-badge {
  display: inline-block;
  padding: 4px 10px;
  color: #56515d;
  font-size: 11px;
  font-weight: 700;
  background: var(--soft);
  border-radius: 999px;
}

.post-content {
  margin: 10px 0 0;
  color: #3c3842;
  font-size: 13px;
  line-height: 1.65;
  white-space: pre-wrap;
  word-break: keep-all;
  overflow-wrap: anywhere;
}

.delete-confirm {
  padding: 14px;
  margin-top: 18px;
  background: #fff5f5;
  border: 1px solid #efc6c6;
  border-radius: 10px;
}

.delete-confirm > p {
  margin: 0 0 9px;
  color: #9b2f2f;
  font-size: 12px;
  font-weight: 650;
}

.delete-confirm-actions {
  display: flex;
  margin-top: 9px;
  gap: 8px;
}

.ghost-button,
.danger-button {
  flex: 1;
  min-height: 38px;
  font: inherit;
  font-size: 12px;
  font-weight: 700;
  border-radius: 8px;
  cursor: pointer;
}

.ghost-button {
  color: #56515d;
  background: #fff;
  border: 1px solid #d7d4db;
}

.danger-button {
  color: #fff;
  background: #c0392b;
  border: 0;
}

.comment-section {
  padding-top: 18px;
  margin-top: 18px;
  border-top: 1px solid var(--line);
}

.comment-heading {
  margin: 0 0 12px;
  color: var(--ink);
  font-size: 13px;
  font-weight: 750;
}

.comment-list {
  display: flex;
  padding: 0;
  margin: 0;
  gap: 12px;
  list-style: none;
  flex-direction: column;
}

.comment-item {
  padding-bottom: 12px;
  border-bottom: 1px solid var(--line);
}

.comment-topline {
  display: flex;
  gap: 8px;
  align-items: baseline;
  justify-content: space-between;
}

.comment-nickname {
  color: var(--purple);
  font-size: 12px;
  font-weight: 750;
}

.comment-topline-right {
  display: flex;
  gap: 8px;
  align-items: baseline;
  flex: 0 0 auto;
}

.comment-time {
  color: #a19da6;
  font-size: 10.5px;
}

.comment-delete {
  padding: 0;
  color: #a19da6;
  font: inherit;
  font-size: 10.5px;
  font-weight: 650;
  background: transparent;
  border: 0;
  cursor: pointer;
}

.comment-delete:hover {
  color: #c0392b;
}

.comment-delete-confirm {
  padding: 10px;
  margin-top: 8px;
  background: #fff5f5;
  border: 1px solid #efc6c6;
  border-radius: 9px;
}

.comment-delete-actions {
  display: flex;
  margin-top: 8px;
  gap: 7px;
}

.ghost-button-sm,
.danger-button-sm {
  flex: 1;
  min-height: 32px;
  font: inherit;
  font-size: 11px;
  font-weight: 700;
  border-radius: 7px;
  cursor: pointer;
}

.ghost-button-sm {
  color: #56515d;
  background: #fff;
  border: 1px solid #d7d4db;
}

.danger-button-sm {
  color: #fff;
  background: #c0392b;
  border: 0;
}

.comment-body {
  margin: 4px 0 0;
  color: #3c3842;
  font-size: 12.5px;
  line-height: 1.55;
  white-space: pre-wrap;
  word-break: keep-all;
  overflow-wrap: anywhere;
}

.comment-empty {
  margin: 0;
  color: var(--muted);
  font-size: 12px;
}

.comment-form {
  display: flex;
  margin-top: 16px;
  gap: 9px;
  flex-direction: column;
}

.comment-form-row {
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
  min-height: 72px;
  resize: vertical;
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
  margin: 8px 0 0;
  color: #9b2f2f;
  font-size: 11.5px;
}

.edit-form {
  display: flex;
  gap: 9px;
  flex-direction: column;
}

.edit-form .category-pill {
  align-self: flex-start;
}

.rating-picker {
  display: flex;
  gap: 4px;
  margin-top: 4px;
}

.star-button {
  width: 28px;
  height: 28px;
  padding: 0;
  color: #d8d5db;
  font-size: 19px;
  background: transparent;
  border: 0;
  cursor: pointer;
}

.star-button.filled {
  color: var(--star);
}

.edit-form-actions {
  display: flex;
  gap: 8px;
}

.edit-form-actions .ghost-button,
.edit-form-actions .submit-button {
  flex: 1;
}
</style>
