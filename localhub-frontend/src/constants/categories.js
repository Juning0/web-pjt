export const CATEGORIES = [
  '관광지',
  '문화시설',
  '축제·행사',
  '여행코스',
  '레포츠',
  '숙박',
  '쇼핑',
  '음식점',
]

// 백엔드 공공데이터(GET /api/locations)의 카테고리 값은 구분자가 없어 지도 검색 시에만 변환한다.
const LOCATION_CATEGORY_OVERRIDES = {
  '축제·행사': '축제공연행사',
}

export function toLocationCategory(category) {
  return LOCATION_CATEGORY_OVERRIDES[category] || category
}
