import asyncio
import json
import re
from pathlib import Path
from typing import Any

from sqlalchemy.exc import SQLAlchemyError

from app import crud
from app.database import SessionLocal


CATEGORY_KEYWORDS: dict[str, tuple[str, ...]] = {
    "관광지": (
        "관광지",
        "명소",
        "가볼만한",
        "갈만한",
        "볼거리",
        "여행지",
        "나들이",
        "아이랑",
        "가족여행",
        "데이트코스",
        "데이트",
        "연인",
        "커플",
    ),
    "레포츠": (
        "레포츠",
        "체험",
        "액티비티",
        "스포츠",
        "운동",
        "캠핑",
        "글램핑",
        "등산",
        "자전거",
        "수상레저",
        "골프",
    ),
    "문화시설": (
        "문화시설",
        "박물관",
        "미술관",
        "전시",
        "공연장",
        "도서관",
        "과학관",
        "기념관",
    ),
    "쇼핑": (
        "쇼핑",
        "시장",
        "백화점",
        "상점",
        "기념품",
        "쇼핑몰",
        "전통시장",
        "특산물",
        "장보기",
    ),
    "숙박": (
        "숙박",
        "숙소",
        "호텔",
        "모텔",
        "펜션",
        "게스트하우스",
        "리조트",
        "민박",
        "한옥스테이",
        "잘곳",
        "잘 곳",
        "잠잘",
        "묵을",
        "머물",
        "하룻밤",
        "하루 묵",
        "묵고",
        "묵다",
        "머물고",
        "머무를",
        "자고",
        "자는 곳",
        "잘래",
        "잘 만한",
        "호캉스",
    ),
    "여행코스": (
        "여행코스",
        "여행 코스",
        "코스",
        "동선",
        "당일치기",
        "1박2일",
        "여행계획",
        "여행 계획",
        "여행일정",
        "여행 일정",
        "일정 짜",
        "코스 짜",
    ),
    "음식점": (
        "음식점",
        "맛집",
        "식당",
        "먹거리",
        "모범음식점",
        "카페",
        "밥집",
        "밥 먹을",
        "밥먹을",
        "식사",
        "먹을곳",
        "먹을 곳",
        "빵집",
        "디저트",
        "브런치",
        "커피",
        "먹고",
        "먹지",
        "뭐먹",
        "뭐 먹",
    ),
    "축제공연행사": ("축제", "공연", "행사", "페스티벌", "이벤트", "콘서트"),
}

# 이 단어들은 카테고리 판별에도 쓰지만, 제목에 포함되면 더 정확한 결과가 되므로
# 검색 토큰에서는 제거하지 않습니다. 예: "카페"가 음식점 전체로 퍼지지 않도록 함.
SEARCHABLE_CATEGORY_TERMS = {
    "캠핑",
    "글램핑",
    "등산",
    "자전거",
    "수상레저",
    "골프",
    "박물관",
    "미술관",
    "공연장",
    "도서관",
    "과학관",
    "기념관",
    "시장",
    "백화점",
    "기념품",
    "쇼핑몰",
    "전통시장",
    "특산물",
    "호텔",
    "모텔",
    "펜션",
    "게스트하우스",
    "리조트",
    "민박",
    "한옥스테이",
    "카페",
    "빵집",
    "디저트",
    "브런치",
    "커피",
    "축제",
    "공연",
    "행사",
    "페스티벌",
    "콘서트",
}

REGION_ALIASES: dict[str, tuple[str, ...]] = {
    "대전": ("대전광역시", "대전시", "대전"),
    "세종": ("세종특별자치시", "세종시", "세종"),
    "계룡": ("계룡시", "계룡"),
    "공주": ("공주시", "공주"),
    "논산": ("논산시", "논산"),
    "옥천": ("옥천군", "옥천"),
    "충청남도": ("충청남도", "충남"),
    "충청북도": ("충청북도", "충북"),
}
REGION_KEYWORDS = tuple(REGION_ALIASES)
AREA_CODE_REGIONS = {"3": "대전", "8": "세종", "33": "충청북도", "34": "충청남도"}

