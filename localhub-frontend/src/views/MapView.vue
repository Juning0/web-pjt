<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import PlaceDetailModal from '@/components/PlaceDetailModal.vue'
import { CATEGORIES, toLocationCategory } from '@/constants/categories'
import { getLocation, listAllLocations } from '@/api/locations'
import { loadKakaoMaps } from '@/utils/kakaoMap'

const route = useRoute()

const places = ref([])
const isPlacesLoading = ref(false)
const placesError = ref('')

// 카테고리 다중 선택 시 카테고리별로 나눠 조회한 뒤 합친다(백엔드는 카테고리 단일 필터만 지원).
async function fetchPlaces() {
  isPlacesLoading.value = true
  placesError.value = ''
  try {
    const categories = selectedCategories.value.length ? selectedCategories.value : [undefined]
    const lists = await Promise.all(
      categories.map((category) =>
        listAllLocations({ category: category ? toLocationCategory(category) : undefined }),
      ),
    )
    const merged = new Map()
    lists.flat().forEach((item) => merged.set(item.content_id, item))
    places.value = Array.from(merged.values())
  } catch (error) {
    placesError.value = error.message || '장소를 불러오지 못했어요.'
  } finally {
    isPlacesLoading.value = false
  }
  renderMarkers()
}

const PIN_SVG = `<svg xmlns="http://www.w3.org/2000/svg" width="32" height="40" viewBox="0 0 32 40">
  <path d="M16 0C7.163 0 0 7.163 0 16c0 11 16 24 16 24s16-13 16-24C32 7.163 24.837 0 16 0z" fill="#7e66e2"/>
  <circle cx="16" cy="16" r="6" fill="#fff"/>
</svg>`
const PIN_IMAGE_SRC = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(PIN_SVG)}`

const mapContainer = ref(null)
const loadError = ref('')
const isMapReady = ref(false)

const selectedCategories = ref([])
const searchKeyword = ref('')
const selectedPlace = ref(null)
const isPlaceModalOpen = ref(false)
const isPlaceDetailLoading = ref(false)
const locateError = ref('')
let locateErrorTimer

const visiblePlaces = computed(() => {
  // places는 fetchPlaces()가 이미 선택된 카테고리로 서버에서 걸러 받아온 결과라 여기서는 키워드만 거른다.
  const trimmedKeyword = searchKeyword.value.trim().toLowerCase()
  return places.value.filter((place) => {
    const matchesKeyword =
      !trimmedKeyword ||
      place.title.toLowerCase().includes(trimmedKeyword) ||
      place.addr1.toLowerCase().includes(trimmedKeyword)
    return matchesKeyword
  })
})

function clearSearch() {
  searchKeyword.value = ''
  renderMarkers()
}

let mapInstance = null
let kakaoRef = null
let clusterer = null
let markers = []
let highlightedMarker = null

function isCategoryActive(category) {
  if (category === '전체') return selectedCategories.value.length === 0
  return selectedCategories.value.includes(category)
}

function toggleCategory(category) {
  if (category === '전체') {
    selectedCategories.value = []
  } else {
    selectedCategories.value = isCategoryActive(category)
      ? selectedCategories.value.filter((item) => item !== category)
      : [...selectedCategories.value, category]
  }
  fetchPlaces()
}

async function openPlace(place) {
  isPlaceModalOpen.value = true
  isPlaceDetailLoading.value = true
  selectedPlace.value = null
  try {
    selectedPlace.value = await getLocation(place.content_id)
  } catch {
    // 상세 조회에 실패해도 목록 데이터로는 계속 보여준다.
    selectedPlace.value = place
  } finally {
    isPlaceDetailLoading.value = false
  }
}

function closePlaceModal() {
  isPlaceModalOpen.value = false
}

function handleSelectLocation(source) {
  const latitude = source.latitude ?? source.lat
  const longitude = source.longitude ?? source.lng
  if (!mapInstance || !kakaoRef || latitude == null || longitude == null) return
  mapInstance.panTo(new kakaoRef.maps.LatLng(latitude, longitude))
}

function firstQueryValue(value) {
  return Array.isArray(value) ? value[0] : value
}

function routeLocation() {
  const latitude = Number(firstQueryValue(route.query.lat))
  const longitude = Number(firstQueryValue(route.query.lng))
  const title = firstQueryValue(route.query.title)
  if (!title || !Number.isFinite(latitude) || !Number.isFinite(longitude)) return null

  const ratingValue = Number(firstQueryValue(route.query.rating))
  const reviewValue = Number(firstQueryValue(route.query.reviews))
  return {
    content_id: firstQueryValue(route.query.id) || `chat-${latitude}-${longitude}`,
    title,
    category: firstQueryValue(route.query.category) || '장소',
    addr1: firstQueryValue(route.query.address) || '',
    first_image: firstQueryValue(route.query.image) || '',
    avg_rating: Number.isFinite(ratingValue) ? ratingValue : null,
    review_count: Number.isFinite(reviewValue) ? reviewValue : 0,
    lat: latitude,
    lng: longitude,
  }
}

function focusRouteLocation() {
  if (!mapInstance || !kakaoRef) return
  highlightedMarker?.setMap(null)
  highlightedMarker = null

  const place = routeLocation()
  if (!place) return

  const position = new kakaoRef.maps.LatLng(place.lat, place.lng)
  const markerImage = new kakaoRef.maps.MarkerImage(
    PIN_IMAGE_SRC,
    new kakaoRef.maps.Size(32, 40),
    { offset: new kakaoRef.maps.Point(16, 40) },
  )
  highlightedMarker = new kakaoRef.maps.Marker({
    map: mapInstance,
    position,
    image: markerImage,
    title: place.title,
  })
  kakaoRef.maps.event.addListener(highlightedMarker, 'click', () => openPlace(place))
  mapInstance.setLevel(4)
  mapInstance.panTo(position)
  openPlace(place)
}

function clearMarkers() {
  clusterer?.clear()
  markers = []
}

function renderMarkers() {
  if (!mapInstance || !kakaoRef || !clusterer) return
  clearMarkers()

  if (!visiblePlaces.value.length) return

  const bounds = new kakaoRef.maps.LatLngBounds()
  const markerImage = new kakaoRef.maps.MarkerImage(
    PIN_IMAGE_SRC,
    new kakaoRef.maps.Size(32, 40),
    { offset: new kakaoRef.maps.Point(16, 40) },
  )

  visiblePlaces.value.forEach((place) => {
    const position = new kakaoRef.maps.LatLng(place.lat, place.lng)
    const marker = new kakaoRef.maps.Marker({ position, image: markerImage, title: place.title })
    kakaoRef.maps.event.addListener(marker, 'click', () => openPlace(place))
    markers.push(marker)
    bounds.extend(position)
  })

  clusterer.addMarkers(markers)
  // 가까이 붙어있는 마커는 클러스터로 묶이므로, 항상 보이는 마커 전체에 맞춰 지도 범위를 다시 잡는다.
  mapInstance.setBounds(bounds)
}

function focusPlace(place) {
  if (mapInstance && kakaoRef) {
    mapInstance.panTo(new kakaoRef.maps.LatLng(place.lat, place.lng))
  }
  openPlace(place)
}

function showLocateError(message) {
  locateError.value = message
  window.clearTimeout(locateErrorTimer)
  locateErrorTimer = window.setTimeout(() => {
    locateError.value = ''
  }, 2600)
}

function locateMe() {
  if (!navigator.geolocation) {
    showLocateError('이 브라우저는 위치 정보를 지원하지 않아요.')
    return
  }
  navigator.geolocation.getCurrentPosition(
    (position) => {
      if (!mapInstance || !kakaoRef) return
      mapInstance.setLevel(5)
      mapInstance.panTo(
        new kakaoRef.maps.LatLng(position.coords.latitude, position.coords.longitude),
      )
    },
    () => {
      showLocateError('위치 정보를 가져오지 못했어요. 권한을 확인해 주세요.')
    },
  )
}

onMounted(async () => {
  try {
    const kakao = await loadKakaoMaps()
    kakaoRef = kakao
    mapInstance = new kakao.maps.Map(mapContainer.value, {
      center: new kakao.maps.LatLng(36.3504, 127.3845),
      level: 8,
    })
    clusterer = new kakao.maps.MarkerClusterer({
      map: mapInstance,
      averageCenter: true,
      minLevel: 6,
      styles: [
        {
          width: '40px',
          height: '40px',
          background: 'rgba(126, 102, 226, 0.88)',
          borderRadius: '50%',
          color: '#fff',
          textAlign: 'center',
          lineHeight: '40px',
          fontWeight: 'bold',
          fontSize: '13px',
        },
      ],
    })
    isMapReady.value = true
    await fetchPlaces()
    focusRouteLocation()
  } catch (error) {
    loadError.value = error.message || '지도를 불러오지 못했어요.'
  }
})

onUnmounted(() => {
  clearMarkers()
  highlightedMarker?.setMap(null)
  highlightedMarker = null
  clusterer = null
  mapInstance = null
  kakaoRef = null
})

watch(
  () => route.query,
  () => focusRouteLocation(),
  { deep: true },
)
</script>

<template>
  <div class="map-page">
    <header class="map-topbar">
      <RouterLink to="/" class="icon-button" aria-label="뒤로가기">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="m15 5-7 7 7 7" />
        </svg>
      </RouterLink>
      <h1>지도로 보기</h1>
      <span class="header-spacer" aria-hidden="true"></span>
    </header>

    <div class="map-body">
      <aside class="map-list-panel">
        <div class="map-list-controls">
          <form class="map-search sidebar-search" @submit.prevent="renderMarkers">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <circle cx="11" cy="11" r="6.5" />
              <path d="m16 16 4 4" />
            </svg>
            <input
              v-model="searchKeyword"
              type="search"
              placeholder="장소명 또는 주소를 검색해 보세요"
              aria-label="지도 장소 검색"
              @input="renderMarkers"
            />
            <button
              v-if="searchKeyword"
              type="button"
              class="map-search-clear"
              aria-label="검색어 지우기"
              @click="clearSearch"
            >
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="m6 6 12 12M18 6 6 18" />
              </svg>
            </button>
          </form>

          <div class="category-chips sidebar-chips" aria-label="장소 카테고리 (중복 선택 가능)">
            <button
              type="button"
              :class="{ active: isCategoryActive('전체') }"
              @click="toggleCategory('전체')"
            >
              전체
            </button>
            <button
              v-for="category in CATEGORIES"
              :key="category"
              type="button"
              :class="{ active: isCategoryActive(category) }"
              :aria-pressed="isCategoryActive(category)"
              @click="toggleCategory(category)"
            >
              {{ category }}
            </button>
          </div>
        </div>

        <div class="map-list-header">총 {{ visiblePlaces.length }}곳</div>
        <p v-if="isPlacesLoading" class="map-list-empty">장소를 불러오는 중...</p>
        <p v-else-if="placesError" class="map-list-empty">{{ placesError }}</p>
        <ul v-else-if="visiblePlaces.length" class="map-list">
          <li v-for="place in visiblePlaces" :key="place.content_id" @click="focusPlace(place)">
            <span class="map-list-category">{{ place.category }}</span>
            <h3>{{ place.title }}</h3>
            <p class="map-list-rating">{{ place.addr1 }}</p>
          </li>
        </ul>
        <p v-else class="map-list-empty">조건에 맞는 장소가 없어요.</p>
      </aside>

      <div class="map-stage">
        <form class="map-search floating" @submit.prevent="renderMarkers">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <circle cx="11" cy="11" r="6.5" />
            <path d="m16 16 4 4" />
          </svg>
          <input
            v-model="searchKeyword"
            type="search"
            placeholder="장소명 또는 주소를 검색해 보세요"
            aria-label="지도 장소 검색"
            @input="renderMarkers"
          />
          <button
            v-if="searchKeyword"
            type="button"
            class="map-search-clear"
            aria-label="검색어 지우기"
            @click="clearSearch"
          >
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="m6 6 12 12M18 6 6 18" />
            </svg>
          </button>
        </form>

        <div class="category-chips floating" aria-label="장소 카테고리 (중복 선택 가능)">
          <button
            type="button"
            :class="{ active: isCategoryActive('전체') }"
            @click="toggleCategory('전체')"
          >
            전체
          </button>
          <button
            v-for="category in CATEGORIES"
            :key="category"
            type="button"
            :class="{ active: isCategoryActive(category) }"
            :aria-pressed="isCategoryActive(category)"
            @click="toggleCategory(category)"
          >
            {{ category }}
          </button>
        </div>

        <div ref="mapContainer" class="map-container"></div>

        <button class="locate-button" type="button" aria-label="내 위치로 이동" @click="locateMe">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <circle cx="12" cy="12" r="3" />
            <path d="M12 2v3M12 19v3M2 12h3M19 12h3" />
          </svg>
        </button>

        <p v-if="locateError" class="map-toast">{{ locateError }}</p>
        <p v-if="loadError" class="map-error">{{ loadError }}</p>
        <p v-else-if="!isMapReady" class="map-loading">지도를 불러오는 중...</p>
      </div>
    </div>

    <PlaceDetailModal
      :place="selectedPlace"
      :open="isPlaceModalOpen"
      :loading="isPlaceDetailLoading"
      @close="closePlaceModal"
      @select-location="handleSelectLocation"
    />
  </div>
</template>

<style scoped>
.map-page {
  display: flex;
  height: calc(100dvh - 68px);
  flex-direction: column;
}

.map-topbar {
  display: flex;
  min-height: 52px;
  padding: 8px 14px;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid #e9e7eb;
}

.map-topbar h1 {
  margin: 0;
  color: #29272e;
  font-size: 17px;
  font-weight: 780;
  flex: 1;
  text-align: center;
}

.header-spacer {
  width: 38px;
}

.icon-button {
  display: grid;
  width: 38px;
  height: 38px;
  padding: 0;
  color: #29272e;
  background: transparent;
  border: 0;
  border-radius: 8px;
  cursor: pointer;
  place-items: center;
}

.icon-button:hover {
  background: #f4f2f7;
}

.icon-button svg {
  width: 20px;
  height: 20px;
  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 1.8;
}

.map-body {
  display: flex;
  flex: 1;
  min-height: 0;
}

.map-list-panel {
  display: flex;
  width: 300px;
  flex: 0 0 300px;
  overflow-y: auto;
  border-right: 1px solid #e9e7eb;
  flex-direction: column;
}

.map-list-header {
  padding: 14px 16px 10px;
  color: #56515d;
  font-size: 12.5px;
  font-weight: 700;
}

.map-list {
  display: flex;
  padding: 0;
  margin: 0;
  list-style: none;
  flex-direction: column;
}

.map-list li {
  padding: 12px 16px;
  cursor: pointer;
  border-top: 1px solid #f0eef2;
}

.map-list li:hover {
  background: #faf9fc;
}

.map-list-category {
  display: inline-block;
  padding: 3px 9px;
  color: #7e66e2;
  font-size: 10px;
  font-weight: 750;
  background: #f1edff;
  border-radius: 999px;
}

.map-list h3 {
  margin: 6px 0 0;
  overflow: hidden;
  color: #29272e;
  font-size: 13.5px;
  font-weight: 750;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.map-list-rating {
  margin: 4px 0 0;
  overflow: hidden;
  color: #77727c;
  font-size: 11px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.map-list-empty {
  padding: 28px 16px;
  color: #9b97a0;
  font-size: 12px;
  text-align: center;
}

.map-stage {
  position: relative;
  flex: 1;
  min-height: 0;
}

.map-container {
  width: 100%;
  height: 100%;
  background: #f4f2f7;
}

.locate-button {
  position: absolute;
  right: 14px;
  bottom: 14px;
  z-index: 10;
  display: grid;
  width: 42px;
  height: 42px;
  padding: 0;
  color: #29272e;
  background: #fff;
  border: 1px solid #e5e3e8;
  border-radius: 50%;
  cursor: pointer;
  box-shadow: 0 8px 18px rgb(35 32 42 / 14%);
  place-items: center;
}

.locate-button:hover {
  color: #7e66e2;
}

.locate-button svg {
  width: 20px;
  height: 20px;
  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 1.8;
}

.map-toast {
  position: absolute;
  left: 50%;
  bottom: 66px;
  z-index: 10;
  margin: 0;
  padding: 8px 14px;
  color: #fff;
  font-size: 11.5px;
  background: #29272e;
  border-radius: 999px;
  white-space: nowrap;
  transform: translateX(-50%);
}

.map-list-controls {
  display: flex;
  padding: 14px 16px 4px;
  gap: 10px;
  flex-direction: column;
}

.map-search.sidebar-search {
  position: static;
  width: 100%;
}

.category-chips.sidebar-chips {
  position: static;
  width: 100%;
  justify-content: flex-start;
}

/* 데스크톱은 리스트 패널 상단에 검색·필터를 두고, 지도 위 플로팅 버전은 모바일에서만 보여준다. */
.map-search.floating,
.category-chips.floating {
  display: none;
}

.map-search {
  position: absolute;
  top: 14px;
  left: 14px;
  z-index: 10;
  display: flex;
  width: min(420px, calc(100% - 28px));
  min-height: 46px;
  padding: 0 16px;
  gap: 9px;
  align-items: center;
  background: rgb(255 255 255 / 92%);
  border: 1px solid #e5e3e8;
  border-radius: 999px;
  backdrop-filter: blur(8px);
}

.map-search svg:first-child {
  width: 18px;
  height: 18px;
  color: #85818b;
  flex: 0 0 auto;
  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-width: 1.8;
}

.map-search input {
  min-width: 0;
  flex: 1;
  color: #29272e;
  font: inherit;
  font-size: 13px;
  background: transparent;
  border: 0;
  outline: 0;
}

.map-search input::placeholder {
  color: #a19da6;
}

.map-search input::-webkit-search-cancel-button {
  display: none;
}

.map-search-clear {
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

.map-search-clear svg {
  width: 16px;
  height: 16px;
  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-width: 1.8;
}

.category-chips.floating {
  position: absolute;
  top: 70px;
  left: 14px;
  z-index: 10;
  justify-content: flex-start;
  width: min(420px, calc(100% - 28px));
  padding: 9px 10px;
  overflow-x: auto;
  flex-wrap: nowrap;
  background: rgb(255 255 255 / 92%);
  border: 1px solid #e5e3e8;
  border-radius: 999px;
  backdrop-filter: blur(8px);
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.category-chips.floating::-webkit-scrollbar {
  display: none;
}

.category-chips.floating button {
  flex: 0 0 auto;
  white-space: nowrap;
}

.category-chips.floating::after {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  width: 30px;
  content: '';
  background: linear-gradient(to right, transparent, rgb(255 255 255 / 85%) 70%);
  border-radius: 0 999px 999px 0;
  pointer-events: none;
}

.map-error,
.map-loading {
  position: absolute;
  top: 50%;
  left: 50%;
  z-index: 5;
  margin: 0;
  padding: 10px 16px;
  color: #56515d;
  font-size: 12.5px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 8px 20px rgb(35 32 42 / 12%);
  transform: translate(-50%, -50%);
  white-space: nowrap;
}

.map-error {
  color: #9b2f2f;
}

@media (max-width: 760px) {
  .map-body {
    flex-direction: column;
  }

  .map-list-panel {
    order: 2;
    width: 100%;
    height: 34vh;
    flex: 0 0 auto;
    border-top: 1px solid #e9e7eb;
    border-right: 0;
  }

  .map-stage {
    order: 1;
    min-height: 200px;
  }

  .map-list-controls {
    display: none;
  }

  .map-search.floating,
  .category-chips.floating {
    display: flex;
  }
}
</style>
