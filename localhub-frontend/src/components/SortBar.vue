<script setup lang="ts">
import { ref } from 'vue'

interface Props {
  totalCount: number
}

defineProps<Props>()
const emit = defineEmits<{
  'sort-change': [sort: string]
}>()

const sortOptions = ['최신순', '조회순', '평점높은순']
const selectedSort = ref('최신순')
const isMenuOpen = ref(false)

const handleSortChange = (sort: string) => {
  selectedSort.value = sort
  isMenuOpen.value = false
  emit('sort-change', sort)
}

const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value
}
</script>

<template>
  <div class="sort-bar">
    <div class="sort-wrapper">
      <span class="total-count">총 {{ totalCount }}건</span>

      <div class="sort-dropdown">
        <button class="sort-button" @click="toggleMenu">
          {{ selectedSort }}
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M6 9l6 6 6-6" />
          </svg>
        </button>

        <div v-if="isMenuOpen" class="sort-menu">
          <button
            v-for="option in sortOptions"
            :key="option"
            :class="['sort-option', { active: selectedSort === option }]"
            @click="handleSortChange(option)"
          >
            {{ option }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.sort-bar {
  width: 100%;
  padding: 12px 20px;
  background-color: #ffffff;
  border-bottom: 1px solid #f0f0f0;
}

.sort-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.total-count {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.sort-dropdown {
  position: relative;
}

.sort-button {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  background-color: #ffffff;
  color: #333;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.sort-button:hover {
  border-color: #333;
}

.sort-button svg {
  width: 16px;
  height: 16px;
}

.sort-menu {
  position: absolute;
  top: calc(100% + 4px);
  right: 0;
  background-color: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  min-width: 100px;
  display: flex;
  flex-direction: column;
  z-index: 10;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.sort-option {
  padding: 10px 12px;
  border: none;
  background-color: transparent;
  color: #666;
  font-size: 13px;
  cursor: pointer;
  text-align: right;
  transition: all 0.2s;
}

.sort-option:hover {
  background-color: #f0f0f0;
  color: #333;
}

.sort-option.active {
  color: #333;
  font-weight: 600;
}

@media (max-width: 640px) {
  .sort-bar {
    padding: 10px 16px;
  }

  .total-count {
    font-size: 13px;
  }

  .sort-button {
    padding: 4px 8px;
    font-size: 12px;
  }
}
</style>
