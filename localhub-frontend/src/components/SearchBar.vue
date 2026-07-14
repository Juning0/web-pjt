<script setup lang="ts">
import { ref } from 'vue'

const searchQuery = ref('')

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
  <div class="search-container">
    <div class="search-wrapper">
      <div class="search-input-box">
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
.search-container {
  width: 100%;
  padding: 16px 20px;
  background-color: #ffffff;
}

.search-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  gap: 12px;
  align-items: center;
  justify-content: center;
}

.search-input-box {
  width: 100%;
  max-width: 600px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  background-color: #ffffff;
  transition: border-color 0.2s;
}

.search-input-box:focus-within {
  border-color: #333;
}

.search-icon {
  width: 20px;
  height: 20px;
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
  .search-container {
    padding: 12px 16px;
  }

  .search-wrapper {
    gap: 8px;
  }

  .login-btn {
    padding: 8px 16px;
    font-size: 13px;
  }
}
</style>
