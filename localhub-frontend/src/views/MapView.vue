<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import PlaceDetailModal from '@/components/PlaceDetailModal.vue'
import { CATEGORIES, toLocationCategory } from '@/constants/categories'
import { getLocation, listAllLocations } from '@/api/locations'
import { loadKakaoMaps } from '@/utils/kakaoMap'

const route = useRoute()
const router = useRouter()

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

// "내 위치" 마커 — 장소 핀과 구분되도록 파란 GPS 점 스타일로 그린다.
const MY_LOCATION_SVG = `<svg xmlns="http://www.w3.org/2000/svg" width="26" height="26" viewBox="0 0 26 26">
  <circle cx="13" cy="13" r="12" fill="#4285f4" fill-opacity="0.22"/>
  <circle cx="13" cy="13" r="6" fill="#4285f4" stroke="#fff" stroke-width="2.5"/>
</svg>`
const MY_LOCATION_IMAGE_SRC = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(MY_LOCATION_SVG)}`

// 잘못된 좌표 한 건이 전체 지도 범위를 한국 밖까지 넓히지 않도록 방어한다.
// 대전여지도 데이터 범위(대전·충청)를 넉넉하게 포함하는 대한민국 영역이다.
const KOREA_COORDINATE_BOUNDS = Object.freeze({
  minLat: 33,
  maxLat: 39,
  minLng: 124,
  maxLng: 132,
})

function getValidCoordinates(place) {
  const lat = Number(place?.lat ?? place?.latitude)
  const lng = Number(place?.lng ?? place?.longitude)
  const isValid =
    Number.isFinite(lat) &&
    Number.isFinite(lng) &&
    lat >= KOREA_COORDINATE_BOUNDS.minLat &&
    lat <= KOREA_COORDINATE_BOUNDS.maxLat &&
    lng >= KOREA_COORDINATE_BOUNDS.minLng &&
    lng <= KOREA_COORDINATE_BOUNDS.maxLng

  return isValid ? { lat, lng } : null
}

const mapContainer = ref(null)
const loadError = ref('')
const isMapReady = ref(false)

const selectedCategories = ref([])
const searchKeyword = ref('')
const selectedPlace = ref(null)
const isPlaceModalOpen = ref(false)
const isRouteFocusActive = ref(false)
const focusedRoutePlace = ref(null)
const isPlaceDetailLoading = ref(false)
const locateError = ref('')
let locateErrorTimer

const visiblePlaces = computed(() => {
  // places는 fetchPlaces()가 이미 선택된 카테고리로 서버에서 걸러 받아온 결과라 여기서는 키워드만 거른다.
  const trimmedKeyword = searchKeyword.value.trim().toLowerCase()
  return places.value.filter((place) => {
    const matchesKeyword =
      !trimmedKeyword ||
      String(place.title || '').toLowerCase().includes(trimmedKeyword) ||
      String(place.addr1 || '').toLowerCase().includes(trimmedKeyword)
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
let myLocationMarker = null

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
  if (isRouteFocusActive.value) {
    // 카테고리를 직접 고르면 단일 장소 포커스에서 빠져나와 전체 목록을 본다.
    router.replace({ name: 'map' })
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
  if (latitude == null || longitude == null) {
    showLocateError('이 장소의 지도 좌표가 올바르지 않아요.')
    return
  }

  // 홈 화면의 장소 모달에서 "지도에서 보기"를 눌렀을 때와 동일하게, 쿼리를 갱신해서
  // 단일 장소 포커스(route-focus) 화면으로 들어가게 한다.
  closePlaceModal()
  const query = {
    id: String(source.id ?? source.content_id ?? ''),
    title: source.title ?? '',
    category: source.category ?? '',
    address: source.address ?? source.addr1 ?? '',
    lat: String(latitude),
    lng: String(longitude),
  }
  if (source.rating != null || source.avg_rating != null) {
    query.rating = String(source.rating ?? source.avg_rating)
  }
  if (source.review_count != null) {
    query.reviews = String(source.review_count)
  }
  if (source.image_url || source.first_image) {
    query.image = source.image_url || source.first_image
  }
  router.push({ name: 'map', query })
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

async function focusRouteLocation() {
  if (!mapInstance || !kakaoRef) return

  highlightedMarker?.setMap(null)
  highlightedMarker = null

  const place = routeLocation()
  if (!place) {
    isRouteFocusActive.value = false
    focusedRoutePlace.value = null
    await nextTick()
    mapInstance.relayout()
    renderMarkers()
    return
  }

  const coordinates = getValidCoordinates(place)
  if (!coordinates) {
    showLocateError('선택한 장소의 지도 좌표가 올바르지 않아요.')
    return
  }

  isRouteFocusActive.value = true
  focusedRoutePlace.value = place
  closePlaceModal()
  clearMarkers()
  await nextTick()
  mapInstance.relayout()

  const position = new kakaoRef.maps.LatLng(coordinates.lat, coordinates.lng)
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
}

async function showAllMarkers() {
  closePlaceModal()
  searchKeyword.value = ''
  selectedCategories.value = []
  await router.replace({ name: 'map' })
  await fetchPlaces()
}

function clearMarkers() {
  clusterer?.clear()
  markers = []
}

function renderMarkers() {
  if (!mapInstance || !kakaoRef || !clusterer || isRouteFocusActive.value) return
  clearMarkers()

  const mappablePlaces = visiblePlaces.value
    .map((place) => ({ place, coordinates: getValidCoordinates(place) }))
    .filter((item) => item.coordinates)

  if (!mappablePlaces.length) return

  const bounds = new kakaoRef.maps.LatLngBounds()
  const markerImage = new kakaoRef.maps.MarkerImage(
    PIN_IMAGE_SRC,
    new kakaoRef.maps.Size(32, 40),
    { offset: new kakaoRef.maps.Point(16, 40) },
  )

  mappablePlaces.forEach(({ place, coordinates }) => {
    const position = new kakaoRef.maps.LatLng(coordinates.lat, coordinates.lng)
    const marker = new kakaoRef.maps.Marker({ position, image: markerImage, title: place.title })
    kakaoRef.maps.event.addListener(marker, 'click', () => openPlace(place))
    markers.push(marker)
    bounds.extend(position)
  })

  clusterer.addMarkers(markers)
  // 가까이 붙어있는 마커는 클러스터로 묶이므로, 항상 보이는 마커 전체에 맞춰 지도 범위를 다시 잡는다.
  if (markers.length === 1) {
    mapInstance.setLevel(5)
    mapInstance.panTo(markers[0].getPosition())
  } else {
    mapInstance.setBounds(bounds)
  }
}

function focusPlace(place) {
  const coordinates = getValidCoordinates(place)
  if (mapInstance && kakaoRef && coordinates) {
    mapInstance.panTo(new kakaoRef.maps.LatLng(coordinates.lat, coordinates.lng))
  } else if (!coordinates) {
    showLocateError('이 장소의 지도 좌표가 올바르지 않아요.')
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
      const here = new kakaoRef.maps.LatLng(position.coords.latitude, position.coords.longitude)
      mapInstance.setLevel(5)
      mapInstance.panTo(here)

      myLocationMarker?.setMap(null)
      const markerImage = new kakaoRef.maps.MarkerImage(
        MY_LOCATION_IMAGE_SRC,
        new kakaoRef.maps.Size(26, 26),
        { offset: new kakaoRef.maps.Point(13, 13) },
      )
      myLocationMarker = new kakaoRef.maps.Marker({
        map: mapInstance,
        position: here,
        image: markerImage,
        title: '내 위치',
        zIndex: 10,
      })
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
    if (routeLocation()) {
      // 특정 장소를 보러 들어온 경우 전체 목록은 불러오지 않고 그 장소만 보여준다.
      await focusRouteLocation()
    } else {
      await fetchPlaces()
    }
  } catch (error) {
    loadError.value = error.message || '지도를 불러오지 못했어요.'
  }
})

onUnmounted(() => {
  clearMarkers()
  highlightedMarker?.setMap(null)
  highlightedMarker = null
  myLocationMarker?.setMap(null)
  myLocationMarker = null
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
      <aside v-if="!isRouteFocusActive" class="map-list-panel">
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
        <form v-if="!isRouteFocusActive" class="map-search floating" @submit.prevent="renderMarkers">
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

        <div v-if="!isRouteFocusActive" class="category-chips floating" aria-label="장소 카테고리 (중복 선택 가능)">
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

        <div v-if="isRouteFocusActive" class="route-focus-panel" role="status">
          <div class="route-focus-copy">
            <span>선택한 장소</span>
            <strong>{{ focusedRoutePlace?.title }}</strong>
          </div>
          <button type="button" @click="showAllMarkers">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="m15 5-7 7 7 7" />
            </svg>
            전체 마커로 돌아가기
          </button>
        </div>

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

.route-focus-panel {
  position: absolute;
  top: 14px;
  left: 50%;
  z-index: 10;
  display: flex;
  width: min(520px, calc(100% - 28px));
  min-height: 58px;
  padding: 9px 10px 9px 14px;
  gap: 12px;
  align-items: center;
  justify-content: space-between;
  background: rgb(255 255 255 / 94%);
  border: 1px solid #dedbe4;
  border-radius: 14px;
  box-shadow: 0 10px 28px rgb(35 32 42 / 14%);
  backdrop-filter: blur(8px);
  transform: translateX(-50%);
}

.route-focus-copy {
  display: flex;
  min-width: 0;
  flex-direction: column;
}

.route-focus-copy span {
  color: #827d88;
  font-size: 10px;
  font-weight: 700;
}

.route-focus-copy strong {
  margin-top: 2px;
  overflow: hidden;
  color: #29272e;
  font-size: 13px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.route-focus-panel button {
  display: inline-flex;
  min-height: 36px;
  padding: 7px 11px;
  gap: 5px;
  color: #fff;
  font: inherit;
  font-size: 11px;
  font-weight: 750;
  white-space: nowrap;
  background: #29272e;
  border: 0;
  border-radius: 9px;
  cursor: pointer;
  align-items: center;
}

.route-focus-panel button:hover {
  background: #7e66e2;
}

.route-focus-panel button svg {
  width: 15px;
  height: 15px;
  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 1.9;
}

.locate-button {
  position: absolute;
  /* map-stage는 position:relative 컨테이너라 여기 right/bottom은 뷰포트가 아니라
     map-stage 기준이다. map-stage 오른쪽/아래쪽 끝은 데스크톱에서 뷰포트의
     콘텐츠 영역 끝과 일치하므로, 챗봇 FAB의 뷰포트 계산식(--chat-fab-right)이
     아니라 그 FAB가 유지하는 순수 여백 상수(--chat-fab-inset)만 재사용해야
     오프셋이 중복 적용되지 않는다. */
  right: calc(var(--chat-fab-inset) + var(--chat-fab-size) + var(--fab-gap));
  bottom: var(--chat-fab-bottom);
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

/* 챗봇 FAB(button.chat-launcher)와 챗봇 패널(section.chat-panel)은 서로 배타적으로
   렌더링된다(v-if="!isOpen" / v-else). 챗봇이 열려 FAB가 사라지면 그만큼 자리를
   비워둘 필요가 없으니, FAB 크기+간격만큼 빼서 모서리에 더 붙인다. */
body:has(.chat-panel) .locate-button {
  right: var(--chat-fab-inset);
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
  width: calc(100% - 28px);
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
  width: calc(100% - 28px);
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

  .route-focus-panel {
    top: 10px;
    width: calc(100% - 20px);
    padding-left: 12px;
    gap: 8px;
  }

  .route-focus-panel button {
    padding: 7px 9px;
    font-size: 10px;
  }

  .locate-button {
    /* 모바일은 챗봇 FAB가 지도 아래 리스트 패널 쪽에 걸쳐 있어서, 챗봇 FAB
       위치/상태와 무관하게 챗봇이 아예 없는 것처럼 기본 위치를 쓴다. */
    right: 14px;
    bottom: 14px;
  }
}
</style>
