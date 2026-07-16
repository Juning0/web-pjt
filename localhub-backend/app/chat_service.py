import json
import logging
from typing import Any

from openai import (
    APIConnectionError,
    AuthenticationError,
    AsyncOpenAI,
    BadRequestError,
    NotFoundError,
    OpenAIError,
    PermissionDeniedError,
    RateLimitError,
)

from app.chat_data_service import LocalHubDataService
from app.chat_schemas import (
    ChatMode,
    ChatRequest,
    ChatResponse,
    ChatSource,
    QueryIntent,
    ResolvedChatMode,
)


logger = logging.getLogger(__name__)
ALLOWED_MODEL = "gpt-5-mini"

FOLLOW_UP_MARKERS = ("거기", "그곳", "그 곳", "그중", "그 중", "아까", "그러면", "그럼", "다른")
DIFFERENT_MARKERS = ("다른", "말고", "새로운", "또 추천", "더 보여", "더 알려")
ONE_EACH_MARKERS = (
    "하나씩",
    "한 곳씩",
    "한곳씩",
    "한 개씩",
    "한개씩",
    "각각 하나",
    "각 하나",
    "각 1곳",
    "각 한 곳",
    "각 한곳",
)
GREETING_MARKERS = ("안녕", "안녕하세요", "반가워", "반갑습니다", "하이", "hello", "hi")
FAQ_MARKERS = (
    "도움말",
    "사용법",
    "질문 예시",
    "데이터 범위",
    "어떤 지역 데이터",
    "무슨 데이터",
    "지도 마커",
    "평점은 어디서",
    "뭘 물어",
    "무엇을 물어",
)

SYSTEM_INSTRUCTIONS = """
당신은 대전·충청권 지역 정보 서비스 '대전여지도'의 한국어 안내 챗봇이다.

반드시 아래 규칙을 지킨다.
1. 현재 사용자 질문을 이전 대화보다 우선하고, 제공된 대전여지도 검색 결과 JSON 안의 사실만 사용한다.
2. 현재 검색 결과에 없는 이전 장소를 반복해서 추천하지 않는다.
3. 장소명, 주소, 평점, 리뷰 수, 게시글 내용은 임의로 만들거나 추측하지 않는다.
4. rating이 null이면 '평점 정보 없음' 또는 '아직 등록된 평점이 없음'이라고 표현한다.
5. 축제 결과의 start_date와 end_date가 비어 있으면 확인 가능한 일정 데이터가 없다고 분명히 말한다.
6. 장소 추천과 커뮤니티 게시글을 구분해서 설명한다.
7. 숙박 예약 가능 여부, 가격, 영업시간, 행사 개최 여부처럼 JSON에 없는 최신 정보는 단정하지 않는다.
8. 검색 결과가 비어 있으면 없는 결과를 만들어내지 말고, 현재 제공 데이터에서 찾지 못했다고 안내한다.
9. 답은 친절하고 간결한 한국어 일반 텍스트로 작성하며, 장소는 최대 5개까지만 소개한다.
10. 웹 검색, 도구 실행, 예약, 게시글 작성 등은 수행하지 않고 질의응답만 한다.
11. 사용자가 여러 카테고리를 '하나씩' 요청하면 검색 결과에서 카테고리별로 정확히 1곳씩 답한다.
12. category_result_counts가 1 이상인 카테고리를 결과가 없다고 잘못 안내하지 않는다.
13. nearby_search가 있으면 기준 장소와 검색 반경을 확인하고, distance_km는 좌표로 계산한 직선거리로 안내한다.
""".strip()

