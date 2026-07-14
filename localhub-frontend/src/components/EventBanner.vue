<script setup lang="ts">
import { ref } from 'vue'

const bannerIndex = ref(0)

const banners = [
  { id: 1, title: '페스티벌 배너' },
  { id: 2, title: '이벤트 배너' },
  { id: 3, title: '프로모션 배너' }
]

const nextBanner = () => {
  bannerIndex.value = (bannerIndex.value + 1) % banners.length
}

const prevBanner = () => {
  bannerIndex.value = (bannerIndex.value - 1 + banners.length) % banners.length
}

const goToBanner = (index: number) => {
  bannerIndex.value = index
}
</script>

<template>
  <div class="banner-container">
    <div class="banner-wrapper">
      <div class="banner-slide">
        <div class="banner-content">
          {{ banners[bannerIndex].title }}
        </div>
      </div>

      <button class="banner-btn prev-btn" @click="prevBanner">❮</button>
      <button class="banner-btn next-btn" @click="nextBanner">❯</button>

      <div class="banner-dots">
        <button
          v-for="(banner, index) in banners"
          :key="banner.id"
          :class="['dot', { active: bannerIndex === index }]"
          @click="goToBanner(index)"
          :aria-label="`배너 ${index + 1}`"
        ></button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.banner-container {
  width: 100%;
  padding: 16px 20px;
  background-color: #ffffff;
}

.banner-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
  border-radius: 12px;
  overflow: hidden;
}

.banner-slide {
  width: 100%;
  aspect-ratio: 16 / 5;
  background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.banner-content {
  color: #999;
  font-size: 18px;
  font-weight: 500;
}

.banner-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 40px;
  height: 40px;
  border: none;
  background-color: rgba(0, 0, 0, 0.5);
  color: white;
  font-size: 20px;
  cursor: pointer;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
  z-index: 2;
}

.banner-btn:hover {
  background-color: rgba(0, 0, 0, 0.7);
}

.prev-btn {
  left: 10px;
}

.next-btn {
  right: 10px;
}

.banner-dots {
  position: absolute;
  bottom: 12px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 8px;
  z-index: 2;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  border: none;
  background-color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition: all 0.2s;
}

.dot:hover {
  background-color: rgba(255, 255, 255, 0.8);
}

.dot.active {
  background-color: rgba(255, 255, 255, 1);
  transform: scale(1.2);
}

@media (max-width: 640px) {
  .banner-container {
    padding: 12px 16px;
  }

  .banner-slide {
    aspect-ratio: 3 / 2;
  }

  .banner-content {
    font-size: 16px;
  }

  .banner-btn {
    width: 32px;
    height: 32px;
    font-size: 16px;
  }

  .prev-btn {
    left: 8px;
  }

  .next-btn {
    right: 8px;
  }
}
</style>
