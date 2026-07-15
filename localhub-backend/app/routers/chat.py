from pathlib import Path

from fastapi import APIRouter

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
async def chat(request: ChatRequest) -> ChatResponse:
    """관광 데이터·평점·커뮤니티를 근거로 질의응답한다."""
    return await chat_service.answer(request)
