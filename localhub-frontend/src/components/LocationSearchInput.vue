<script setup>
import { ref, watch } from 'vue'
import { listLocations } from '@/api/locations'

const props = defineProps({
  modelValue: {
    type: Object,
    default: null,
  },
  placeholder: {
    type: String,
    default: '장소명을 검색해 주세요',
  },
})

const emit = defineEmits(['update:modelValue'])

const query = ref(props.modelValue?.title || '')
const results = ref([])
const isSearching = ref(false)
const isDropdownOpen = ref(false)

let searchTimer
let searchToken = 0

// 부모가 v-model을 외부에서 비우면(폼 리셋 등) 입력값도 함께 비운다.
watch(
  () => props.modelValue,
  (value) => {
    query.value = value?.title || ''
  },
)

async function search(keyword) {
  const token = ++searchToken
  isSearching.value = true
  try {
    const response = await listLocations({ keyword, size: 8 })
    if (token !== searchToken) return
    results.value = response.items
    isDropdownOpen.value = true
  } catch {
    if (token !== searchToken) return
    results.value = []
  } finally {
    if (token === searchToken) isSearching.value = false
  }
}

watch(query, (value) => {
  // 방금 selectLocation()으로 채워진 값이면 재검색하지 않는다.
  if (props.modelValue && value === props.modelValue.title) return
  if (props.modelValue) emit('update:modelValue', null)

  window.clearTimeout(searchTimer)
  const trimmed = value.trim()
  if (!trimmed) {
    results.value = []
    isDropdownOpen.value = false
    return
  }
  searchTimer = window.setTimeout(() => search(trimmed), 250)
})

function selectLocation(location) {
  emit('update:modelValue', location)
  query.value = location.title
  results.value = []
  isDropdownOpen.value = false
}

function clear() {
  emit('update:modelValue', null)
  query.value = ''
  results.value = []
  isDropdownOpen.value = false
}

function handleFocus() {
  if (results.value.length) isDropdownOpen.value = true
}

function handleBlur() {
  // li의 click이 blur보다 늦게 처리되므로, 살짝 지연을 두고 닫는다.
  window.setTimeout(() => {
    isDropdownOpen.value = false
  }, 150)
}
</script>

<template>
  <div class="location-field">
    <div class="location-search" :class="{ 'has-selection': modelValue }">
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <circle cx="11" cy="11" r="6.5" />
        <path d="m16 16 4 4" />
      </svg>
      <input
        v-model="query"
        class="location-input"
        :placeholder="placeholder"
        autocomplete="off"
        @focus="handleFocus"
        @blur="handleBlur"
      />
      <button
        v-if="query"
        type="button"
        class="location-clear"
        aria-label="장소 검색어 지우기"
        @click="clear"
      >
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="m6 6 12 12M18 6 6 18" />
        </svg>
      </button>
    </div>

    <ul v-if="isDropdownOpen && results.length" class="location-results">
      <li v-for="location in results" :key="location.content_id" @click="selectLocation(location)">
        <span class="location-result-title">{{ location.title }}</span>
        <span class="location-result-addr">{{ location.addr1 }}</span>
      </li>
    </ul>
    <p v-else-if="isDropdownOpen && !isSearching && query.trim()" class="location-empty">
      검색 결과가 없어요.
    </p>
  </div>
</template>

<style scoped>
.location-field,
.location-field * {
  box-sizing: border-box;
}

.location-field {
  position: relative;
}

.location-search {
  display: flex;
  min-height: 50px;
  padding: 0 14px;
  gap: 10px;
  align-items: center;
  background: #fff;
  border: 1.5px solid #cbc8d0;
  border-radius: 11px;
  transition: border-color 160ms ease;
}

.location-search:focus-within {
  border-color: #7e66e2;
}

.location-search.has-selection {
  background: #f1edff;
  border-color: #7e66e2;
}

.location-search svg {
  width: 19px;
  height: 19px;
  color: #85818b;
  flex: 0 0 auto;
  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-width: 1.8;
}

.location-input {
  width: 100%;
  min-width: 0;
  padding: 0;
  color: #28262f;
  font: inherit;
  font-size: 14.5px;
  font-weight: 650;
  background: transparent;
  border: 0;
  outline: 0;
  flex: 1;
}

.location-clear {
  display: grid;
  width: 24px;
  height: 24px;
  padding: 0;
  color: #85818b;
  background: transparent;
  border: 0;
  cursor: pointer;
  flex: 0 0 auto;
  place-items: center;
}

.location-clear svg {
  width: 16px;
  height: 16px;
}

.location-results {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  z-index: 5;
  width: 100%;
  max-height: 220px;
  padding: 6px;
  margin: 0;
  overflow-y: auto;
  list-style: none;
  background: #fff;
  border: 1px solid #e5e3e8;
  border-radius: 12px;
  box-shadow: 0 16px 34px rgb(35 32 42 / 16%);
}

.location-results li {
  padding: 9px 10px;
  cursor: pointer;
  border-radius: 8px;
}

.location-results li:hover {
  background: #f1edff;
}

.location-result-title {
  display: block;
  overflow: hidden;
  color: #28262f;
  font-size: 13px;
  font-weight: 700;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.location-result-addr {
  display: block;
  margin-top: 2px;
  overflow: hidden;
  color: #716e78;
  font-size: 11px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.location-empty {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  z-index: 5;
  width: 100%;
  padding: 12px;
  margin: 0;
  color: #716e78;
  font-size: 12px;
  text-align: center;
  background: #fff;
  border: 1px solid #e5e3e8;
  border-radius: 12px;
  box-shadow: 0 16px 34px rgb(35 32 42 / 16%);
}
</style>
