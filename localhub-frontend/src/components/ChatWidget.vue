<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { requestChat } from '@/api/chat'

const props = defineProps({
  apiBaseUrl: {
    type: String,
    default: '',
  },
  initialOpen: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits([
  'select-location',
  'select-post',
  'open-location-detail',
  'related-posts',
])

const STORAGE_KEY = 'localhub-chat-history-v1'
const MAX_STORED_MESSAGES = 30

const modes = [
  { id: 'recommend', label: '추천' },
  { id: 'posts', label: '게시글 검색' },
  { id: 'faq', label: 'FAQ' },
]

const starters = {
  recommend: [
    '대전 관광지 추천해줘',
    '평점 높은 음식점 알려줘',
    '공주 숙소 찾아줘',
  ],
  posts: [
    '칼국수 관련 게시글 찾아줘',
    '평점 있는 후기 보여줘',
    '최신 커뮤니티 게시글 찾아줘',
  ],
  faq: [
    '어떤 지역 데이터를 볼 수 있어?',
    '축제 일정도 알 수 있어?',
    '지도 마커도 가능해?',
  ],
}

function createWelcomeMessage() {
  return {
    id: `welcome-${Date.now()}`,
    role: 'assistant',
    content: '안녕하세요! 대전·충청권에서 어디로 떠나볼까요? 장소 추천, 평점, 축제 정보, 커뮤니티 글을 찾아드릴게요.',
    sources: [],
    suggestions: [],
  }
}

function loadMessages() {
  try {
    const saved = JSON.parse(window.localStorage.getItem(STORAGE_KEY) || '[]')
    if (Array.isArray(saved) && saved.some((item) => item?.role === 'user')) {
      return saved
        .filter(
          (item) =>
            item &&
            ['user', 'assistant'].includes(item.role) &&
            typeof item.content === 'string',
        )
        .slice(-MAX_STORED_MESSAGES)
    }
  } catch {
    // A damaged history should not prevent the chatbot from opening.
  }
  return [createWelcomeMessage()]
}

const isOpen = ref(props.initialOpen)
const mode = ref('recommend')
const draft = ref('')
const messages = ref(loadMessages())
const isLoading = ref(false)
const isComposing = ref(false)
const messageList = ref(null)
const inputBox = ref(null)

const activeStarters = computed(() => starters[mode.value])
const placeholder = computed(() => {
  if (mode.value === 'posts') return '검색할 장소나 게시글 내용을 입력하세요'
  if (mode.value === 'faq') return 'LocalHub 사용법을 물어보세요'
  return '어디로 떠나고 싶은지 물어보세요'
})

watch(
  messages,
  (value) => {
    try {
      window.localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify(value.slice(-MAX_STORED_MESSAGES)),
      )
    } catch {
      // Private browsing or a full storage quota can disable persistence safely.
    }
  },
  { deep: true },
)

watch(isOpen, async (opened) => {
  if (!opened) return
  await nextTick()
  scrollToBottom()
  inputBox.value?.focus()
})

onMounted(() => {
  if (isOpen.value) scrollToBottom()
})

function openChat() {
  isOpen.value = true
}

function closeChat() {
  isOpen.value = false
}

function clearHistory() {
  messages.value = [createWelcomeMessage()]
  draft.value = ''
  nextTick(() => {
    resetInputHeight()
    inputBox.value?.focus()
  })
}

function changeMode(nextMode) {
  mode.value = nextMode
  nextTick(() => inputBox.value?.focus())
}

function scrollToBottom() {
  if (!messageList.value) return
  messageList.value.scrollTop = messageList.value.scrollHeight
}

function resizeInput(event) {
  const element = event.target
  element.style.height = 'auto'
  element.style.height = `${Math.min(element.scrollHeight, 96)}px`
}

function resetInputHeight() {
  if (inputBox.value) inputBox.value.style.height = 'auto'
}

function handleEnter(event) {
  if (event.isComposing || isComposing.value || event.shiftKey) return
  event.preventDefault()
  sendMessage()
}

function makeId(prefix) {
  return `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2)}`
}

function historyContent(item) {
  if (item.role !== 'assistant' || !item.sources?.length) return item.content
  const titles = item.sources.map((source) => source.title).filter(Boolean).slice(0, 8)
  return titles.length ? `${item.content}\n[화면에 표시된 결과: ${titles.join(', ')}]` : item.content
}

async function sendMessage(text = draft.value) {
  const message = text.trim()
  if (!message || isLoading.value) return

  const requestMode = mode.value
  const history = messages.value
    .filter((item) => ['user', 'assistant'].includes(item.role))
    .slice(-8)
    .map((item) => ({ role: item.role, content: historyContent(item).slice(0, 2000) }))

  messages.value.push({
    id: makeId('user'),
    role: 'user',
    content: message,
    sources: [],
    suggestions: [],
  })
  draft.value = ''
  isLoading.value = true
  await nextTick()
  resetInputHeight()
  scrollToBottom()

  try {
    const response = await requestChat({
      message,
      history,
      mode: requestMode,
      apiBaseUrl: props.apiBaseUrl,
    })
    if (modes.some((item) => item.id === response.mode)) {
      mode.value = response.mode
    }
    messages.value.push({
      id: makeId('assistant'),
      role: 'assistant',
      content: response.answer,
      sources: response.sources || [],
      suggestions: response.suggestions || [],
      fallback: Boolean(response.fallback),
      engine: response.engine || 'local',
      notice: response.notice || '',
      errorCode: response.error_code || '',
      retryText: response.error_code ? message : '',
      retryMode: requestMode,
    })
  } catch (error) {
    messages.value.push({
      id: makeId('error'),
      role: 'assistant',
      content: error.message || '일시적인 오류가 발생했어요. 잠시 후 다시 시도해 주세요.',
      sources: [],
      suggestions: [],
      isError: true,
      retryText: message,
      retryMode: requestMode,
    })
  } finally {
    isLoading.value = false
    await nextTick()
    scrollToBottom()
    inputBox.value?.focus()
  }
}

function selectSource(source) {
  const eventName = source.type === 'location' ? 'select-location' : 'select-post'
  emit(eventName, source)
  window.dispatchEvent(
    new CustomEvent(`localhub:${eventName}`, {
      detail: source,
    }),
  )
}

function viewLocationOnMap(source) {
  if (source.type !== 'location') return
  closeChat()
  selectSource(source)
}

function openLocationDetail(source) {
  if (source.type !== 'location') return
  emit('open-location-detail', source)
}

function openRelatedPosts(source) {
  if (source.type !== 'location') return
  emit('related-posts', source)
}

async function retryMessage(message, index) {
  if (!message.retryText || isLoading.value) return

  const previousMessage = messages.value[index - 1]
  if (
    previousMessage?.role === 'user' &&
    previousMessage.content === message.retryText
  ) {
    messages.value.splice(index - 1, 2)
  } else {
    messages.value.splice(index, 1)
  }

  if (modes.some((item) => item.id === message.retryMode)) {
    mode.value = message.retryMode
  }

  await sendMessage(message.retryText)
}

function handleImageError(event) {
  event.currentTarget.style.display = 'none'
}

function ratingLabel(source) {
  if (source.rating === null || source.rating === undefined) return '평점 정보 없음'
  return `★ ${Number(source.rating).toFixed(1)} · 리뷰 ${source.review_count || 0}`
}

function formatEventDate(value) {
  if (!/^\d{8}$/.test(value || '')) return value || ''
  return `${value.slice(0, 4)}.${value.slice(4, 6)}.${value.slice(6, 8)}`
}

function eventDateLabel(source) {
  if (!source.start_date && !source.end_date) return ''
  if (source.start_date === source.end_date || !source.end_date) {
    return formatEventDate(source.start_date)
  }
  return `${formatEventDate(source.start_date)} ~ ${formatEventDate(source.end_date)}`
}
</script>

<template>
  <Teleport to="body">
    <Transition name="chat-fade" mode="out-in">
      <button
        v-if="!isOpen"
        key="launcher"
        class="chat-launcher"
        type="button"
        aria-label="LocalHub 챗봇 열기"
        title="LocalHub AI 여행 도우미"
        @click="openChat"
      >
        <svg viewBox="0 0 32 32" aria-hidden="true">
          <path d="M7.5 8.5h17a3 3 0 0 1 3 3v8a3 3 0 0 1-3 3H16l-5.8 4v-4H7.5a3 3 0 0 1-3-3v-8a3 3 0 0 1 3-3Z" />
          <circle cx="11" cy="15.5" r="1.3" />
          <circle cx="16" cy="15.5" r="1.3" />
          <circle cx="21" cy="15.5" r="1.3" />
        </svg>
        <span class="launcher-pulse" aria-hidden="true"></span>
      </button>

      <section
        v-else
        key="panel"
        class="chat-panel"
        role="dialog"
        aria-modal="false"
        aria-label="LocalHub AI 여행 도우미"
      >
        <header class="chat-header">
          <div class="brand-mark" aria-hidden="true">
            <svg viewBox="0 0 24 24">
              <path d="M5.5 6.5h13a2.5 2.5 0 0 1 2.5 2.5v6a2.5 2.5 0 0 1-2.5 2.5H12l-4.5 3v-3h-2A2.5 2.5 0 0 1 3 15V9a2.5 2.5 0 0 1 2.5-2.5Z" />
            </svg>
          </div>
          <div class="header-copy">
            <div class="header-title-row">
              <h2>LocalHub AI</h2>
              <span class="status-dot" aria-label="온라인"></span>
            </div>
            <p>대전·충청 여행 도우미</p>
          </div>
          <button
            class="icon-button clear-button"
            type="button"
            aria-label="대화 내용 지우기"
            title="대화 내용 지우기"
            @click="clearHistory"
          >
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M4 7h16M9 7V4h6v3m-8 0 1 13h8l1-13M10 11v5m4-5v5" />
            </svg>
          </button>
          <button
            class="icon-button"
            type="button"
            aria-label="챗봇 닫기"
            @click="closeChat"
          >
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="m6 6 12 12M18 6 6 18" />
            </svg>
          </button>
        </header>

        <nav class="chat-tabs" aria-label="챗봇 검색 유형">
          <button
            v-for="item in modes"
            :key="item.id"
            type="button"
            :class="['tab-button', { active: mode === item.id }]"
            :aria-current="mode === item.id ? 'page' : undefined"
            @click="changeMode(item.id)"
          >
            {{ item.label }}
          </button>
        </nav>

        <div ref="messageList" class="message-list" aria-live="polite">
          <article
            v-for="(message, index) in messages"
            :key="message.id"
            :class="['message-row', message.role]"
          >
            <div v-if="message.role === 'assistant'" class="mini-avatar" aria-hidden="true">
              <svg viewBox="0 0 24 24">
                <path d="M5.5 6.5h13A2.5 2.5 0 0 1 21 9v6a2.5 2.5 0 0 1-2.5 2.5H12l-4.5 3v-3h-2A2.5 2.5 0 0 1 3 15V9a2.5 2.5 0 0 1 2.5-2.5Z" />
              </svg>
            </div>
            <div class="message-content">
              <p :class="['message-bubble', { error: message.isError }]">
                {{ message.content }}
              </p>
              <button
                v-if="(message.isError || message.errorCode) && message.retryText"
                class="retry-button"
                type="button"
                :disabled="isLoading"
                @click="retryMessage(message, index)"
              >
                다시 시도
              </button>
              <span
                v-if="message.engine"
                :class="['engine-badge', { openai: message.engine === 'openai' }]"
              >
                {{ message.engine === 'openai' ? 'GPT-5 mini' : 'LocalHub 데이터' }}
              </span>
              <p
                v-if="message.notice"
                class="system-notice"
                :title="message.errorCode || undefined"
              >
                <strong>AI 연결 안내</strong>
                {{ message.notice }}
              </p>

              <div v-if="message.sources?.length" class="source-list">
                <article
                  v-for="source in message.sources"
                  :key="`${source.type}-${source.id}`"
                  :class="['source-card', { clickable: source.type === 'location' }]"
                  :tabindex="source.type === 'location' ? 0 : undefined"
                  @click="source.type === 'location' && openLocationDetail(source)"
                  @keydown.enter.self="source.type === 'location' && openLocationDetail(source)"
                >
                  <div v-if="source.type === 'location'" class="source-image">
                    <div class="image-placeholder" aria-hidden="true">
                      <svg viewBox="0 0 24 24">
                        <path d="M4 18V6a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v12H4Zm0-3 4-4 3 3 2-2 5 5M15.5 9a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3Z" />
                      </svg>
                    </div>
                    <img
                      v-if="source.image_url"
                      :src="source.image_url"
                      :alt="`${source.title} 사진`"
                      loading="lazy"
                      @error="handleImageError"
                    />
                  </div>
                  <div class="source-body">
                    <div class="source-topline">
                      <span class="source-category">{{ source.category || '커뮤니티' }}</span>
                      <span v-if="source.type === 'post'" class="view-count">
                        조회 {{ source.view_count || 0 }}
                      </span>
                    </div>
                    <h3>{{ source.title }}</h3>
                    <p v-if="source.type === 'location'" class="rating">
                      {{ ratingLabel(source) }}
                    </p>
                    <p v-if="eventDateLabel(source)" class="event-date">
                      {{ eventDateLabel(source) }}
                    </p>
                    <p v-if="source.address" class="source-address">{{ source.address }}</p>
                    <p v-if="source.excerpt" class="source-excerpt">{{ source.excerpt }}</p>

                    <div v-if="source.type === 'location'" class="source-actions">
                      <button
                        class="source-action"
                        type="button"
                        @click.stop="openLocationDetail(source)"
                      >
                        상세보기
                      </button>
                      <button
                        class="source-action"
                        type="button"
                        @click.stop="viewLocationOnMap(source)"
                      >
                        지도에서 보기
                      </button>
                      <button
                        class="source-action"
                        type="button"
                        @click.stop="openRelatedPosts(source)"
                      >
                        관련 게시글
                      </button>
                    </div>

                    <button
                      v-else
                      class="source-action"
                      type="button"
                      @click="selectSource(source)"
                    >
                      게시글 열기
                      <svg viewBox="0 0 20 20" aria-hidden="true">
                        <path d="m7 4 6 6-6 6" />
                      </svg>
                    </button>
                  </div>
                </article>
              </div>

              <div
                v-if="
                  index === messages.length - 1 &&
                  message.suggestions?.length &&
                  !isLoading
                "
                class="suggestion-list"
              >
                <button
                  v-for="suggestion in message.suggestions"
                  :key="suggestion"
                  type="button"
                  @click="sendMessage(suggestion)"
                >
                  {{ suggestion }}
                </button>
              </div>
            </div>
          </article>

          <div v-if="messages.length === 1" class="starter-area">
            <p>이렇게 물어보세요</p>
            <button
              v-for="starter in activeStarters"
              :key="starter"
              type="button"
              @click="sendMessage(starter)"
            >
              <span aria-hidden="true">{{ mode === 'faq' ? '?' : mode === 'posts' ? '⌕' : '✦' }}</span>
              {{ starter }}
            </button>
          </div>

          <div v-if="isLoading" class="message-row assistant loading-row">
            <div class="mini-avatar" aria-hidden="true">
              <svg viewBox="0 0 24 24">
                <path d="M5.5 6.5h13A2.5 2.5 0 0 1 21 9v6a2.5 2.5 0 0 1-2.5 2.5H12l-4.5 3v-3h-2A2.5 2.5 0 0 1 3 15V9a2.5 2.5 0 0 1 2.5-2.5Z" />
              </svg>
            </div>
            <div class="typing-indicator" aria-label="답변 작성 중">
              <span></span><span></span><span></span>
            </div>
          </div>
        </div>

        <form class="chat-composer" @submit.prevent="sendMessage()">
          <textarea
            ref="inputBox"
            v-model="draft"
            rows="1"
            maxlength="800"
            :placeholder="placeholder"
            aria-label="챗봇에게 질문하기"
            :disabled="isLoading"
            @input="resizeInput"
            @compositionstart="isComposing = true"
            @compositionend="isComposing = false"
            @keydown.enter="handleEnter"
          ></textarea>
          <button
            type="submit"
            :disabled="!draft.trim() || isLoading"
            aria-label="메시지 보내기"
          >
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="m4 4 17 8-17 8 3-8-3-8Zm3 8h14" />
            </svg>
          </button>
        </form>
        <p class="chat-disclaimer">AI 답변은 LocalHub 제공 데이터를 기준으로 합니다.</p>
      </section>
    </Transition>
  </Teleport>
</template>

<style scoped>
.chat-launcher,
.chat-panel,
.chat-panel * {
  box-sizing: border-box;
}

.chat-launcher {
  position: fixed;
  right: max(28px, calc((100vw - 1120px) / 2 + 28px));
  bottom: 28px;
  z-index: 1000;
  display: grid;
  width: 58px;
  height: 58px;
  padding: 0;
  place-items: center;
  color: #a993ff;
  background: #28262f;
  border: 1px solid #1d1b22;
  border-radius: 50%;
  box-shadow: 0 14px 32px rgb(31 28 42 / 24%);
  cursor: pointer;
  transition: transform 180ms ease, box-shadow 180ms ease;
}

.chat-launcher:hover {
  transform: translateY(-3px);
  box-shadow: 0 18px 36px rgb(31 28 42 / 30%);
}

.chat-launcher:focus-visible,
.chat-panel button:focus-visible,
.chat-panel textarea:focus-visible {
  outline: 3px solid rgb(126 102 226 / 28%);
  outline-offset: 2px;
}

.chat-launcher svg {
  width: 31px;
  height: 31px;
  fill: currentColor;
}

.chat-launcher svg circle {
  fill: #28262f;
}

.launcher-pulse {
  position: absolute;
  top: 2px;
  right: 3px;
  width: 12px;
  height: 12px;
  background: #55c78c;
  border: 3px solid #28262f;
  border-radius: 50%;
}

.chat-panel {
  --ink: #28262f;
  --muted: #716e78;
  --line: #dedce3;
  --soft: #f7f6f8;
  --purple: #7e66e2;
  --purple-soft: #f1edff;
  --star: #e9a900;
  position: fixed;
  right: max(28px, calc((100vw - 1120px) / 2 + 28px));
  bottom: 96px;
  z-index: 1000;
  display: flex;
  width: min(400px, calc(100vw - 32px));
  height: min(650px, calc(100dvh - 124px));
  overflow: hidden;
  color: var(--ink);
  font-family: Pretendard, Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background: #fff;
  border: 1px solid #cbc8d1;
  border-radius: 15px;
  box-shadow: 0 24px 60px rgb(38 34 48 / 22%);
  flex-direction: column;
}

.chat-header {
  display: flex;
  min-height: 68px;
  padding: 12px 12px 11px 15px;
  align-items: center;
  border-bottom: 1px solid var(--line);
}

.brand-mark,
.mini-avatar {
  display: grid;
  flex: 0 0 auto;
  color: var(--purple);
  background: var(--purple-soft);
  border-radius: 10px;
  place-items: center;
}

.brand-mark {
  width: 40px;
  height: 40px;
}

.brand-mark svg {
  width: 23px;
  height: 23px;
  fill: currentColor;
}

.header-copy {
  min-width: 0;
  margin-left: 10px;
  flex: 1;
}

.header-title-row {
  display: flex;
  gap: 7px;
  align-items: center;
}

.header-copy h2 {
  margin: 0;
  font-size: 15px;
  font-weight: 750;
  line-height: 1.25;
  letter-spacing: -0.01em;
}

.header-copy p {
  margin: 3px 0 0;
  color: var(--muted);
  font-size: 11.5px;
  line-height: 1.3;
}

.status-dot {
  width: 7px;
  height: 7px;
  background: #3cba78;
  border-radius: 50%;
  box-shadow: 0 0 0 3px rgb(60 186 120 / 13%);
}

.icon-button {
  display: grid;
  width: 34px;
  height: 34px;
  padding: 0;
  color: #595660;
  background: transparent;
  border: 0;
  border-radius: 8px;
  cursor: pointer;
  place-items: center;
}

.icon-button:hover {
  color: var(--ink);
  background: var(--soft);
}

.icon-button svg {
  width: 19px;
  height: 19px;
  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 1.8;
}

.clear-button svg {
  width: 18px;
  height: 18px;
}

.chat-tabs {
  display: flex;
  gap: 7px;
  padding: 10px 14px;
  background: #fff;
  border-bottom: 1px solid var(--line);
}

.tab-button {
  min-height: 30px;
  padding: 5px 12px;
  color: #56535d;
  font: inherit;
  font-size: 11.5px;
  font-weight: 650;
  background: #fff;
  border: 1px solid #cfccd5;
  border-radius: 999px;
  cursor: pointer;
}

.tab-button:hover {
  border-color: #8d8898;
}

.tab-button.active {
  color: #fff;
  background: var(--ink);
  border-color: var(--ink);
}

.message-list {
  min-height: 0;
  padding: 15px 14px 18px;
  overflow-x: hidden;
  overflow-y: auto;
  background: #fbfafb;
  flex: 1;
  overscroll-behavior: contain;
  scroll-behavior: smooth;
}

.message-list::-webkit-scrollbar {
  width: 7px;
}

.message-list::-webkit-scrollbar-thumb {
  background: #d5d2d9;
  border: 2px solid #fbfafb;
  border-radius: 10px;
}

.message-row {
  display: flex;
  max-width: 100%;
  margin-bottom: 14px;
  align-items: flex-start;
}

.message-row.user {
  justify-content: flex-end;
}

.mini-avatar {
  width: 28px;
  height: 28px;
  margin-right: 7px;
  border-radius: 8px;
}

.mini-avatar svg {
  width: 16px;
  height: 16px;
  fill: currentColor;
}

.message-content {
  min-width: 0;
  max-width: calc(100% - 35px);
}

.user .message-content {
  max-width: 82%;
}

.message-bubble {
  width: fit-content;
  max-width: 100%;
  margin: 0;
  padding: 10px 12px;
  white-space: pre-wrap;
  color: #38353e;
  font-size: 12.5px;
  line-height: 1.58;
  word-break: keep-all;
  overflow-wrap: anywhere;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 4px 12px 12px 12px;
}

.user .message-bubble {
  color: #fff;
  background: var(--ink);
  border-color: var(--ink);
  border-radius: 12px 4px 12px 12px;
}

.message-bubble.error {
  color: #9b2f2f;
  background: #fff5f5;
  border-color: #efc6c6;
}

.retry-button {
  margin-top: 6px;
  padding: 6px 10px;
  color: #8c3434;
  font: inherit;
  font-size: 10.5px;
  font-weight: 700;
  background: #fff;
  border: 1px solid #e3b8b8;
  border-radius: 7px;
  cursor: pointer;
}

.retry-button:hover {
  background: #fff1f1;
  border-color: #cf8f8f;
}

.retry-button:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.engine-badge {
  display: inline-block;
  margin-top: 5px;
  padding: 2px 6px;
  color: #77727e;
  font-size: 9px;
  font-weight: 700;
  line-height: 1.4;
  background: #f1eff3;
  border-radius: 999px;
}

.engine-badge.openai {
  color: #6550a5;
  background: #f0ebff;
}

.system-notice {
  width: 100%;
  margin: 6px 0 0;
  padding: 8px 10px;
  color: #725b20;
  font-size: 10.5px;
  line-height: 1.45;
  background: #fff9e8;
  border: 1px solid #ead9a4;
  border-radius: 8px;
}

.system-notice strong {
  display: block;
  margin-bottom: 2px;
  color: #5e4913;
}

.source-list {
  display: grid;
  gap: 8px;
  width: 100%;
  margin-top: 8px;
}

.source-card {
  display: flex;
  min-width: 0;
  overflow: hidden;
  background: #fff;
  border: 1px solid #d3d0d8;
  border-radius: 10px;
}

.source-card:hover {
  border-color: #aaa5b2;
  box-shadow: 0 5px 16px rgb(43 39 52 / 7%);
}

.source-card.clickable {
  cursor: pointer;
}

.source-card.clickable:focus-visible {
  outline: 3px solid rgb(126 102 226 / 24%);
  outline-offset: 2px;
}

.source-image {
  position: relative;
  width: 92px;
  min-height: 112px;
  flex: 0 0 92px;
  background: #ebe9ed;
}

.source-image img {
  position: absolute;
  inset: 0;
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-placeholder {
  display: grid;
  width: 100%;
  height: 100%;
  min-height: 112px;
  color: #aaa6b0;
  background:
    linear-gradient(135deg, rgb(255 255 255 / 45%) 25%, transparent 25%) -8px 0 / 16px 16px,
    linear-gradient(225deg, rgb(255 255 255 / 45%) 25%, transparent 25%) -8px 0 / 16px 16px,
    #e8e6ea;
  place-items: center;
}

.image-placeholder svg {
  width: 27px;
  height: 27px;
  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 1.5;
}

.source-body {
  min-width: 0;
  padding: 10px 11px 9px;
  flex: 1;
}

.source-topline {
  display: flex;
  margin-bottom: 3px;
  gap: 8px;
  align-items: center;
  justify-content: space-between;
}

.source-category {
  color: var(--purple);
  font-size: 10px;
  font-weight: 750;
}

.view-count {
  color: #8b8791;
  font-size: 9.5px;
}

.source-body h3 {
  margin: 0;
  overflow: hidden;
  color: #28252d;
  font-size: 12.5px;
  font-weight: 750;
  line-height: 1.35;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.rating,
.event-date {
  margin: 4px 0 0;
  color: var(--star);
  font-size: 10.5px;
  font-weight: 700;
}

.event-date {
  color: var(--purple);
}

.source-address,
.source-excerpt {
  display: -webkit-box;
  margin: 4px 0 0;
  overflow: hidden;
  color: #77737c;
  font-size: 10px;
  line-height: 1.4;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.source-actions {
  display: flex;
  margin-top: 8px;
  gap: 5px;
  flex-wrap: wrap;
}

.source-action {
  display: inline-flex;
  min-height: 26px;
  margin: 7px 0 0;
  padding: 4px 7px;
  gap: 2px;
  color: #3c3842;
  font: inherit;
  font-size: 9.5px;
  font-weight: 700;
  background: #fff;
  border: 1px solid #d7d2e2;
  border-radius: 6px;
  cursor: pointer;
  align-items: center;
}

.source-actions .source-action {
  margin-top: 0;
}

.source-action:hover {
  color: var(--purple);
  background: var(--purple-soft);
  border-color: #bdb2ea;
}

.source-action svg {
  width: 13px;
  height: 13px;
  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 1.8;
}

.suggestion-list {
  display: flex;
  margin-top: 8px;
  gap: 6px;
  flex-wrap: wrap;
}

.suggestion-list button {
  padding: 6px 9px;
  color: #5f586d;
  font: inherit;
  font-size: 10px;
  background: #fff;
  border: 1px solid #d7d2e2;
  border-radius: 999px;
  cursor: pointer;
}

.suggestion-list button:hover {
  color: #6249c4;
  background: var(--purple-soft);
  border-color: #bdb2ea;
}

.starter-area {
  margin: 2px 0 8px 35px;
}

.starter-area > p {
  margin: 0 0 7px;
  color: #89858e;
  font-size: 10.5px;
  font-weight: 650;
}

.starter-area button {
  display: flex;
  width: 100%;
  min-height: 37px;
  margin-top: 6px;
  padding: 8px 10px;
  gap: 8px;
  color: #3b3840;
  font: inherit;
  font-size: 11px;
  font-weight: 600;
  text-align: left;
  background: #fff;
  border: 1px solid #d6d3db;
  border-radius: 7px;
  cursor: pointer;
  align-items: center;
}

.starter-area button:hover {
  background: #faf9fc;
  border-color: #aaa5b2;
  transform: translateX(2px);
}

.starter-area button span {
  display: grid;
  width: 20px;
  height: 20px;
  color: var(--purple);
  background: var(--purple-soft);
  border-radius: 6px;
  flex: 0 0 20px;
  place-items: center;
}

.loading-row {
  margin-bottom: 0;
}

.typing-indicator {
  display: flex;
  width: 52px;
  height: 36px;
  gap: 4px;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 4px 12px 12px 12px;
  align-items: center;
  justify-content: center;
}

.typing-indicator span {
  width: 5px;
  height: 5px;
  background: #9a95a0;
  border-radius: 50%;
  animation: typing 1.15s infinite ease-in-out;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 140ms;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 280ms;
}

.chat-composer {
  display: flex;
  min-height: 64px;
  padding: 10px 12px 8px;
  gap: 8px;
  background: #fff;
  border-top: 1px solid var(--line);
  align-items: flex-end;
}

.chat-composer textarea {
  min-width: 0;
  min-height: 40px;
  max-height: 96px;
  padding: 10px 11px;
  color: var(--ink);
  font: inherit;
  font-size: 12px;
  line-height: 1.5;
  resize: none;
  background: #fff;
  border: 1px solid #cbc8d0;
  border-radius: 9px;
  flex: 1;
}

.chat-composer textarea::placeholder {
  color: #aaa6af;
}

.chat-composer textarea:disabled {
  background: #f6f5f7;
}

.chat-composer > button {
  display: grid;
  width: 40px;
  height: 40px;
  padding: 0;
  color: #fff;
  background: var(--ink);
  border: 0;
  border-radius: 9px;
  cursor: pointer;
  flex: 0 0 40px;
  place-items: center;
}

.chat-composer > button:disabled {
  color: #aaa7ae;
  background: #e6e4e8;
  cursor: not-allowed;
}

.chat-composer > button svg {
  width: 20px;
  height: 20px;
  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 1.8;
}

.chat-disclaimer {
  margin: -2px 0 7px;
  color: #9a969e;
  font-size: 9px;
  text-align: center;
}

.chat-fade-enter-active,
.chat-fade-leave-active {
  transition: opacity 160ms ease, transform 180ms ease;
}

.chat-fade-enter-from,
.chat-fade-leave-to {
  opacity: 0;
  transform: translateY(8px) scale(0.98);
}

@keyframes typing {
  0%,
  60%,
  100% {
    opacity: 0.35;
    transform: translateY(0);
  }
  30% {
    opacity: 1;
    transform: translateY(-3px);
  }
}

@media (max-width: 640px) {
  .chat-panel {
    inset: 0;
    width: 100%;
    height: 100dvh;
    border: 0;
    border-radius: 0;
  }

  .chat-header {
    padding-top: max(12px, env(safe-area-inset-top));
  }

  .chat-launcher {
    right: 18px;
    bottom: max(18px, env(safe-area-inset-bottom));
  }

  .chat-composer {
    padding-bottom: max(8px, env(safe-area-inset-bottom));
  }

  .message-list {
    padding-right: 12px;
    padding-left: 12px;
  }

  .message-content {
    max-width: calc(100% - 34px);
  }
}

@media (prefers-reduced-motion: reduce) {
  .chat-launcher,
  .chat-fade-enter-active,
  .chat-fade-leave-active,
  .typing-indicator span {
    transition: none;
    animation: none;
  }
}
</style>
