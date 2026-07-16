from typing import Literal

from pydantic import BaseModel, Field


ChatMode = Literal["auto", "recommend", "posts", "faq"]
ResolvedChatMode = Literal["recommend", "posts", "faq"]
LocationCategory = Literal[
    "관광지",
    "레포츠",
    "문화시설",
    "쇼핑",
    "숙박",
    "여행코스",
    "음식점",
    "축제공연행사",
]
IntentRegion = Literal["대전", "세종", "공주", "논산", "계룡", "옥천", "충청남도", "충청북도"]


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=2_000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=800)
    history: list[ChatMessage] = Field(default_factory=list, max_length=20)
    mode: ChatMode = "auto"


class QueryIntent(BaseModel):
    mode: ResolvedChatMode = "recommend"
    categories: list[LocationCategory] = Field(default_factory=list, max_length=3)
    regions: list[IntentRegion] = Field(default_factory=list, max_length=3)
    keywords: list[str] = Field(default_factory=list, max_length=5)
    wants_rating: bool = False
    wants_schedule: bool = False
    is_follow_up: bool = False


class ChatSource(BaseModel):
    type: Literal["location", "post"]
    id: str
    title: str
    category: str = ""
    address: str = ""
    rating: float | None = None
    review_count: int = 0
    image_url: str = ""
    latitude: float | None = None
    longitude: float | None = None
    start_date: str = ""
    end_date: str = ""
    excerpt: str = ""
    view_count: int = 0


class ChatResponse(BaseModel):
    answer: str
    sources: list[ChatSource] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    mode: ResolvedChatMode = "recommend"
    fallback: bool = False
    engine: Literal["openai", "local"] = "local"
    notice: str = ""
    error_code: str = ""


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    locations_loaded: int
    openai_configured: bool
    model: str
    data_source: str