POST_MARKERS = ("게시글", "게시 글", "커뮤니티", "후기", "리뷰", "글 검색", "작성글")
RATING_MARKERS = (
    "평점",
    "별점",
    "리뷰 많은",
    "후기 많은",
    "리뷰순",
    "후기순",
    "리뷰 좋은",
    "후기 좋은",
    "높은 순",
)
SCHEDULE_MARKERS = (
    "일정",
    "기간",
    "언제",
    "날짜",
    "시작",
    "종료",
    "오늘",
    "내일",
    "주말",
    "이번 주",
    "이번 달",
)
RECOMMEND_MARKERS = (
    "추천",
    "가볼",
    "갈만",
    "어디 갈",
    "어디가",
    "뭐하지",
    "뭐 할",
    "뭐할",
    "둘러볼",
    "구경",
    "다른",
    "새로운",
    "더 보여",
    "더 알려",
)

STOP_WORDS = {
    "추천",
    "추천해줘",
    "추천해주세요",
    "알려줘",
    "알려주세요",
    "찾아줘",
    "찾아주세요",
    "보여줘",
    "보여주세요",
    "검색",
    "관련",
    "정보",
    "어디",
    "어떤",
    "좋은",
    "높은",
    "많은",
    "근처",
    "장소",
    "곳",
    "대한",
    "하고",
    "싶어",
    "있어",
    "있나",
    "있나요",
    "게시글",
    "커뮤니티",
    "후기",
    "리뷰",
    "평점",
    "별점",
    "일정",
    "기간",
    "날짜",
    "시설",
    "해줘",
    "해주세요",
    "부탁",
    "부탁해",
    "에서",
    "으로",
    "이랑",
    "이랑은",
    "하고",
    "할만한",
    "할",
    "볼",
    "살",
    "갈",
    "이번",
    "주말",
    "오늘",
    "내일",
    "다른",
    "다시",
    "정도",
    "이나",
    "또는",
    "혹은",
    "먹을",
    "구경",
    "둘러볼",
    "뭐하지",
    "뭐할",
}

FAQ_ENTRIES = (
    {
        "keywords": ("데이터", "지역", "범위", "무슨 정보"),
        "answer": (
            "LocalHub 챗봇은 제공된 JSON 기준으로 대전광역시, 충청남도(공주·논산·계룡), "
            "충청북도 옥천의 관광지, 레포츠, 문화시설, 쇼핑, 숙박, 여행코스, 음식점, "
            "축제·공연·행사 데이터를 검색해요. 현재 파일에는 세종 데이터가 없습니다."
        ),
    },
    {
        "keywords": ("평점", "별점", "리뷰 수"),
        "answer": (
            "평점과 리뷰 수는 LocalHub에 사용자가 작성한 게시글 데이터를 기준으로 보여줘요. "
            "아직 리뷰가 없는 장소는 '평점 정보 없음'으로 안내합니다."
        ),
    },
    {
        "keywords": ("축제 일정", "축제 날짜", "행사 일정", "기간"),
        "answer": (
            "현재 제공된 관광 JSON에는 축제명과 주소는 있지만 시작일·종료일 필드가 없어요. "
            "따라서 챗봇은 확인되지 않은 일정을 만들지 않고, 일정 데이터가 없다고 안내합니다."
        ),
    },
    {
        "keywords": ("지도", "마커", "좌표"),
        "answer": (
            "장소 데이터에 위도와 경도가 있어서 지도 마커로 연결할 수 있어요. "
            "챗봇 결과 카드에도 주소와 좌표를 함께 반환합니다."
        ),
    },
    {
        "keywords": ("무엇을 물어", "사용법", "질문 예시", "도움말"),
        "answer": (
            "예를 들어 '대전 관광지 추천해줘', '평점 높은 음식점 알려줘', "
            "'공주 숙소 찾아줘', '칼국수 관련 게시글 찾아줘'처럼 물어보면 됩니다."
        ),
    },
)


def _safe_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _compact_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def _contains_marker(query: str, markers: tuple[str, ...]) -> bool:
    normalized = re.sub(r"\s+", "", query.lower())
    return any(re.sub(r"\s+", "", marker.lower()) in normalized for marker in markers)


