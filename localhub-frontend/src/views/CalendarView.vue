<script setup lang="ts">
import { ref, computed } from 'vue'

interface Festival {
  id: number
  name: string
  startDate: string
  endDate: string
  location: string
  category: string
}

const currentDate = ref(new Date(2026, 6)) // 2026년 7월
const selectedDate = ref<Date | null>(null)

const festivals: Festival[] = [
  {
    id: 1,
    name: '대전 문화재 야행',
    startDate: '2026-07-10',
    endDate: '2026-07-12',
    location: '대전광역시',
    category: '문화'
  },
  {
    id: 2,
    name: '세종 호수 음악회',
    startDate: '2026-07-15',
    endDate: '2026-07-15',
    location: '세종시',
    category: '음악'
  },
  {
    id: 3,
    name: '충청도 음식 축제',
    startDate: '2026-07-20',
    endDate: '2026-07-22',
    location: '충청권',
    category: '음식'
  },
  {
    id: 4,
    name: '여름 불빛 축제',
    startDate: '2026-07-25',
    endDate: '2026-07-26',
    location: '대전광역시',
    category: '축제'
  }
]

const monthYear = computed(() => {
  const year = currentDate.value.getFullYear()
  const month = currentDate.value.getMonth() + 1
  return `${year}년 ${month}월`
})

const daysInMonth = computed(() => {
  return new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() + 1, 0).getDate()
})

const firstDayOfMonth = computed(() => {
  return new Date(currentDate.value.getFullYear(), currentDate.value.getMonth(), 1).getDay()
})

const calendarDays = computed(() => {
  const days = []
  for (let i = 0; i < firstDayOfMonth.value; i++) {
    days.push(null)
  }
  for (let i = 1; i <= daysInMonth.value; i++) {
    days.push(i)
  }
  return days
})

const festivalsByDate = computed(() => {
  const map = new Map<string, Festival[]>()
  festivals.forEach(festival => {
    const startDate = new Date(festival.startDate)
    const endDate = new Date(festival.endDate)
    for (let d = new Date(startDate); d <= endDate; d.setDate(d.getDate() + 1)) {
      const dateStr = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
      if (!map.has(dateStr)) {
        map.set(dateStr, [])
      }
      map.get(dateStr)!.push(festival)
    }
  })
  return map
})

const selectedDateFestivals = computed(() => {
  if (!selectedDate.value) return []
  const dateStr = `${selectedDate.value.getFullYear()}-${String(selectedDate.value.getMonth() + 1).padStart(2, '0')}-${String(selectedDate.value.getDate()).padStart(2, '0')}`
  return festivalsByDate.value.get(dateStr) || []
})

const prevMonth = () => {
  currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() - 1)
}

const nextMonth = () => {
  currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() + 1)
}

const selectDate = (day: number | null) => {
  if (day) {
    selectedDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth(), day)
  }
}

const isToday = (day: number | null) => {
  if (!day) return false
  const today = new Date()
  return day === today.getDate() &&
    currentDate.value.getMonth() === today.getMonth() &&
    currentDate.value.getFullYear() === today.getFullYear()
}

const isSelected = (day: number | null) => {
  if (!day || !selectedDate.value) return false
  return day === selectedDate.value.getDate() &&
    currentDate.value.getMonth() === selectedDate.value.getMonth() &&
    currentDate.value.getFullYear() === selectedDate.value.getFullYear()
}

