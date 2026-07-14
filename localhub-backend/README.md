# LocalHub Backend (FastAPI + SQLite)

대전/충청권 지역 정보 공유 커뮤니티 백엔드. 챗봇 제외 BE 전체.

## 기술 스택
FastAPI · SQLAlchemy 2.0 · SQLite · Pydantic v2 · uvicorn

## 프로젝트 구조
```
localhub-backend/
├── app/
│   ├── main.py          # FastAPI 진입점 + CORS
│   ├── config.py        # .env 로드 (pydantic-settings)
│   ├── database.py      # 엔진 + WAL 동시성 설정 + get_db
│   ├── models.py        # locations / posts / comments
│   ├── schemas.py       # Pydantic 요청·응답
│   ├── crud.py          # DB 조작 로직
│   └── routers/
│       ├── locations.py # 공공데이터 읽기 전용
│       ├── posts.py     # 게시판 CRUD (비번검증+평점)
│       └── comments.py  # 댓글 CRUD
├── data/                # 제공 JSON 8개 (여기에 넣기)
├── seed.py              # JSON → SQLite 적재
├── requirements.txt
├── .env.example         # 복사해서 .env 로 사용
└── .gitignore           # .env, *.db 제외
```

## 로컬 실행
```bash
# 1) 가상환경 + 의존성
python -m venv venv && source venv/bin/activate   # win: venv\Scripts\activate
pip install -r requirements.txt

# 2) 환경변수
cp .env.example .env

# 3) 제공 JSON 8개를 data/ 폴더에 복사

# 4) 초기 데이터 적재 (→ localhub.db 생성, 총 1,365건)
python seed.py

# 5) 서버 실행
uvicorn app.main:app --reload
# 문서: http://127.0.0.1:8000/docs
```

## API 요약

### 공공데이터 (읽기 전용)
| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/locations?category=&keyword=&page=&size=` | POI 목록 |
| GET | `/api/locations/{content_id}` | 상세 + 장소별 평균평점 |

`category` 값: 관광지 / 레포츠 / 문화시설 / 쇼핑 / 숙박 / 여행코스 / 음식점 / 축제공연행사

### 게시판
| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/posts?category=&keyword=&sort=&page=&size=` | 목록 (sort: latest/rating/views) |
| GET | `/api/posts/{id}` | 상세 (조회수 +1) |
| POST | `/api/posts` | 작성 |
| PUT | `/api/posts/{id}` | 수정 (비번 필요) |
| POST | `/api/posts/{id}/delete` | 삭제 (비번 필요) |

### 댓글
| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/api/posts/{id}/comments` | 작성 |
| POST | `/api/posts/comments/{id}/delete` | 삭제 (비번 필요) |

## Render 배포 메모
- Build: `pip install -r requirements.txt`
- Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- 환경변수(CORS_ORIGINS 등)는 Render 대시보드에 등록 (.env 커밋 금지)
- ⚠️ **무료 티어는 재배포/재시작 시 파일시스템이 초기화되어 SQLite가 날아감.**
  데모 중 게시글 유지가 필요하면 seed된 .db를 repo에 포함하거나 유료 디스크 고려.

## 설계 노트
- **비밀번호 평문 저장**: RFP III-2-나 의도된 설계 (암호화 X). 수정/삭제는 평문 일치로만 확인.
- **삭제에 POST /delete 사용**: DELETE 메서드 body가 프록시에서 무시될 수 있어 비번 전달 안정성 위해.
- **SQLite WAL + busy_timeout**: 파일 기반 동시성/데드락 대비 (요구사항 검토의견 반영).
- **장소별 평균 평점**: posts.rating을 location_id로 집계, 별도 컬럼 없음.

## 데이터 출처
한국관광공사 Tour API(TourAPI 4.0) · 공공누리 제3유형(출처표시+변경금지)
출처: https://www.data.go.kr/data/15101578/openapi.do
