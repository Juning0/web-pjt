<script setup lang="ts">
import { ref } from 'vue'

const searchQuery = ref('')

const handleBack = () => {
  console.log('뒤로가기')
}

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    console.log('검색:', searchQuery.value)
  }
}

const handleKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Enter') {
    handleSearch()
  }
}
</script>

<template>
  <div class="board-header">
    <div class="header-wrapper">
      <button class="back-btn" @click="handleBack">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 12H5M12 19l-7-7 7-7" />
        </svg>
      </button>

      <div class="search-box">
        <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"></circle>
          <path d="m21 21-4.35-4.35"></path>
        </svg>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="검색..."
          class="search-input"
          @keydown="handleKeydown"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.board-header {
  width: 100%;
  padding: 16px 20px;
  background-color: #ffffff;
  border-bottom: 1px solid #f0f0f0;
}

.header-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
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

.search-box {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  background-color: #ffffff;
  transition: border-color 0.2s;
  flex: 1;
  max-width: 500px;
}

.search-box:focus-within {
  border-color: #333;
}

.search-icon {
  width: 18px;
  height: 18px;
  color: #999;
  flex-shrink: 0;
}

.search-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 14px;
  color: #333;
}

.search-input::placeholder {
  color: #999;
}

@media (max-width: 640px) {
  .board-header {
    padding: 12px 16px;
  }

  .page-title {
    font-size: 18px;
  }
}
</style>
