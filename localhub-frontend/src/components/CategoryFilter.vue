<script setup lang="ts">
import { ref } from 'vue'

const categories = [
  { id: 1, name: '전체' },
  { id: 2, name: '관광지' },
  { id: 3, name: '레포츠' },
  { id: 4, name: '문화시설' },
  { id: 5, name: '쇼핑' },
  { id: 6, name: '숙박' },
  { id: 7, name: '여행코스' },
  { id: 8, name: '축제행사' }
]

const activeCategory = ref(1)

const selectCategory = (categoryId: number) => {
  activeCategory.value = categoryId
  console.log('선택된 카테고리:', categories.find(c => c.id === categoryId)?.name)
}
</script>

<template>
  <div class="category-container">
    <div class="category-wrapper">
      <button
        v-for="category in categories"
        :key="category.id"
        :class="['category-btn', { active: activeCategory === category.id }]"
        @click="selectCategory(category.id)"
      >
        {{ category.name }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.category-container {
  width: 100%;
  padding: 16px 20px;
  background-color: #ffffff;
  border-bottom: 1px solid #f0f0f0;
}

.category-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.category-btn {
  padding: 8px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 20px;
  background-color: #ffffff;
  color: #666;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.category-btn:hover {
  border-color: #333;
  color: #333;
}

.category-btn.active {
  background-color: #333;
  color: #ffffff;
  border-color: #333;
}

@media (max-width: 640px) {
  .category-container {
    padding: 12px 16px;
  }

  .category-wrapper {
    gap: 6px;
  }

  .category-btn {
    padding: 6px 12px;
    font-size: 13px;
  }
}
</style>
