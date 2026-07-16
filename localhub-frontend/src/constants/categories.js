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

// 백엔드 장소 데이터의 카테고리 표기에 맞게 변환한다.
const LOCATION_CATEGORY_OVERRIDES = {
  '축제·행사': '축제공연행사',
}

export function toLocationCategory(category) {
  return LOCATION_CATEGORY_OVERRIDES[category] || category
}

const POST_CATEGORY_OVERRIDES = Object.fromEntries(
  Object.entries(LOCATION_CATEGORY_OVERRIDES).map(([post, location]) => [location, post]),
)

export function toPostCategory(category) {
  return POST_CATEGORY_OVERRIDES[category] || category
}
