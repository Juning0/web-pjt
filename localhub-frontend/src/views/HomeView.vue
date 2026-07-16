<script setup>
import { inject, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import PlaceDetailModal from '@/components/PlaceDetailModal.vue'
import { toLocationCategory } from '@/constants/categories'
import { getLocation, listLocations } from '@/api/locations'

const showIntegrationEvent = inject('showIntegrationEvent')
const router = useRouter()
const searchKeyword = ref('')

// 실제 공공데이터(GET /api/locations)를 보여준다. 행사 날짜(start_date/end_date)는
// 원본 데이터에 아예 없어 표시하지 않는다.
const places = ref([])
const trendingPlaces = ref([])
const weeklyEvents = ref([])
const isSectionsLoading = ref(true)

onMounted(async () => {
  try {
    const [recommend, trending, events] = await Promise.all([
      // 최근에 리뷰가 달린 장소부터 — 리뷰가 아직 없으면 자연스럽게 뒤로 밀린다.
      listLocations({ sort: 'recent', size: 3 }),
      // 평점 높은 음식점부터 — 마찬가지로 리뷰 없는 곳은 뒤로 밀린다.
      listLocations({ category: toLocationCategory('음식점'), sort: 'rating', size: 5 }),
      listLocations({ category: toLocationCategory('축제·행사'), size: 4 }),
    ])
    places.value = recommend.items
    trendingPlaces.value = trending.items
    weeklyEvents.value = events.items
  } catch {
    // 홈 화면 추천 섹션은 부가 정보라 실패해도 조용히 비워둔다.
  } finally {
    isSectionsLoading.value = false
  }
})

function searchPlaces() {
  const query = {}
  if (searchKeyword.value.trim()) query.keyword = searchKeyword.value.trim()
  router.push({ path: '/explore', query })
}

const selectedPlace = ref(null)
const isPlaceModalOpen = ref(false)
const isPlaceDetailLoading = ref(false)

async function openPlace(place) {
  isPlaceModalOpen.value = true
  isPlaceDetailLoading.value = true
  selectedPlace.value = null
  try {
    selectedPlace.value = await getLocation(place.content_id)
  } catch {
    selectedPlace.value = place
  } finally {
    isPlaceDetailLoading.value = false
  }
}

function closePlaceModal() {
  isPlaceModalOpen.value = false
}
</script>

<template>
  <main>
    <section id="explore" class="hero-section">
      <p class="eyebrow">대전·충청 여행을 한곳에서</p>
      <h1>오늘은 어디로<br />떠나볼까요?</h1>
      <p class="hero-copy">지역의 장소와 사람들의 생생한 후기를 함께 찾아보세요.</p>
      <form class="search-bar" @submit.prevent="searchPlaces">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <circle cx="11" cy="11" r="6.5" />
          <path d="m16 16 4 4" />
        </svg>
        <input
          v-model="searchKeyword"
          aria-label="찾고 싶은 장소 검색"
          placeholder="찾고 싶은 장소를 검색해 보세요"
        />
        <button type="submit">검색</button>
      </form>
    </section>

    <section id="community" class="community-banner">
      <div class="community-icon" aria-hidden="true">
        <svg viewBox="0 0 24 24">
          <path d="M5.5 6.5h13a2.5 2.5 0 0 1 2.5 2.5v6a2.5 2.5 0 0 1-2.5 2.5H12l-4.5 3v-3h-2A2.5 2.5 0 0 1 3 15V9a2.5 2.5 0 0 1 2.5-2.5Z" />
        </svg>
      </div>
      <div class="community-copy">
        <p class="eyebrow">COMMUNITY</p>
        <h2>직접 다녀온 이야기를 나눠보세요</h2>
        <p>여행 후기와 별점을 남기고, 다른 지역 주민의 추천도 확인할 수 있어요.</p>
      </div>
      <RouterLink to="/board" class="community-link-button">
        커뮤니티 둘러보기 <span aria-hidden="true">→</span>
      </RouterLink>
    </section>

    <section id="trending" class="content-section">
      <div class="section-heading">
        <div>
          <p class="eyebrow">LOCAL FOOD</p>
          <h2>평점 높은 음식점</h2>
        </div>
      </div>
      <div class="event-scroll">
        <template v-if="isSectionsLoading">
          <article v-for="n in 5" :key="`trending-skeleton-${n}`" class="event-card skeleton-card">
            <div class="event-thumb skeleton-shimmer"></div>
            <div class="event-body">
              <div class="skeleton-line title skeleton-shimmer"></div>
              <div class="skeleton-line subtitle skeleton-shimmer"></div>
            </div>
          </article>
        </template>
        <template v-else>
          <article
            v-for="place in trendingPlaces"
            :key="place.content_id"
            class="event-card"
            @click="openPlace(place)"
          >
            <div class="event-thumb">
              <img
                v-if="place.first_image"
                :src="place.first_image"
                :alt="`${place.title} 사진`"
                loading="lazy"
              />
              <div v-else class="no-image" aria-hidden="true">
                <svg viewBox="0 0 24 24">
                  <path d="M4 18V6a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v12H4Zm0-3 4-4 3 3 2-2 5 5M15.5 9a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3Z" />
                </svg>
                <p>이미지가 제공되지 않는 장소입니다.</p>
              </div>
              <span class="event-badge">{{ place.category }}</span>
            </div>
            <div class="event-body">
              <h3>{{ place.title }}</h3>
              <small>{{ place.addr1 }}</small>
            </div>
          </article>
        </template>
      </div>
    </section>

    <section id="recommend" class="content-section">
      <div class="section-heading">
        <div>
          <p class="eyebrow">LOCAL PICK</p>
          <h2>지금 둘러보기 좋은 장소</h2>
        </div>
        <button type="button" @click="router.push('/explore')">
          전체 보기 <span aria-hidden="true">→</span>
        </button>
      </div>
      <div class="event-scroll">
        <template v-if="isSectionsLoading">
          <article v-for="n in 3" :key="`recommend-skeleton-${n}`" class="event-card skeleton-card">
            <div class="event-thumb skeleton-shimmer"></div>
            <div class="event-body">
              <div class="skeleton-line title skeleton-shimmer"></div>
              <div class="skeleton-line subtitle skeleton-shimmer"></div>
            </div>
          </article>
        </template>
        <template v-else>
          <article
            v-for="place in places"
            :key="place.content_id"
            class="event-card"
            @click="openPlace(place)"
          >
            <div class="event-thumb">
              <img
                v-if="place.first_image"
                :src="place.first_image"
                :alt="`${place.title} 사진`"
                loading="lazy"
              />
              <div v-else class="no-image" aria-hidden="true">
                <svg viewBox="0 0 24 24">
                  <path d="M4 18V6a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v12H4Zm0-3 4-4 3 3 2-2 5 5M15.5 9a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3Z" />
                </svg>
                <p>이미지가 제공되지 않는 장소입니다.</p>
              </div>
              <span class="event-badge">{{ place.category }}</span>
            </div>
            <div class="event-body">
              <h3>{{ place.title }}</h3>
              <small>{{ place.addr1 }}</small>
            </div>
          </article>
        </template>
      </div>
    </section>

    <section id="events" class="content-section">
      <div class="section-heading">
        <div>
          <p class="eyebrow">LOCAL EVENTS</p>
          <h2>지역 축제·행사</h2>
        </div>
      </div>
      <div class="event-scroll">
        <template v-if="isSectionsLoading">
          <article v-for="n in 4" :key="`events-skeleton-${n}`" class="event-card skeleton-card">
            <div class="event-thumb skeleton-shimmer"></div>
            <div class="event-body">
              <div class="skeleton-line title skeleton-shimmer"></div>
              <div class="skeleton-line subtitle skeleton-shimmer"></div>
            </div>
          </article>
        </template>
        <template v-else>
          <article
            v-for="event in weeklyEvents"
            :key="event.content_id"
            class="event-card"
            @click="openPlace(event)"
          >
            <div class="event-thumb">
              <img
                v-if="event.first_image"
                :src="event.first_image"
                :alt="`${event.title} 사진`"
                loading="lazy"
              />
              <div v-else class="no-image" aria-hidden="true">
                <svg viewBox="0 0 24 24">
                  <path d="M4 18V6a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v12H4Zm0-3 4-4 3 3 2-2 5 5M15.5 9a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3Z" />
                </svg>
                <p>이미지가 제공되지 않는 장소입니다.</p>
              </div>
              <span class="event-badge">{{ event.category }}</span>
            </div>
            <div class="event-body">
              <h3>{{ event.title }}</h3>
              <small>{{ event.addr1 }}</small>
            </div>
          </article>
        </template>
      </div>
    </section>

  </main>

  <PlaceDetailModal
    :place="selectedPlace"
    :open="isPlaceModalOpen"
    :loading="isPlaceDetailLoading"
    @close="closePlaceModal"
    @select-location="showIntegrationEvent"
  />
</template>
