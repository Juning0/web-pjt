from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.routers import posts, comments, locations

# 앱 시작 시 테이블 생성 (없으면 생성).
# 실제 초기 데이터 적재는 seed.py 로 수행.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LocalHub API",
    description="대전/충청권 지역 정보 공유 커뮤니티 백엔드",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(locations.router)
app.include_router(posts.router)
app.include_router(comments.router)
# 챗봇 라우터(현준님)는 이후 app.include_router(chat.router) 로 추가


@app.get("/")
def health():
    return {"status": "ok", "service": "LocalHub API"}