INTENT_INSTRUCTIONS = """
당신은 대전여지도 관광 챗봇의 검색 의도 분석기다. 사용자의 현재 질문과 최근 대화에서 검색 조건만 추출한다.

- mode는 장소 검색/추천이면 recommend, 커뮤니티 글이나 후기를 찾으면 posts, 서비스 사용법 질문이면 faq다.
- categories는 다음 값만 사용한다: 관광지, 레포츠, 문화시설, 쇼핑, 숙박, 여행코스, 음식점, 축제공연행사.
- '잘 곳/묵을 곳/하룻밤'은 숙박, '밥/먹을 곳/맛집'은 음식점, '아이랑 갈 곳/명소'는 관광지다.
- '캠핑/운동/액티비티'는 레포츠, '박물관/전시'는 문화시설, '시장/기념품'은 쇼핑이다.
- '당일치기/1박2일/동선'은 여행코스, '축제/행사/공연 일정'은 축제공연행사다.
- regions는 대전, 세종, 공주, 논산, 계룡, 옥천, 충청남도, 충청북도 중에서만 고른다.
- 현재 질문에 지역이나 카테고리가 생략되고 '거기/그중/다른 곳'처럼 이어 묻는 경우에만 최근 대화 조건을 물려받는다.
- keywords에는 장소명, 음식명, 동네명처럼 제목이나 주소에서 검색 가능한 핵심어만 넣는다.
- '예쁜/조용한/아이와/실내'처럼 현재 기본 데이터 필드로 확인할 수 없는 조건은 keywords에 넣지 않는다.
- 확인할 수 없는 값은 추측하지 말고 빈 배열로 둔다.
""".strip()


