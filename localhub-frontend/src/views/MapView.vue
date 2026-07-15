<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import PlaceDetailModal from '@/components/PlaceDetailModal.vue'
import { CATEGORIES } from '@/constants/categories'
import { loadKakaoMaps } from '@/utils/kakaoMap'

// 백엔드 CORS 허용 전까지 실 API(GET /api/locations) 대신 mock 데이터로 표시
const places = ref([
  { content_id: 'map-1', category: '음식점', title: '성심당 본점', addr1: '대전광역시 중구 대종로 480', first_image: '', avg_rating: 4.8, review_count: 1204, lat: 36.3266, lng: 127.4246 },
  { content_id: 'map-2', category: '관광지', title: '대전오월드', addr1: '대전광역시 중구 사정공원로 70', first_image: '', avg_rating: 4.7, review_count: 892, lat: 36.2873, lng: 127.4001 },
  { content_id: 'map-3', category: '문화시설', title: '한밭수목원', addr1: '대전광역시 서구 둔산대로 169', first_image: '', avg_rating: 4.5, review_count: 543, lat: 36.3654, lng: 127.3868 },
  { content_id: 'map-4', category: '관광지', title: '대청호반 자전거길', addr1: '대전광역시 대덕구 대청로 618-136', first_image: '', avg_rating: 4.6, review_count: 376, lat: 36.4744, lng: 127.4815 },
  { content_id: 'map-5', category: '숙박', title: '유성호텔', addr1: '대전광역시 유성구 온천로 76', first_image: '', avg_rating: 4.3, review_count: 210, lat: 36.3546, lng: 127.3413 },
  { content_id: 'map-6', category: '문화시설', title: '국립중앙과학관', addr1: '대전광역시 유성구 대덕대로 481', first_image: '', avg_rating: 4.6, review_count: 802, lat: 36.3745, lng: 127.3742 },
  { content_id: 'map-7', category: '관광지', title: '장태산 휴양림', addr1: '대전광역시 서구 장척로 461', first_image: '', avg_rating: 4.7, review_count: 512, lat: 36.2589, lng: 127.3324 },
  { content_id: 'map-8', category: '음식점', title: '중앙시장 튀김골목', addr1: '대전광역시 동구 중앙로 200', first_image: '', avg_rating: 4.2, review_count: 398, lat: 36.3283, lng: 127.4302 },
  { content_id: 'map-9', category: '레포츠', title: '갑천 자전거길', addr1: '대전광역시 유성구 갑천동로', first_image: '', avg_rating: 4.1, review_count: 164, lat: 36.3612, lng: 127.3556 },
  { content_id: 'map-10', category: '축제·행사', title: '대전 사이언스 페스티벌', addr1: '대전광역시 유성구 대덕대로 480', first_image: '', avg_rating: 4.4, review_count: 190, lat: 36.3745, lng: 127.3845 },
])

const PIN_SVG = `<svg xmlns="http://www.w3.org/2000/svg" width="32" height="40" viewBox="0 0 32 40">
  <path d="M16 0C7.163 0 0 7.163 0 16c0 11 16 24 16 24s16-13 16-24C32 7.163 24.837 0 16 0z" fill="#7e66e2"/>
  <circle cx="16" cy="16" r="6" fill="#fff"/>
</svg>`
const PIN_IMAGE_SRC = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(PIN_SVG)}`

const mapContainer = ref(null)
const loadError = ref('')
const isMapReady = ref(false)

const selectedCategories = ref([])
const selectedPlace = ref(null)
const isPlaceModalOpen = ref(false)

let mapInstance = null
let kakaoRef = null
let clusterer = null
let markers = []

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
  renderMarkers()
}

function openPlace(place) {
  selectedPlace.value = place
  isPlaceModalOpen.value = true
}

function closePlaceModal() {
  isPlaceModalOpen.value = false
}

function handleSelectLocation(source) {
  if (!mapInstance || !kakaoRef || source.lat == null || source.lng == null) return
  mapInstance.panTo(new kakaoRef.maps.LatLng(source.lat, source.lng))
}

function clearMarkers() {
  clusterer?.clear()
  markers = []
}

function renderMarkers() {
  if (!mapInstance || !kakaoRef || !clusterer) return
  clearMarkers()

  const visiblePlaces = selectedCategories.value.length
    ? places.value.filter((place) => selectedCategories.value.includes(place.category))
    : places.value

  if (!visiblePlaces.length) return

  const bounds = new kakaoRef.maps.LatLngBounds()
  const markerImage = new kakaoRef.maps.MarkerImage(
    PIN_IMAGE_SRC,
    new kakaoRef.maps.Size(32, 40),
    { offset: new kakaoRef.maps.Point(16, 40) },
  )

  visiblePlaces.forEach((place) => {
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
    renderMarkers()
  } catch (error) {
    loadError.value = error.message || '지도를 불러오지 못했어요.'
  }
})

onUnmounted(() => {
  clearMarkers()
  clusterer = null
  mapInstance = null
  kakaoRef = null
})
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

    <div class="map-stage">
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

      <p v-if="loadError" class="map-error">{{ loadError }}</p>
      <p v-else-if="!isMapReady" class="map-loading">지도를 불러오는 중...</p>
    </div>

    <PlaceDetailModal
      :place="selectedPlace"
      :open="isPlaceModalOpen"
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

.category-chips.floating {
  position: absolute;
  top: 14px;
  left: 14px;
  right: 14px;
  z-index: 10;
  justify-content: flex-start;
  padding: 9px 10px;
  overflow-x: auto;
  flex-wrap: nowrap;
  background: rgb(255 255 255 / 92%);
  border: 1px solid #e5e3e8;
  border-radius: 999px;
  backdrop-filter: blur(8px);
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
</style>
