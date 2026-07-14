<script setup lang="ts">
const trendingSearches = [
  { rank: 1, keyword: '성심당' },
  { rank: 2, keyword: '계족산' },
  { rank: 3, keyword: '어르숨제' }
]

const upcomingEvents = [
  {
    id: 1,
    title: '대전 사이언스페스티벌',
    dateRange: '7.18 ~ 7.20'
  },
  {
    id: 2,
    title: '보령 머드축제',
    dateRange: '7.25 ~ 8.10'
  }
]
</script>

<template>
  <div class="side-panel">
    <!-- Trending Searches -->
    <div class="panel-section">
      <div class="section-header">
        <span class="fire-icon">🔥</span>
        <h3 class="section-title">실시간 인기 검색</h3>
      </div>
      <div class="trending-list">
        <div v-for="search in trendingSearches" :key="search.rank" class="trending-item">
          <span class="rank-badge">{{ search.rank }}</span>
          <span class="keyword">{{ search.keyword }}</span>
        </div>
      </div>
    </div>

    <!-- Upcoming Events -->
    <div class="panel-section">
      <div class="section-header">
        <span class="calendar-icon">📅</span>
        <h3 class="section-title">이번 주 축제/행사</h3>
      </div>
      <div class="events-list">
        <div v-for="event in upcomingEvents" :key="event.id" class="event-item">
          <h4 class="event-title">{{ event.title }}</h4>
          <p class="event-date">{{ event.dateRange }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.side-panel {
  display: flex;
  flex-direction: row;
  gap: 20px;
}

.panel-section {
  background-color: #ffffff;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  padding: 16px;
  flex: 1;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.fire-icon,
.calendar-icon {
  font-size: 18px;
}

.section-title {
  margin: 0;
  font-size: 14px;
  font-weight: 700;
  color: #333;
}

.trending-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.trending-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 0;
  font-size: 13px;
}

.rank-badge {
  min-width: 20px;
  height: 20px;
  background-color: #333;
  color: #ffffff;
  border-radius: 3px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 12px;
}

.keyword {
  color: #666;
  cursor: pointer;
  transition: color 0.2s;
}

.keyword:hover {
  color: #333;
}

.events-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.event-item {
  padding: 12px;
  background-color: #f9f9f9;
  border-radius: 8px;
  border-left: 3px solid #333;
}

.event-title {
  margin: 0 0 6px 0;
  font-size: 13px;
  font-weight: 600;
  color: #333;
  line-height: 1.3;
}

.event-date {
  margin: 0;
  font-size: 12px;
  color: #999;
}
</style>