def _secure_image_url(value: Any) -> str:
    url = str(value or "").strip()
    if url.startswith("http://tong.visitkorea.or.kr/"):
        return "https://" + url.removeprefix("http://")
    return url


def _tokens(query: str) -> list[str]:
    words = re.findall(r"[0-9A-Za-z가-힣]+", query.lower())
    category_words = {
        word.replace(" ", "")
        for values in CATEGORY_KEYWORDS.values()
        for word in values
        if word.replace(" ", "") not in SEARCHABLE_CATEGORY_TERMS
    }
    region_words = {
        alias.replace(" ", "") for aliases in REGION_ALIASES.values() for alias in aliases
    }
    removable_words = sorted(
        STOP_WORDS | category_words | region_words,
        key=len,
        reverse=True,
    )
    tokens: list[str] = []
    for word in words:
        cleaned = word
        for removable in removable_words:
            cleaned = cleaned.replace(removable, " ")
        tokens.extend(
            token
            for token in re.findall(r"[0-9A-Za-z가-힣]+", cleaned)
            if len(token) > 1
        )
    return tokens


class LocalHubDataService:
    """제공 JSON을 검색하고 팀의 같은 SQLite DB에서 평점·게시글을 보강한다."""

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.locations = self._load_locations()

    def _load_locations(self) -> list[dict[str, Any]]:
        locations: list[dict[str, Any]] = []
        for path in sorted(self.data_dir.glob("*.json")):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue

            category = _compact_text(str(payload.get("contentType", "")))
            for item in payload.get("items", []):
                locations.append(
                    {
                        "type": "location",
                        "id": str(item.get("contentid", "")),
                        "title": _compact_text(str(item.get("title", ""))),
                        "category": category,
                        "address": _compact_text(
                            " ".join(
                                part
                                for part in (str(item.get("addr1", "")), str(item.get("addr2", "")))
                                if part
                            )
                        ),
                        "tel": _compact_text(str(item.get("tel", ""))),
                        "longitude": _safe_float(item.get("mapx")),
                        "latitude": _safe_float(item.get("mapy")),
                        "image_url": _secure_image_url(item.get("firstimage")),
                        "rating": None,
                        "review_count": 0,
                        "start_date": str(item.get("eventstartdate", "") or ""),
                        "end_date": str(item.get("eventenddate", "") or ""),
                        "area_region": AREA_CODE_REGIONS.get(str(item.get("areacode", "")), ""),
                    }
                )
        return locations

    @staticmethod
    def detect_categories(query: str) -> list[str]:
        normalized = query.lower().replace(" ", "")
        matched_categories: list[tuple[int, int, str]] = []
        for category_order, (category, keywords) in enumerate(CATEGORY_KEYWORDS.items()):
            positions = [
                normalized.find(keyword.replace(" ", ""))
                for keyword in keywords
                if keyword.replace(" ", "") in normalized
            ]
            if positions:
                matched_categories.append((min(positions), category_order, category))
        categories = [
            category for _, _, category in sorted(matched_categories)
        ]
        strong_tourism_words = ("관광지", "명소", "볼거리", "여행지")
        if len(categories) > 1 and "관광지" in categories and not any(
            word in normalized for word in strong_tourism_words
        ):
            categories.remove("관광지")
        if (
            "문화시설" in categories
            and "축제공연행사" in categories
            and "공연장" in normalized
            and not any(word in normalized for word in ("축제", "행사", "페스티벌", "이벤트"))
        ):
            categories.remove("축제공연행사")
        return categories

    @staticmethod
    def detect_regions(query: str) -> list[str]:
        regions = [
            region
            for region, aliases in REGION_ALIASES.items()
            if any(alias in query for alias in aliases)
        ]
        specific_regions = {"대전", "세종", "계룡", "공주", "논산", "옥천"}
        if any(region in specific_regions for region in regions):
            regions = [region for region in regions if region not in ("충청남도", "충청북도")]
        return regions

    @staticmethod
    def extract_keywords(query: str) -> list[str]:
        return _tokens(query)

    @staticmethod
    def is_post_query(query: str) -> bool:
        return _contains_marker(query, POST_MARKERS)

    @staticmethod
    def is_rating_query(query: str) -> bool:
        return _contains_marker(query, RATING_MARKERS)

    @staticmethod
    def is_schedule_query(query: str) -> bool:
        return _contains_marker(query, SCHEDULE_MARKERS) and _contains_marker(
            query, CATEGORY_KEYWORDS["축제공연행사"]
        )

    @staticmethod
    def is_recommendation_query(query: str) -> bool:
        return _contains_marker(query, RECOMMEND_MARKERS)

    def find_mentioned_location_ids(self, texts: list[str]) -> set[str]:
        combined = "\n".join(texts)
        return {
            location["id"]
            for location in self.locations
            if len(location["title"]) >= 2 and location["title"] in combined
        }

    @staticmethod
    def find_faq(query: str) -> str | None:
        normalized = query.replace(" ", "")
        for entry in FAQ_ENTRIES:
            if any(keyword.replace(" ", "") in normalized for keyword in entry["keywords"]):
                return str(entry["answer"])
        return None

    @staticmethod
    def _region_matches(location: dict[str, Any], regions: list[str]) -> bool:
        if not regions:
            return True
        searchable = f"{location['title']} {location['address']}"
        for region in regions:
            aliases = REGION_ALIASES.get(region, (region,))
            if any(alias in searchable for alias in aliases):
                return True
            if location.get("area_region") == region:
                return True
        return False

    def _search_local(self, query: str, limit: int = 12) -> list[dict[str, Any]]:
        categories = self.detect_categories(query)
        regions = self.detect_regions(query)
        query_tokens = _tokens(query)
        pool = [
            location
            for location in self.locations
            if (not categories or location["category"] in categories)
            and self._region_matches(location, regions)
        ]
        effective_tokens = [
            token
            for token in query_tokens
            if any(
                token
                in f"{location['title']} {location['address']} {location['category']}".lower()
                for location in pool
            )
        ]
        has_search_signal = bool(categories or regions or effective_tokens)
        scored: list[tuple[float, dict[str, Any]]] = []

        for location in pool:
            title = location["title"].lower()
            address = location["address"].lower()
            category = location["category"].lower()
            score = 0.0
            if categories:
                score += 10
            if regions:
                score += 7

            for token in effective_tokens:
                if token in title:
                    score += 14
                elif token in address:
                    score += 6
                elif token in category:
                    score += 4

            if effective_tokens and not any(
                token in title or token in address or token in category for token in effective_tokens
            ):
                continue
            if not has_search_signal:
                continue

            score += 0.4 if location["image_url"] else 0
            score += 0.2 if location["address"] else 0
            scored.append((score, location))

        scored.sort(key=lambda pair: (-pair[0], pair[1]["title"]))
        if len(categories) > 1:
            buckets = {
                category: iter(
                    [pair for pair in scored if pair[1]["category"] == category]
                )
                for category in categories
            }
            balanced: list[tuple[float, dict[str, Any]]] = []
            while len(balanced) < limit:
                added = False
                for category in categories:
                    try:
                        balanced.append(next(buckets[category]))
                        added = True
                    except StopIteration:
                        continue
                    if len(balanced) == limit:
                        break
                if not added:
                    break
            scored = balanced
        return [{**location, "_score": score} for score, location in scored[:limit]]

    def _default_recommendations(self, query: str, limit: int = 12) -> list[dict[str, Any]]:
        regions = self.detect_regions(query)
        preferred = ("관광지", "음식점", "문화시설", "축제공연행사", "숙박")
        chosen: list[dict[str, Any]] = []
        for category in preferred:
            candidates = [
                item
                for item in self.locations
                if item["category"] == category
                and self._region_matches(item, regions)
            ]
            candidates.sort(key=lambda item: (not bool(item["image_url"]), item["title"]))
            chosen.extend({**item, "_score": 1.0} for item in candidates[:3])
        return chosen[:limit]

    async def search_locations(
        self,
        query: str,
        *,
        limit: int = 5,
        allow_defaults: bool = False,
        exclude_ids: set[str] | None = None,
    ) -> list[dict[str, Any]]:
        excluded = exclude_ids or set()
        candidate_limit = max(12, min(60, limit + len(excluded) + 8))
        candidates = [
            item for item in self._search_local(query, limit=candidate_limit)
            if item["id"] not in excluded
        ][:12]
        if not candidates and allow_defaults and not self.detect_categories(query):
            candidates = [
                item for item in self._default_recommendations(query, limit=candidate_limit)
                if item["id"] not in excluded
            ][:12]
        if not candidates:
            return []

        rating_query = self.is_rating_query(query)
        if not rating_query:
            candidates = candidates[:limit]

        enriched = await asyncio.gather(
            *(self._enrich_location(item) for item in candidates),
            return_exceptions=True,
        )
        results = [
            item if isinstance(item, dict) else candidates[index]
            for index, item in enumerate(enriched)
        ]

        if rating_query:
            results.sort(
                key=lambda item: (
                    item.get("rating") is None,
                    -(item.get("rating") or 0),
                    -int(item.get("review_count") or 0),
                    -float(item.get("_score") or 0),
                )
            )
        return [self._public_location(item) for item in results[:limit]]

    async def _enrich_location(
        self,
        location: dict[str, Any],
    ) -> dict[str, Any]:
        return await asyncio.to_thread(self._enrich_location_sync, location)

    @staticmethod
    def _enrich_location_sync(location: dict[str, Any]) -> dict[str, Any]:
        try:
            with SessionLocal() as db:
                detail = crud.get_location(db, location["id"])
                if detail is None:
                    return location
                average_rating, review_count = crud.get_location_rating(
                    db, location["id"]
                )
                return {
                    **location,
                    "address": detail.addr1 or location["address"],
                    "image_url": _secure_image_url(
                        detail.first_image or location["image_url"]
                    ),
                    "longitude": (
                        detail.lng if detail.lng is not None else location["longitude"]
                    ),
                    "latitude": (
                        detail.lat if detail.lat is not None else location["latitude"]
                    ),
                    "rating": average_rating,
                    "review_count": int(review_count or 0),
                }
        except SQLAlchemyError:
            # DB가 아직 seed 되지 않았어도 JSON 검색 결과는 정상 반환한다.
            return location

    @staticmethod
    def _public_location(location: dict[str, Any]) -> dict[str, Any]:
        return {
            key: location.get(key)
            for key in (
                "type",
                "id",
                "title",
                "category",
                "address",
                "rating",
                "review_count",
                "image_url",
                "latitude",
                "longitude",
                "start_date",
                "end_date",
            )
        }

    async def search_posts(self, query: str, limit: int = 4) -> list[dict[str, Any]]:
        return await asyncio.to_thread(self._search_posts_sync, query, limit)

    @staticmethod
    def _search_posts_sync(query: str, limit: int) -> list[dict[str, Any]]:
        query_tokens = sorted(_tokens(query), key=len, reverse=True)
        keyword = query_tokens[0] if query_tokens else ""
        try:
            with SessionLocal() as db:
                _, items = crud.get_posts(
                    db,
                    keyword=keyword or None,
                    sort="latest",
                    page=1,
                    size=limit,
                )
                results = [
                    {
                        "type": "post",
                        "id": str(item.id),
                        "title": item.title,
                        "category": item.category,
                        "rating": item.rating,
                        "content": item.content,
                        "view_count": int(item.view_count or 0),
                    }
                    for item in items
                ]
        except SQLAlchemyError:
            return []

        posts: list[dict[str, Any]] = []
        for item in results:
            content = _compact_text(str(item.get("content", "")))
            posts.append(
                {
                    "type": "post",
                    "id": str(item.get("id", "")),
                    "title": str(item.get("title", "")),
                    "category": str(item.get("category", "")),
                    "rating": item.get("rating"),
                    "excerpt": f"{content[:137]}..." if len(content) > 140 else content,
                    "view_count": int(item.get("view_count") or 0),
                }
            )
        return posts
