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

const POST_CATEGORY_BY_LOCATION_CATEGORY = Object.fromEntries(
  Object.entries(LOCATION_CATEGORY_OVERRIDES).map(([postCategory, locationCategory]) => [
    locationCategory,
    postCategory,
  ]),
)

// 장소(Location)의 카테고리 값을 게시글 카테고리 표기로 되돌린다. 글쓰기 시 장소를 고르면
// 그 장소의 카테고리를 그대로 게시글 카테고리로 써야 하기 때문에 필요하다.
export function toPostCategory(locationCategory) {
  return POST_CATEGORY_BY_LOCATION_CATEGORY[locationCategory] || locationCategory
}
