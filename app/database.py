from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

# check_same_thread=False : FastAPI는 여러 스레드에서 동작하므로 SQLite 기본 제약 해제
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
)


# SQLite 동시성 대비: WAL 모드 + busy_timeout
# (요구사항 검토의견: "파일 기반 SQLite 특성상 데드락 우려로 동시성 대비책 마련")
@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_conn, _):
    cur = dbapi_conn.cursor()
    cur.execute("PRAGMA journal_mode=WAL;")     # 읽기/쓰기 동시성 향상
    cur.execute("PRAGMA busy_timeout=5000;")     # 잠김 시 5초까지 대기 후 에러
    cur.execute("PRAGMA foreign_keys=ON;")       # FK 제약 활성화
    cur.close()


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_db():
    """FastAPI 의존성 주입용 DB 세션 제너레이터."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
