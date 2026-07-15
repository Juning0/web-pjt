<script setup>
import { onUnmounted, ref, watch } from 'vue'
import { CATEGORIES } from '@/constants/categories'
import { randomNickname } from '@/utils/nickname'
import { createPost } from '@/api/posts'

const props = defineProps({
  open: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['close', 'created'])

const selectedCategory = ref(null)
const rating = ref(0)
const title = ref('')
const content = ref('')
const nickname = ref(randomNickname())
const password = ref('')
const isSubmitting = ref(false)
const formError = ref('')

function resetForm() {
  selectedCategory.value = null
  rating.value = 0
  title.value = ''
  content.value = ''
  nickname.value = randomNickname()
  password.value = ''
  isSubmitting.value = false
  formError.value = ''
}

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) resetForm()
  },
)

function toggleCategory(category) {
  selectedCategory.value = selectedCategory.value === category ? null : category
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

async function submitPost() {
  if (isSubmitting.value) return

  if (!selectedCategory.value) {
    formError.value = '카테고리를 선택해 주세요.'
    return
  }
  if (!title.value.trim() || !content.value.trim() || !nickname.value.trim() || !password.value.trim()) {
    formError.value = '제목, 내용, 닉네임, 비밀번호를 모두 입력해 주세요.'
    return
  }

  formError.value = ''
  isSubmitting.value = true

  try {
    const created = await createPost({
      category: selectedCategory.value,
      title: title.value.trim(),
      content: `[${nickname.value.trim()}] ${content.value.trim()}`,
      password: password.value.trim(),
      rating: rating.value || null,
    })
    emit('created', created)
  } catch (error) {
    formError.value = error.message || '게시글 등록에 실패했어요.'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="open" class="modal-backdrop" @click.self="handleClose">
        <section class="write-modal" role="dialog" aria-modal="true" aria-label="글쓰기">
          <header class="modal-header">
            <button class="icon-button" type="button" aria-label="닫기" @click="handleClose">
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="m6 6 12 12M18 6 6 18" />
              </svg>
            </button>
            <h2>글쓰기</h2>
            <span class="header-spacer" aria-hidden="true"></span>
          </header>

          <form class="modal-body" @submit.prevent="submitPost">
            <label class="field-label">카테고리</label>
            <div class="category-chips" aria-label="게시글 카테고리 선택">
              <button
                v-for="category in CATEGORIES"
                :key="category"
                type="button"
                :class="{ active: selectedCategory === category }"
                :aria-pressed="selectedCategory === category"
                @click="toggleCategory(category)"
              >
                {{ category }}
              </button>
            </div>

            <label class="field-label">평점</label>
            <div class="rating-picker" role="radiogroup" aria-label="별점 선택">
              <button
                v-for="value in 5"
                :key="value"
                type="button"
                :class="['star-button', { filled: value <= rating }]"
                :aria-pressed="value <= rating"
                :aria-label="`${value}점`"
                @click="rating = value"
              >★</button>
              <span v-if="!rating" class="rating-hint">탭해서 선택</span>
            </div>

            <input
              v-model="title"
              class="text-input"
              maxlength="200"
              placeholder="제목"
            />
            <textarea
              v-model="content"
              class="text-area"
              placeholder="내용을 입력하세요..."
            ></textarea>

            <div class="nickname-password-row">
              <div class="nickname-field">
                <input
                  v-model="nickname"
                  class="text-input"
                  maxlength="20"
                  placeholder="닉네임"
                />
                <button
                  type="button"
                  class="nickname-suggest"
                  title="닉네임 추천 받기"
                  @click="nickname = randomNickname()"
                >
                  추천
                </button>
              </div>
              <input
                v-model="password"
                type="password"
                class="text-input"
                placeholder="비밀번호"
              />
            </div>
            <p class="password-hint">* 비밀번호는 수정/삭제 시 필요해요</p>

            <p v-if="formError" class="form-error">{{ formError }}</p>

            <button class="submit-button" type="submit" :disabled="isSubmitting">
              {{ isSubmitting ? '등록 중...' : '등록하기' }}
            </button>
          </form>
        </section>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.modal-backdrop,
.write-modal,
.write-modal * {
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

.write-modal {
  --ink: #28262f;
  --muted: #716e78;
  --line: #dedce3;
  --soft: #f7f6f8;
  --purple: #7e66e2;
  --purple-soft: #f1edff;
  --star: #e9a900;
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

.modal-header h2 {
  margin: 0;
  font-size: 15px;
  font-weight: 750;
}

.header-spacer {
  width: 34px;
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

.icon-button:hover {
  background: var(--soft);
}

.icon-button svg {
  width: 18px;
  height: 18px;
  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 2;
}

.modal-body {
  display: flex;
  padding: 18px 20px 24px;
  overflow-y: auto;
  gap: 9px;
  flex-direction: column;
}

.field-label {
  margin-top: 8px;
  color: var(--muted);
  font-size: 11.5px;
  font-weight: 700;
}

.category-chips {
  display: flex;
  gap: 7px;
  flex-wrap: wrap;
}

.category-chips button {
  min-height: 30px;
  padding: 5px 12px;
  color: #625e67;
  font: inherit;
  font-size: 11px;
  font-weight: 650;
  background: #fff;
  border: 1px solid #d7d4db;
  border-radius: 999px;
  cursor: pointer;
}

.category-chips button.active {
  color: #fff;
  background: var(--ink);
  border-color: var(--ink);
}

.rating-picker {
  display: flex;
  gap: 4px;
  align-items: center;
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

.rating-hint {
  margin-left: 6px;
  color: #a19da6;
  font-size: 11px;
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
  min-height: 110px;
  resize: vertical;
}

.nickname-password-row {
  display: flex;
  gap: 8px;
}

.nickname-field {
  display: flex;
  flex: 1;
  gap: 6px;
}

.nickname-field .text-input {
  flex: 1;
  min-width: 0;
}

.nickname-password-row > .text-input {
  flex: 1;
  min-width: 0;
}

.nickname-suggest {
  padding: 0 12px;
  color: var(--purple);
  font: inherit;
  font-size: 11.5px;
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

.password-hint {
  margin: 0;
  color: #a19da6;
  font-size: 10.5px;
}

.form-error {
  margin: 0;
  color: #9b2f2f;
  font-size: 11.5px;
}

.submit-button {
  min-height: 46px;
  margin-top: 6px;
  color: #fff;
  font: inherit;
  font-size: 13px;
  font-weight: 750;
  background: var(--ink);
  border: 0;
  border-radius: 10px;
  cursor: pointer;
}

.submit-button:disabled {
  background: #9a97a0;
  cursor: not-allowed;
}

.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 160ms ease;
}

.modal-fade-enter-active .write-modal,
.modal-fade-leave-active .write-modal {
  transition: transform 180ms ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-from .write-modal,
.modal-fade-leave-to .write-modal {
  transform: translateY(10px) scale(0.98);
}

@media (prefers-reduced-motion: reduce) {
  .modal-fade-enter-active,
  .modal-fade-leave-active,
  .modal-fade-enter-active .write-modal,
  .modal-fade-leave-active .write-modal {
    transition: none;
  }
}
</style>