class ChatService:
    def __init__(
        self,
        data_service: LocalHubDataService,
        *,
        openai_api_key: str,
        openai_base_url: str = "",
    ) -> None:
        self.data_service = data_service
        client_options: dict[str, Any] = {
            "api_key": openai_api_key,
            "timeout": 20.0,
            "max_retries": 0,
        }
        if openai_base_url:
            client_options["base_url"] = openai_base_url.rstrip("/")
        self.openai_client = AsyncOpenAI(**client_options) if openai_api_key else None

    async def answer(self, request: ChatRequest) -> ChatResponse:
        query = request.message.strip()
        if self._is_greeting(query):
            return ChatResponse(
                answer=(
                    "안녕하세요! 대전·충청권의 관광지, 맛집, 숙박, 문화시설, 레포츠, "
                    "쇼핑, 여행코스, 축제·행사를 찾아드릴게요."
                ),
                suggestions=["대전 관광지 추천해줘", "공주 숙박시설 알려줘", "칼국수맛집 찾아줘"],
                mode="recommend",
                engine="local",
            )

        nearby_request = self.data_service.parse_nearby_query(query)
        intent, intent_error = await self._resolve_intent(request)
        mode: ResolvedChatMode = intent.mode
        if mode != "recommend":
            nearby_request = None
        elif nearby_request:
            if nearby_request["categories"]:
                intent.categories = nearby_request["categories"]
            intent.keywords = []
        faq_answer = self.data_service.find_faq(query) if mode == "faq" else None
        if mode == "faq" and not faq_answer:
            faq_answer = (
                "데이터 범위, 평점 기준, 축제 일정, 지도·마커, 질문 방법 중에서 "
                "궁금한 내용을 입력해 주세요."
            )

        search_query = self._build_search_query(query, intent)
        exclude_ids: set[str] = set()
        if self._wants_different_results(query):
            history_texts = [message.content for message in request.history]
            if "말고" in query:
                history_texts.append(query)
            exclude_ids = self.data_service.find_mentioned_location_ids(history_texts)
        locations: list[dict[str, Any]] = []
        posts: list[dict[str, Any]] = []
        nearby_anchor: dict[str, Any] | None = None

        if mode == "recommend":
            location_limit = self._location_limit(query, intent)
            if nearby_request:
                locations, nearby_anchor = await self.data_service.search_nearby_locations(
                    nearby_request["anchor_keyword"],
                    categories=intent.categories,
                    limit=location_limit,
                    radius_km=float(nearby_request["radius_km"]),
                    exclude_ids=exclude_ids,
                )
            else:
                locations = await self.data_service.search_locations(
                    search_query,
                    limit=location_limit,
                    allow_defaults=self.data_service.is_recommendation_query(query),
                    exclude_ids=exclude_ids,
                )
        elif mode == "posts":
            locations = await self.data_service.search_locations(
                search_query,
                limit=3,
                exclude_ids=exclude_ids,
            )
            posts = await self.data_service.search_posts(search_query, limit=4)

        sources = [ChatSource(**item) for item in [*locations, *posts]]
        suggestions = self._suggestions(mode, locations, posts)
        context = self._build_context(
            query,
            search_query,
            intent,
            locations,
            posts,
            faq_answer,
            nearby_request=nearby_request,
            nearby_anchor=nearby_anchor,
        )

        if self.openai_client and mode != "faq" and not intent_error:
            try:
                answer = await self._ask_openai(request, context)
                if answer:
                    return ChatResponse(
                        answer=answer,
                        sources=sources,
                        suggestions=suggestions,
                        mode=mode,
                        fallback=False,
                        engine="openai",
                    )
            except Exception as exc:  # Local search remains available when OpenAI is unavailable.
                intent_error = self._openai_error(exc)
                logger.warning("OpenAI answer failed: %s", type(exc).__name__)

        answer = self._fallback_answer(
            query,
            intent,
            locations,
            posts,
            faq_answer,
            nearby_request=nearby_request,
            nearby_anchor=nearby_anchor,
        )
        error_code = ""
        notice = ""
        if mode != "faq":
            if intent_error:
                error_code, notice = intent_error
            elif not self.openai_client:
                error_code, notice = self._missing_key_error()

        return ChatResponse(
            answer=answer,
            sources=sources,
            suggestions=suggestions,
            mode=mode,
            fallback=mode != "faq",
            engine="local",
            notice=notice,
            error_code=error_code,
        )

    async def _resolve_intent(
        self,
        request: ChatRequest,
    ) -> tuple[QueryIntent, tuple[str, str] | None]:
        heuristic = self._heuristic_intent(request)
        if not self.openai_client or heuristic.mode == "faq":
            return heuristic, None

        try:
            parsed = await self._analyze_with_openai(request)
            return self._merge_intents(request.message, heuristic, parsed), None
        except Exception as exc:
            logger.warning("OpenAI intent analysis failed: %s", type(exc).__name__)
            return heuristic, self._openai_error(exc)

    def _heuristic_intent(self, request: ChatRequest) -> QueryIntent:
        query = request.message.strip()
        categories = self.data_service.detect_categories(query)
        regions = self.data_service.detect_regions(query)
        keywords = self.data_service.extract_keywords(query)[:5]
        is_follow_up = any(marker in query.replace(" ", "") for marker in FOLLOW_UP_MARKERS)

        if is_follow_up and (not categories or not regions or not keywords):
            for message in reversed(request.history):
                if message.role != "user":
                    continue
                if not categories:
                    categories = self.data_service.detect_categories(message.content)
                if not regions:
                    regions = self.data_service.detect_regions(message.content)
                if not keywords:
                    keywords = self.data_service.extract_keywords(message.content)[:5]
                if categories and regions and keywords:
                    break

        mode = self._resolve_mode(request.mode, query)
        return QueryIntent(
            mode=mode,
            categories=categories[:3],
            regions=regions[:3],
            keywords=keywords[:5],
            wants_rating=self.data_service.is_rating_query(query),
            wants_schedule=self.data_service.is_schedule_query(query),
            is_follow_up=is_follow_up,
        )

    def _resolve_mode(self, requested_mode: ChatMode, query: str) -> ResolvedChatMode:
        normalized = query.replace(" ", "")
        if requested_mode == "faq" or any(marker.replace(" ", "") in normalized for marker in FAQ_MARKERS):
            return "faq"
        if self.data_service.is_post_query(query) and not self.data_service.is_rating_query(query):
            return "posts"
        if requested_mode == "posts":
            return "posts"
        return "recommend"

    async def _analyze_with_openai(self, request: ChatRequest) -> QueryIntent:
        history_lines = [
            f"{('사용자' if message.role == 'user' else '챗봇')}: {message.content}"
            for message in request.history[-6:]
        ]
        prompt = (
            f"현재 UI 탭: {request.mode}\n"
            + "최근 대화:\n"
            + ("\n".join(history_lines) if history_lines else "(없음)")
            + "\n현재 질문:\n"
            + request.message.strip()
        )
        response = await self.openai_client.responses.parse(
            model=ALLOWED_MODEL,
            instructions=INTENT_INSTRUCTIONS,
            input=prompt,
            text_format=QueryIntent,
            reasoning={"effort": "minimal"},
            max_output_tokens=500,
            store=False,
        )
        if response.output_parsed is None:
            raise ValueError("OpenAI intent response was empty")
        return response.output_parsed

    def _merge_intents(
        self,
        current_query: str,
        heuristic: QueryIntent,
        parsed: QueryIntent,
    ) -> QueryIntent:
        explicit_categories = self.data_service.detect_categories(current_query)
        explicit_regions = self.data_service.detect_regions(current_query)
        mode = heuristic.mode if heuristic.mode in ("faq", "posts") else parsed.mode
        parsed_categories = list(parsed.categories)
        categories = explicit_categories or parsed_categories or heuristic.categories
        return QueryIntent(
            mode=mode,
            categories=categories[:3],
            regions=(explicit_regions or parsed.regions or heuristic.regions)[:3],
            keywords=(parsed.keywords or heuristic.keywords)[:5],
            wants_rating=heuristic.wants_rating or parsed.wants_rating,
            wants_schedule=heuristic.wants_schedule or parsed.wants_schedule,
            is_follow_up=heuristic.is_follow_up or parsed.is_follow_up,
        )

    @staticmethod
    def _build_search_query(original_query: str, intent: QueryIntent) -> str:
        parts = [*intent.regions, *intent.categories, *intent.keywords]
        if intent.wants_rating:
            parts.append("평점 높은 순")
        if intent.wants_schedule:
            parts.append("축제 일정")
        return " ".join(dict.fromkeys(parts)) if parts else original_query

    async def _ask_openai(self, request: ChatRequest, context: dict[str, Any]) -> str:
        history_lines = [
            f"{('사용자' if message.role == 'user' else '챗봇')}: {message.content}"
            for message in request.history[-8:]
        ]
        prompt = (
            "최근 대화:\n"
            + ("\n".join(history_lines) if history_lines else "(없음)")
            + "\n\n현재 사용자 질문:\n"
            + request.message.strip()
            + "\n\n현재 질문용 대전여지도 검색 결과(JSON):\n"
            + json.dumps(context, ensure_ascii=False, indent=2)
        )
        response = await self.openai_client.responses.create(
            model=ALLOWED_MODEL,
            instructions=SYSTEM_INSTRUCTIONS,
            input=prompt,
            reasoning={"effort": "minimal"},
            max_output_tokens=1_000,
            store=False,
        )
        return response.output_text.strip()

    @staticmethod
    def _build_context(
        query: str,
        search_query: str,
        intent: QueryIntent,
        locations: list[dict[str, Any]],
        posts: list[dict[str, Any]],
        faq_answer: str | None,
        *,
        nearby_request: dict[str, Any] | None = None,
        nearby_anchor: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return {
            "current_query": query,
            "resolved_search_query": search_query,
            "resolved_intent": intent.model_dump(),
            "locations": locations,
            "category_result_counts": {
                category: sum(item.get("category") == category for item in locations)
                for category in intent.categories
            },
            "community_posts": posts,
            "faq_answer": faq_answer,
            "nearby_search": (
                {
                    "requested": True,
                    "anchor_keyword": nearby_request["anchor_keyword"],
                    "anchor": nearby_anchor,
                    "radius_km": nearby_request["radius_km"],
                    "distance_type": "좌표 기준 직선거리",
                }
                if nearby_request
                else None
            ),
            "limitations": {
                "festival_start_end_dates_available": any(
                    item.get("start_date") or item.get("end_date") for item in locations
                ),
                "ratings_source": "대전여지도 사용자 게시글",
                "empty_rating_meaning": "아직 등록된 평점이 없음",
                "sejong_records_available": False,
            },
        }

    def _fallback_answer(
        self,
        query: str,
        intent: QueryIntent,
        locations: list[dict[str, Any]],
        posts: list[dict[str, Any]],
        faq_answer: str | None,
        *,
        nearby_request: dict[str, Any] | None = None,
        nearby_anchor: dict[str, Any] | None = None,
    ) -> str:
        if faq_answer:
            return faq_answer
        if nearby_request:
            return self._fallback_nearby_answer(
                intent,
                locations,
                nearby_request,
                nearby_anchor,
            )

        parts: list[str] = []
        if locations:
            heading = "검색된 장소를 알려드릴게요."
            if intent.wants_schedule:
                heading = (
                    "관련 축제·행사 이름은 찾았지만 현재 개최 여부와 정확한 일정은 "
                    "확인할 수 없어요."
                )
            if intent.wants_rating:
                rated = [item for item in locations if item.get("rating") is not None]
                heading = (
                    "등록된 평점을 기준으로 확인한 결과예요."
                    if rated
                    else "조건에 맞는 장소는 찾았지만 아직 등록된 평점은 없어요."
                )
            lines = [heading]
            for index, item in enumerate(locations, start=1):
                rating = (
                    f"평점 {item['rating']:.1f} · 리뷰 {item['review_count']}개"
                    if item.get("rating") is not None
                    else "평점 정보 없음"
                )
                address = item.get("address") or "주소 정보 없음"
                date_text = self._event_date_text(item)
                details = f"{address} · {rating}"
                if date_text:
                    details = f"일정 {date_text}\n   {details}"
                lines.append(f"{index}. {item['title']} ({item['category']})\n   {details}")
            parts.append("\n".join(lines))
        elif "세종" in intent.regions:
            parts.append("현재 제공된 JSON에는 세종 지역 데이터가 없어 장소를 안내할 수 없어요.")
        elif intent.categories or intent.regions or intent.keywords:
            condition = " ".join([*intent.regions, *intent.categories, *intent.keywords]).strip()
            parts.append(f"현재 제공된 대전여지도 데이터에서 '{condition}' 조건의 장소를 찾지 못했어요.")

        is_event_query = "축제공연행사" in intent.categories
        if (intent.wants_schedule or is_event_query) and not any(
            item.get("start_date") or item.get("end_date") for item in locations
        ):
            parts.append(
                "현재 제공된 축제 데이터에는 시작일·종료일이 없어 정확한 일정은 안내할 수 없어요. "
                "행사명에 과거 연도가 포함될 수도 있으므로 현재 개최 여부는 별도 확인이 필요합니다."
            )

        if posts:
            lines = ["관련 커뮤니티 게시글도 찾았어요."]
            for index, post in enumerate(posts, start=1):
                rating = f" · 평점 {post['rating']}" if post.get("rating") is not None else ""
                lines.append(f"{index}. {post['title']}{rating} · 조회 {post['view_count']}")
            parts.append("\n".join(lines))
        elif intent.mode == "posts":
            parts.append("현재 조건과 일치하는 커뮤니티 게시글은 없어요.")

        if not parts:
            return (
                "제가 확인할 수 있는 범위는 대전·충청권 관광지, 음식점, 숙박, 문화시설, "
                "레포츠, 쇼핑, 여행코스, 축제·행사와 대전여지도 게시글이에요. "
                "예: '대전에서 잘 곳 알려줘'"
            )
        return "\n\n".join(parts)

    @staticmethod
    def _fallback_nearby_answer(
        intent: QueryIntent,
        locations: list[dict[str, Any]],
        nearby_request: dict[str, Any],
        nearby_anchor: dict[str, Any] | None,
    ) -> str:
        anchor_keyword = str(nearby_request["anchor_keyword"])
        if nearby_anchor is None:
            return (
                f"현재 제공된 대전여지도 데이터에서 기준 장소 '{anchor_keyword}'를 찾지 못했어요. "
                "장소명을 조금 더 정확하게 입력해 주세요."
            )

        category_text = "·".join(intent.categories) if intent.categories else "장소"
        radius_km = float(nearby_request["radius_km"])
        if not locations:
            return (
                f"{nearby_anchor['title']}을(를) 기준으로 반경 {radius_km:g}km 안에서 "
                f"{category_text} 정보를 찾지 못했어요."
            )

        lines = [
            f"{nearby_anchor['title']} 주변의 {category_text} 정보를 가까운 순으로 알려드릴게요."
        ]
        for index, item in enumerate(locations, start=1):
            distance = item.get("distance_km")
            distance_text = (
                f"약 {float(distance):.1f}km"
                if distance is not None
                else "같은 동네 주소"
            )
            address = item.get("address") or "주소 정보 없음"
            rating = (
                f"평점 {item['rating']:.1f} · 리뷰 {item['review_count']}개"
                if item.get("rating") is not None
                else "평점 정보 없음"
            )
            lines.append(
                f"{index}. {item['title']} ({distance_text})\n"
                f"   {address} · {rating}"
            )
        return "\n".join(lines)

    @staticmethod
    def _event_date_text(item: dict[str, Any]) -> str:
        def format_date(value: str) -> str:
            return (
                f"{value[:4]}.{value[4:6]}.{value[6:8]}"
                if len(value) == 8 and value.isdigit()
                else value
            )

        start = str(item.get("start_date") or "")
        end = str(item.get("end_date") or "")
        if not start and not end:
            return ""
        if not end or start == end:
            return format_date(start)
        return f"{format_date(start)} ~ {format_date(end)}"

    @staticmethod
    def _suggestions(
        mode: ChatMode,
        locations: list[dict[str, Any]],
        posts: list[dict[str, Any]],
    ) -> list[str]:
        if mode == "faq":
            return ["평점은 어디서 가져와?", "축제 일정도 알 수 있어?", "지도 마커도 가능해?"]
        if mode == "posts":
            suggestions = ["최신 게시글 찾아줘", "평점 있는 후기 보여줘"]
            if locations:
                suggestions.insert(0, f"{locations[0]['title']} 위치 알려줘")
            return suggestions[:3]
        suggestions = ["대전 관광지 추천해줘", "평점 높은 음식점 알려줘", "공주 숙소 찾아줘"]
        if locations:
            suggestions[0] = f"{locations[0]['title']} 관련 게시글 찾아줘"
        if posts:
            suggestions[1] = "이 게시글과 관련된 장소 알려줘"
        return suggestions[:3]

    @staticmethod
    def _is_greeting(query: str) -> bool:
        normalized = query.lower().strip().rstrip("!?.~ ")
        return normalized in GREETING_MARKERS

    @staticmethod
    def _wants_different_results(query: str) -> bool:
        normalized = query.replace(" ", "")
        return any(marker.replace(" ", "") in normalized for marker in DIFFERENT_MARKERS)

    @staticmethod
    def _location_limit(query: str, intent: QueryIntent) -> int:
        normalized = query.replace(" ", "")
        asks_one_each = any(
            marker.replace(" ", "") in normalized for marker in ONE_EACH_MARKERS
        )
        if asks_one_each and len(intent.categories) > 1:
            return min(5, len(intent.categories))
        return 5

    @staticmethod
    def _missing_key_error() -> tuple[str, str]:
        return (
            "api_key_missing",
            "OpenAI API 키가 로드되지 않아 기본 데이터 검색 답변을 사용했어요. "
            "로컬은 backend/.env, 배포 서버는 환경 변수 설정 후 FastAPI 재시작을 확인하세요.",
        )

    @staticmethod
    def _openai_error(exc: Exception) -> tuple[str, str]:
        if isinstance(exc, AuthenticationError):
            return (
                "authentication_failed",
                "OpenAI API 키 인증에 실패해 기본 검색 답변을 사용했어요. 키 값과 프로젝트를 확인하세요.",
            )
        if isinstance(exc, PermissionDeniedError):
            return (
                "permission_denied",
                "OpenAI API 키 권한이 Responses 요청을 허용하지 않아 기본 검색 답변을 사용했어요.",
            )
        if isinstance(exc, NotFoundError):
            return (
                "model_unavailable",
                f"API 키 프로젝트에서 {ALLOWED_MODEL} 모델을 사용할 수 없어 기본 검색 답변을 사용했어요.",
            )
        if isinstance(exc, RateLimitError):
            return (
                "rate_limit",
                "OpenAI 사용 한도 또는 호출 한도에 도달해 기본 검색 답변을 사용했어요.",
            )
        if isinstance(exc, APIConnectionError):
            return (
                "connection_error",
                "OpenAI 서버에 연결하지 못해 기본 검색 답변을 사용했어요. 네트워크를 확인하세요.",
            )
        if isinstance(exc, BadRequestError):
            return (
                "bad_request",
                "OpenAI 요청 설정이 거절되어 기본 검색 답변을 사용했어요. 모델과 API 설정을 확인하세요.",
            )
        if isinstance(exc, OpenAIError):
            return (
                "openai_error",
                "OpenAI 응답 오류로 기본 데이터 검색 답변을 사용했어요.",
            )
        return (
            "intent_or_response_error",
            "AI 의도 분석 또는 답변 생성 중 오류가 발생해 기본 데이터 검색 답변을 사용했어요.",
        )
