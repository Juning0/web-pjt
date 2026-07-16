from pathlib import Path

from fastapi import APIRouter, HTTPException, Request

from app.chat_rate_limiter import ChatRateLimiter
from app.chat_data_service import LocalHubDataService
from app.chat_schemas import ChatRequest, ChatResponse, HealthResponse
from app.chat_service import ALLOWED_MODEL, ChatService
from app.config import settings


router = APIRouter(prefix="/api", tags=["chat"])
PROJECT_DIR = Path(__file__).resolve().parents[3]

data_service = LocalHubDataService(data_dir=PROJECT_DIR / "data")
chat_service = ChatService(
    data_service,
    openai_api_key=settings.OPENAI_API_KEY.strip(),
)

chat_rate_limiter = ChatRateLimiter(
    requests_per_window=settings.CHAT_RATE_LIMIT_REQUESTS,
    window_seconds=settings.CHAT_RATE_LIMIT_WINDOW_SECONDS,
    daily_per_client=settings.CHAT_DAILY_LIMIT_PER_CLIENT,
    daily_global=settings.CHAT_DAILY_LIMIT_GLOBAL,
)

def get_client_id(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for", "")

    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    if request.client:
        return request.client.host

    return "unknown"


@router.get("/chat/health", response_model=HealthResponse)
@router.get("/health", response_model=HealthResponse, include_in_schema=False)
async def health_check() -> HealthResponse:
    """챗봇 데이터와 OpenAI 설정 상태를 확인한다. 키 값은 노출하지 않는다."""
    return HealthResponse(
        locations_loaded=len(data_service.locations),
        openai_configured=bool(settings.OPENAI_API_KEY.strip()),
        model=ALLOWED_MODEL,
        data_source="bundled JSON + LocalHub SQLite",
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, request: Request) -> ChatResponse:
    """관광 데이터·평점·커뮤니티를 근거로 질의응답한다."""

    if settings.CHAT_RATE_LIMIT_ENABLED:
        allowed, retry_after, message = await chat_rate_limiter.check(
            get_client_id(request)
        )

        if not allowed:
            raise HTTPException(
                status_code=429,
                detail=message,
                headers={"Retry-After": str(retry_after)},
            )

    return await chat_service.answer(payload)