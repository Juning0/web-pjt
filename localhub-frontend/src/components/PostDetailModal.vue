<script setup>
import { computed, onUnmounted, ref, watch } from 'vue'
import { parseAuthoredContent, randomNickname } from '@/utils/nickname'
import { createComment, deleteComment, deletePost, updatePost } from '@/api/posts'

const props = defineProps({
  post: {
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

const emit = defineEmits(['close', 'deleted'])

const post = ref(null)

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
  editPassword.value = ''
  editFormError.value = ''
  isSavingEdit.value = false
}

watch(
  () => [props.open, props.post],
  ([isOpen, nextPost]) => {
    if (isOpen && nextPost) {
      resetInteractionState()
      // 부모가 들고 있는 같은 객체를 그대로 참조해서, 댓글 변경이 다시 열어도 유지되게 한다.
      post.value = nextPost
    }
  },
  { immediate: true },
)

const authorContent = computed(() => parseAuthoredContent(post.value?.content))

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

function openEditForm() {
  isDeleteConfirmOpen.value = false
  editTitle.value = post.value.title
  editContent.value = authorContent.value.body
  editPassword.value = ''
  editFormError.value = ''
  isEditFormOpen.value = true
}

function cancelEditForm() {
  isEditFormOpen.value = false
  editTitle.value = ''
  editContent.value = ''
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
    })
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
    emit('close')
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
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="open" class="modal-backdrop" @click.self="handleClose">
        <section
          class="post-modal"
          role="dialog"
          aria-modal="true"
          :aria-label="post?.title || '게시글 상세'"
        >
          <header class="modal-header">
            <button class="icon-button" type="button" aria-label="닫기" @click="handleClose">
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="m15 5-7 7 7 7" />
              </svg>
            </button>
            <div v-if="post && !loading" class="header-actions">
              <button class="text-action" type="button" @click="openEditForm">수정</button>
              <span class="header-divider" aria-hidden="true"></span>
              <button class="text-action danger" type="button" @click="openDeleteConfirm">삭제</button>
            </div>
          </header>

          <div class="modal-body">
            <p v-if="loading" class="loading-text">불러오는 중...</p>
            <template v-else-if="post">
              <template v-if="!isEditFormOpen">
                <div class="pill-row">
                  <span class="category-pill">{{ post.category }}</span>
                  <span v-if="post.location_title" class="location-pill">📍 {{ post.location_title }}</span>
                </div>
                <h2 class="post-title">{{ post.title }}</h2>

                <div class="meta-row">
                  <p class="meta-line">{{ metaLabel }}</p>
                  <span class="author-badge">{{ authorContent.nickname }}</span>
                </div>

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
                      class="text-input"
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
                    <input
                      v-model="commentPassword"
                      type="password"
                      class="text-input"
                      placeholder="비밀번호"
                      required
                    />
                  </div>
                  <button class="submit-button" type="submit" :disabled="isSubmittingComment">
                    {{ isSubmittingComment ? '등록 중...' : '댓글 남기기' }}
                  </button>
                  <p v-if="commentFormError" class="form-error">{{ commentFormError }}</p>
                </form>
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
.post-modal,
.post-modal * {
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

.post-modal {
  --ink: #28262f;
  --muted: #716e78;
  --line: #dedce3;
  --soft: #f7f6f8;
  --purple: #7e66e2;
  --purple-soft: #f1edff;
  position: relative;
  display: flex;
  width: min(420px, 100%);
  max-height: min(720px, calc(100dvh - 48px));
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
  padding: 8px 14px;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--line);
}

.icon-button {
  display: grid;
  width: 34px;
  height: 34px;
  padding: 0;
  margin-left: -8px;
  color: var(--ink);
  background: transparent;
  border: 0;
  border-radius: 8px;
  cursor: pointer;
  place-items: center;
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

.pill-row {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
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

.location-pill {
  display: inline-block;
  padding: 5px 11px;
  overflow: hidden;
  color: #56515d;
  font-size: 11px;
  font-weight: 750;
  text-overflow: ellipsis;
  white-space: nowrap;
  background: var(--soft);
  border-radius: 999px;
}

.post-title {
  margin: 12px 0 0;
  font-size: 20px;
  font-weight: 800;
  letter-spacing: -0.02em;
}

.meta-row {
  display: flex;
  margin-top: 8px;
  align-items: baseline;
  justify-content: space-between;
  gap: 8px;
}

.meta-line {
  margin: 0;
  color: var(--muted);
  font-size: 11.5px;
}

.author-badge {
  display: inline-block;
  flex: 0 0 auto;
  padding: 4px 10px;
  color: #56515d;
  font-size: 11px;
  font-weight: 700;
  white-space: nowrap;
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

.comment-form-row input {
  min-width: 0;
  flex: 1 1 0;
}

.nickname-suggest {
  flex: 0 0 auto;
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

.edit-form-actions {
  display: flex;
  gap: 8px;
}

.edit-form-actions .ghost-button,
.edit-form-actions .submit-button {
  flex: 1;
}

.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 160ms ease;
}

.modal-fade-enter-active .post-modal,
.modal-fade-leave-active .post-modal {
  transition: transform 180ms ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-from .post-modal,
.modal-fade-leave-to .post-modal {
  transform: translateY(10px) scale(0.98);
}

@media (prefers-reduced-motion: reduce) {
  .modal-fade-enter-active,
  .modal-fade-leave-active,
  .modal-fade-enter-active .post-modal,
  .modal-fade-leave-active .post-modal,
  .modal-toast-fade-enter-active,
  .modal-toast-fade-leave-active {
    transition: none;
  }
}
</style>
