<script setup>
import { onUnmounted, watch } from 'vue'
import PostContent from '@/components/PostContent.vue'

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

const emit = defineEmits(['close', 'deleted', 'select-location'])

function handleClose() {
  emit('close')
}

function handleDeleted(postId) {
  emit('deleted', postId)
  emit('close')
}

function handleSelectLocation(payload) {
  emit('select-location', payload)
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
          </header>

          <div class="modal-body">
            <PostContent
              :post="post"
              :loading="loading"
              @deleted="handleDeleted"
              @select-location="handleSelectLocation"
            />
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
  --star: #e9a900;
  position: relative;
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
  padding: 8px 14px;
  align-items: center;
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

.modal-body {
  padding: 18px 20px 24px;
  overflow-y: auto;
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
  .modal-fade-leave-active .post-modal {
    transition: none;
  }
}
</style>
