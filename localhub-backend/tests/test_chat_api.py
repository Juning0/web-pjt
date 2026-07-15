from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.chat_schemas import QueryIntent
from app.main import app
from app.routers.chat import chat_service, data_service


client = TestClient(app)


async def skip_database_enrichment(location, **kwargs):
    return location


def test_health_reports_loaded_data() -> None:
    response = client.get("/api/chat/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["locations_loaded"] == 1365
    assert response.json()["model"] == "gpt-5-mini"


def test_faq_answer_does_not_need_openai() -> None:
    response = client.post(
        "/api/chat",
        json={"message": "지도 마커도 가능해?", "history": [], "mode": "faq"},
    )

    assert response.status_code == 200
    body = response.json()
    assert "위도" in body["answer"]
    assert body["mode"] == "faq"
    assert body["fallback"] is False


def test_faq_is_detected_even_when_recommend_tab_is_selected() -> None:
    response = client.post(
        "/api/chat",
        json={"message": "지도 마커도 가능해?", "history": [], "mode": "recommend"},
    )

    assert response.status_code == 200
    assert response.json()["mode"] == "faq"


def test_location_search_uses_bundled_json(monkeypatch) -> None:
    monkeypatch.setattr(data_service, "_enrich_location", skip_database_enrichment)
    response = client.post(
        "/api/chat",
        json={"message": "공주 숙소 찾아줘", "history": [], "mode": "recommend"},
    )

    assert response.status_code == 200
    sources = response.json()["sources"]
    assert sources
    assert all(source["type"] == "location" for source in sources)
    assert all(source["category"] == "숙박" for source in sources)
    assert all("공주" in source["address"] for source in sources)


def test_festival_schedule_is_not_invented(monkeypatch) -> None:
    monkeypatch.setattr(data_service, "_enrich_location", skip_database_enrichment)
    response = client.post(
        "/api/chat",
        json={"message": "축제 일정 알려줘", "history": [], "mode": "recommend"},
    )

    assert response.status_code == 200
    assert "시작일·종료일" in response.json()["answer"]


def test_compound_lodging_word_stays_in_lodging_category(monkeypatch) -> None:
    monkeypatch.setattr(data_service, "_enrich_location", skip_database_enrichment)
    response = client.post(
        "/api/chat",
        json={"message": "대전 숙박시설 추천해줘", "history": [], "mode": "recommend"},
    )

    assert response.status_code == 200
    sources = response.json()["sources"]
    assert sources
    assert all(source["category"] == "숙박" for source in sources)
    assert all("대전" in source["address"] for source in sources)


def test_compound_food_keyword_keeps_specific_search_term(monkeypatch) -> None:
    monkeypatch.setattr(data_service, "_enrich_location", skip_database_enrichment)
    response = client.post(
        "/api/chat",
        json={"message": "칼국수맛집 추천해줘", "history": [], "mode": "recommend"},
    )

    assert response.status_code == 200
    sources = response.json()["sources"]
    assert sources
    assert all(source["category"] == "음식점" for source in sources)
    assert all("칼국수" in source["title"] for source in sources)


def test_one_each_returns_every_requested_category(monkeypatch) -> None:
    monkeypatch.setattr(data_service, "_enrich_location", skip_database_enrichment)
    monkeypatch.setattr(chat_service, "openai_client", None)

    response = client.post(
        "/api/chat",
        json={
            "message": "대전 놀러갈껀데 관광지랑 음식점 숙소 하나씩 알려줘",
            "history": [],
            "mode": "recommend",
        },
    )

    assert response.status_code == 200
    sources = response.json()["sources"]
    assert len(sources) == 3
    assert [source["category"] for source in sources] == ["관광지", "음식점", "숙박"]
    assert all("대전" in source["address"] for source in sources)
    assert all(category in response.json()["answer"] for category in ("관광지", "음식점", "숙박"))


def test_multiple_categories_are_balanced_without_one_each(monkeypatch) -> None:
    monkeypatch.setattr(data_service, "_enrich_location", skip_database_enrichment)
    monkeypatch.setattr(chat_service, "openai_client", None)

    response = client.post(
        "/api/chat",
        json={
            "message": "대전 관광지 음식점 숙소 추천해줘",
            "history": [],
            "mode": "recommend",
        },
    )

    assert response.status_code == 200
    categories = {source["category"] for source in response.json()["sources"]}
    assert categories == {"관광지", "음식점", "숙박"}


def test_explicit_categories_survive_incomplete_openai_intent(monkeypatch) -> None:
    monkeypatch.setattr(data_service, "_enrich_location", skip_database_enrichment)

    class IncompleteIntentResponses:
        async def parse(self, **kwargs):
            return SimpleNamespace(
                output_parsed=QueryIntent(
                    mode="recommend",
                    categories=["관광지", "음식점"],
                    regions=["대전"],
                    keywords=[],
                )
            )

        async def create(self, **kwargs):
            assert '"숙박": 1' in kwargs["input"]
            return SimpleNamespace(output_text="관광지, 음식점, 숙박을 한 곳씩 안내할게요.")

    monkeypatch.setattr(
        chat_service,
        "openai_client",
        SimpleNamespace(responses=IncompleteIntentResponses()),
    )
    response = client.post(
        "/api/chat",
        json={
            "message": "대전 놀러갈껀데 관광지랑 음식점 숙소 하나씩 알려줘",
            "history": [],
            "mode": "recommend",
        },
    )

    assert response.status_code == 200
    assert response.json()["engine"] == "openai"
    assert [source["category"] for source in response.json()["sources"]] == [
        "관광지",
        "음식점",
        "숙박",
    ]


@pytest.mark.parametrize(
    ("query", "category"),
    [
        ("대전에서 아이랑 갈만한 곳", "관광지"),
        ("대전에서 캠핑이나 액티비티 할 곳", "레포츠"),
        ("대전 실내 전시 볼 곳", "문화시설"),
        ("공주 전통시장 구경", "쇼핑"),
        ("대전에서 하룻밤 묵을 곳", "숙박"),
        ("공주에서 하루 묵고 싶어", "숙박"),
        ("충청남도 당일치기 코스", "여행코스"),
        ("대전에서 밥 먹을 곳", "음식점"),
        ("대전 주말 공연 행사", "축제공연행사"),
    ],
)
def test_natural_phrases_search_the_right_category(monkeypatch, query, category) -> None:
    monkeypatch.setattr(data_service, "_enrich_location", skip_database_enrichment)

    response = client.post(
        "/api/chat",
        json={"message": query, "history": [], "mode": "recommend"},
    )

    assert response.status_code == 200
    sources = response.json()["sources"]
    assert sources
    assert all(source["category"] == category for source in sources)


@pytest.mark.parametrize(
    ("query", "title_word"),
    [
        ("대전 카페 알려줘", "카페"),
        ("대전 박물관 알려줘", "박물관"),
        ("대전 백화점 알려줘", "백화점"),
        ("옥천 캠핑 알려줘", "캠핑"),
    ],
)
def test_specific_facility_word_refines_results(monkeypatch, query, title_word) -> None:
    monkeypatch.setattr(data_service, "_enrich_location", skip_database_enrichment)

    response = client.post(
        "/api/chat",
        json={"message": query, "history": [], "mode": "recommend"},
    )

    assert response.status_code == 200
    titles = [source["title"] for source in response.json()["sources"]]
    assert titles
    assert all(title_word in title for title in titles)


def test_performance_hall_is_not_mistaken_for_event(monkeypatch) -> None:
    monkeypatch.setattr(data_service, "_enrich_location", skip_database_enrichment)

    response = client.post(
        "/api/chat",
        json={"message": "대전 공연장 알려줘", "history": [], "mode": "recommend"},
    )

    assert response.status_code == 200
    assert response.json()["sources"]
    assert all(source["category"] == "문화시설" for source in response.json()["sources"])


def test_explicit_empty_category_never_falls_back_to_unrelated_places(monkeypatch) -> None:
    monkeypatch.setattr(data_service, "_enrich_location", skip_database_enrichment)

    response = client.post(
        "/api/chat",
        json={"message": "세종 숙박시설 알려줘", "history": [], "mode": "recommend"},
    )

    assert response.status_code == 200
    assert response.json()["sources"] == []
    assert "세종 지역 데이터가 없어" in response.json()["answer"]


def test_different_follow_up_excludes_places_already_shown(monkeypatch) -> None:
    monkeypatch.setattr(data_service, "_enrich_location", skip_database_enrichment)
    first = client.post(
        "/api/chat",
        json={"message": "공주 숙소 찾아줘", "history": [], "mode": "recommend"},
    ).json()
    shown_titles = ", ".join(source["title"] for source in first["sources"])

    second = client.post(
        "/api/chat",
        json={
            "message": "다른 곳 보여줘",
            "history": [
                {"role": "user", "content": "공주 숙소 찾아줘"},
                {
                    "role": "assistant",
                    "content": f"{first['answer']}\n[화면에 표시된 결과: {shown_titles}]",
                },
            ],
            "mode": "recommend",
        },
    ).json()

    assert second["sources"]
    assert all(source["category"] == "숙박" for source in second["sources"])
    assert {source["id"] for source in first["sources"]}.isdisjoint(
        source["id"] for source in second["sources"]
    )


def test_different_follow_up_also_works_after_generic_recommendation(monkeypatch) -> None:
    monkeypatch.setattr(data_service, "_enrich_location", skip_database_enrichment)
    first = client.post(
        "/api/chat",
        json={"message": "아무 곳이나 추천해줘", "history": [], "mode": "recommend"},
    ).json()
    shown_titles = ", ".join(source["title"] for source in first["sources"])
    second = client.post(
        "/api/chat",
        json={
            "message": "다른 곳 보여줘",
            "history": [
                {"role": "user", "content": "아무 곳이나 추천해줘"},
                {
                    "role": "assistant",
                    "content": f"{first['answer']}\n[화면에 표시된 결과: {shown_titles}]",
                },
            ],
            "mode": "recommend",
        },
    ).json()

    assert first["sources"]
    assert second["sources"]
    assert {source["id"] for source in first["sources"]}.isdisjoint(
        source["id"] for source in second["sources"]
    )


def test_review_count_question_stays_in_recommendation_mode(monkeypatch) -> None:
    monkeypatch.setattr(data_service, "_enrich_location", skip_database_enrichment)

    response = client.post(
        "/api/chat",
        json={"message": "리뷰많은 음식점 알려줘", "history": [], "mode": "recommend"},
    )

    assert response.status_code == 200
    assert response.json()["mode"] == "recommend"
    assert all(source["category"] == "음식점" for source in response.json()["sources"])


def test_post_word_automatically_switches_to_post_search(monkeypatch) -> None:
    monkeypatch.setattr(data_service, "_enrich_location", skip_database_enrichment)

    async def fake_posts(query, limit=4):
        return [
            {
                "type": "post",
                "id": "9",
                "title": "칼국수 후기",
                "category": "맛집",
                "rating": 5,
                "excerpt": "좋았어요.",
                "view_count": 7,
            }
        ]

    monkeypatch.setattr(data_service, "search_posts", fake_posts)
    response = client.post(
        "/api/chat",
        json={"message": "칼국수 후기 찾아줘", "history": [], "mode": "recommend"},
    )

    assert response.status_code == 200
    assert response.json()["mode"] == "posts"
    assert any(source["type"] == "post" for source in response.json()["sources"])


def test_missing_key_is_visible_in_response(monkeypatch) -> None:
    monkeypatch.setattr(data_service, "_enrich_location", skip_database_enrichment)
    monkeypatch.setattr(chat_service, "openai_client", None)

    response = client.post(
        "/api/chat",
        json={"message": "대전 숙소 알려줘", "history": [], "mode": "recommend"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["engine"] == "local"
    assert body["fallback"] is True
    assert body["error_code"] == "api_key_missing"
    assert "FastAPI 재시작" in body["notice"]


def test_openai_intent_analysis_grounds_the_answer(monkeypatch) -> None:
    monkeypatch.setattr(data_service, "_enrich_location", skip_database_enrichment)

    class FakeResponses:
        def __init__(self):
            self.calls = []

        async def parse(self, **kwargs):
            self.calls.append(("parse", kwargs))
            return SimpleNamespace(
                output_parsed=QueryIntent(
                    mode="recommend",
                    categories=["숙박"],
                    regions=["대전"],
                    keywords=[],
                )
            )

        async def create(self, **kwargs):
            self.calls.append(("create", kwargs))
            return SimpleNamespace(output_text="대전 숙박 데이터를 기준으로 안내할게요.")

    fake_responses = FakeResponses()
    monkeypatch.setattr(
        chat_service,
        "openai_client",
        SimpleNamespace(responses=fake_responses),
    )

    response = client.post(
        "/api/chat",
        json={"message": "대전에서 밤을 보낼 만한 데 있어?", "history": [], "mode": "recommend"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["engine"] == "openai"
    assert body["fallback"] is False
    assert body["sources"]
    assert all(source["category"] == "숙박" for source in body["sources"])
    assert [name for name, _ in fake_responses.calls] == ["parse", "create"]
    assert all(kwargs["model"] == "gpt-5-mini" for _, kwargs in fake_responses.calls)
    assert all("tools" not in kwargs for _, kwargs in fake_responses.calls)


def test_openai_failure_returns_search_results_and_reason(monkeypatch) -> None:
    monkeypatch.setattr(data_service, "_enrich_location", skip_database_enrichment)

    class BrokenResponses:
        async def parse(self, **kwargs):
            raise RuntimeError("test failure")

    monkeypatch.setattr(
        chat_service,
        "openai_client",
        SimpleNamespace(responses=BrokenResponses()),
    )
    response = client.post(
        "/api/chat",
        json={"message": "대전 숙소 알려줘", "history": [], "mode": "recommend"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["sources"]
    assert body["engine"] == "local"
    assert body["error_code"] == "intent_or_response_error"
    assert body["notice"]


def test_empty_message_is_rejected() -> None:
    response = client.post("/api/chat", json={"message": "", "history": []})
    assert response.status_code == 422