const hasFestival = (day: number | null) => {
  if (!day) return false
  const dateStr = `${currentDate.value.getFullYear()}-${String(currentDate.value.getMonth() + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
  return festivalsByDate.value.has(dateStr)
}
</script>

<template>
  <div class="calendar-page">
    <div class="calendar-header">
      <button class="nav-btn" @click="prevMonth">◀</button>
      <h1 class="month-year">{{ monthYear }}</h1>
      <button class="nav-btn" @click="nextMonth">▶</button>
    </div>

    <div class="calendar-container">
      <div class="weekdays">
        <div class="weekday">일</div>
        <div class="weekday">월</div>
        <div class="weekday">화</div>
        <div class="weekday">수</div>
        <div class="weekday">목</div>
        <div class="weekday">금</div>
        <div class="weekday">토</div>
      </div>

      <div class="calendar-grid">
        <button
          v-for="(day, index) in calendarDays"
          :key="index"
          :class="[
            'calendar-day',
            { empty: !day, today: isToday(day), selected: isSelected(day), 'has-festival': hasFestival(day) }
          ]"
          @click="selectDate(day)"
        >
          <span class="day-number">{{ day }}</span>
          <div v-if="hasFestival(day)" class="festival-indicator"></div>
        </button>
      </div>
    </div>

    <div class="festival-section">
      <h2 class="festival-title">축제 일정</h2>

      <div v-if="selectedDateFestivals.length > 0" class="festival-list">
        <div v-for="festival in selectedDateFestivals" :key="festival.id" class="festival-card">
          <div class="festival-header">
            <h3 class="festival-name">{{ festival.name }}</h3>
            <span class="festival-category">{{ festival.category }}</span>
          </div>
          <div class="festival-info">
            <span class="festival-date">{{ festival.startDate }} ~ {{ festival.endDate }}</span>
            <span class="festival-location">📍 {{ festival.location }}</span>
          </div>
        </div>
      </div>

      <div v-else class="no-festival">
        날짜를 선택하면 축제 정보를 확인할 수 있습니다.
      </div>
    </div>

    <div class="all-festivals">
      <h2 class="all-festivals-title">이번 달 축제</h2>
      <div class="festival-tags">
        <button
          v-for="festival in festivals"
          :key="festival.id"
          class="festival-tag"
          @click="selectDate(new Date(festival.startDate).getDate())"
        >
          {{ festival.name }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.calendar-page {
  width: 100%;
  min-height: 100vh;
  background-color: #ffffff;
  padding: 20px;
}

.calendar-header {
  max-width: 800px;
  margin: 0 auto 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
}

.nav-btn {
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
  font-size: 16px;
  font-weight: 600;
}

.nav-btn:hover {
  color: #666;
}

.month-year {
  font-size: 22px;
  font-weight: 700;
  color: #333;
  margin: 0;
  min-width: 180px;
  text-align: center;
}

.calendar-container {
  max-width: 800px;
  margin: 0 auto 32px;
  background-color: #ffffff;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 0;
  background-color: #f9f9f9;
  border-bottom: 2px solid #e5e7eb;
}

.weekday {
  padding: 14px 8px;
  text-align: center;
  font-size: 12px;
  font-weight: 600;
  color: #333;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 0;
}

.calendar-day {
  position: relative;
  aspect-ratio: 1;
  border: 1px solid #e5e7eb;
  background-color: #ffffff;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  padding: 8px 4px;
  transition: all 0.2s;
  font-size: 0;
}

.calendar-day:hover:not(.empty) {
  background-color: #f9f9f9;
  border-color: #333;
}

.calendar-day.empty {
  background-color: #fafafa;
  cursor: default;
  border-color: #f0f0f0;
}

.calendar-day.today {
  background-color: #ffeaa7;
  border-color: #ffd700;
}

.calendar-day.selected {
  background-color: #333;
  color: #ffffff;
  border-color: #333;
  box-shadow: 0 2px 8px rgba(51, 51, 51, 0.2);
}

.day-number {
  font-size: 13px;
  font-weight: 600;
  color: inherit;
}

.calendar-day.selected .day-number {
  color: #ffffff;
}

.festival-indicator {
  width: 5px;
  height: 5px;
  background-color: #e74c3c;
  border-radius: 50%;
  margin-top: 3px;
}

.calendar-day.selected .festival-indicator {
  background-color: #ffc107;
}

.festival-section {
  max-width: 800px;
  margin: 0 auto 32px;
  padding: 20px;
  background-color: #ffffff;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
}

.festival-title {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin: 0 0 16px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.festival-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.festival-card {
  padding: 16px;
  background-color: #f9f9f9;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  transition: all 0.2s;
  cursor: pointer;
}

.festival-card:hover {
  border-color: #333;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
  background-color: #ffffff;
}

.festival-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;
}

.festival-name {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.festival-category {
  padding: 6px 10px;
  background-color: #333;
  color: #ffffff;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  white-space: nowrap;
}

.festival-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 12px;
  color: #666;
}

.festival-date {
  font-weight: 500;
  color: #333;
}

.no-festival {
  text-align: center;
  padding: 40px 20px;
  color: #999;
  font-size: 14px;
}

.all-festivals {
  max-width: 800px;
  margin: 0 auto;
}

.all-festivals-title {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin: 0 0 16px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.festival-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.festival-tag {
  padding: 8px 14px;
  border: 2px solid #e5e7eb;
  border-radius: 20px;
  background-color: #ffffff;
  color: #333;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.festival-tag:hover {
  border-color: #333;
  background-color: #333;
  color: #ffffff;
}

@media (max-width: 768px) {
  .calendar-page {
    padding: 16px;
  }

  .month-year {
    font-size: 20px;
    min-width: 140px;
  }

  .calendar-header {
    gap: 14px;
    margin-bottom: 20px;
  }

  .festival-tags {
    gap: 6px;
  }

  .festival-tag {
    font-size: 11px;
    padding: 6px 12px;
  }

  .festival-card {
    padding: 14px;
  }
}

@media (max-width: 640px) {
  .calendar-page {
    padding: 12px;
  }

  .month-year {
    font-size: 18px;
    min-width: 120px;
  }

  .calendar-header {
    gap: 12px;
    margin-bottom: 16px;
  }

  .nav-btn {
    width: 28px;
    height: 28px;
    font-size: 14px;
  }

  .day-number {
    font-size: 12px;
  }

  .weekday {
    font-size: 11px;
    padding: 10px 6px;
  }

  .calendar-day {
    padding: 6px 2px;
  }

  .festival-name {
    font-size: 13px;
  }

  .festival-section {
    padding: 16px;
    margin-bottom: 24px;
  }

  .festival-card {
    padding: 12px;
  }

  .festival-title {
    font-size: 13px;
  }

  .all-festivals-title {
    font-size: 13px;
  }
}
</style>
