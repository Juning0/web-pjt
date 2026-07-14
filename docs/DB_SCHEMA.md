# LocalHub DB 스키마

- DBMS: **SQLite** (파일 기반, `localhub.db`)
- ORM: **SQLAlchemy 2.0**
- 동시성 설정: `PRAGMA journal_mode=WAL`, `busy_timeout=5000`, `foreign_keys=ON`
  (파일 기반 SQLite의 잠금/데드락 대비 — 요구사항 검토의견 반영)

---

## ERD 개요

```
locations (공공데이터, 읽기 전용)
   │ 1
   │
   │ N        (location_id, nullable)
posts (리뷰 게시글)
   │ 1
   │
   │ N
comments (댓글)
```

- `posts.location_id` → `locations.content_id` (N:1, nullable)
  → 특정 장소에 대한 리뷰일 때만 연결. 일반 게시글은 `null`
- `comments.post_id` → `posts.id` (N:1)
  → 게시글 삭제 시 댓글 함께 삭제 (cascade)

---

## 1. locations — 공공데이터 (읽기 전용)

한국관광공사 TourAPI JSON을 `seed.py` 로 적재. 애플리케이션에서 수정·삭제하지 않음.

| 컬럼 | 타입 | 제약 | 설명 |
|------|------|------|------|
| `content_id` | String | **PK** | 콘텐츠 고유 ID (원본 `contentid`) |
| `content_type_id` | String | NOT NULL | 콘텐츠 유형 ID (12/14/15/25/28/32/38/39) |
| `category` | String | NOT NULL, INDEX | 카테고리 한글명 (관광지·음식점 등) |
| `title` | String | NOT NULL | 장소명 |
| `addr1` | String | default `""` | 주소 (여행코스는 빈 값 가능) |
| `addr2` | String | default `""` | 상세 주소 |
| `zipcode` | String | default `""` | 우편번호 |
| `tel` | String | default `""` | 전화번호 (대부분 빈 값) |
| `lng` | Float | nullable | 경도 (원본 `mapx`, string→float 변환) |
| `lat` | Float | nullable | 위도 (원본 `mapy`) |
| `first_image` | String | default `""` | 대표 이미지 URL (빈 값=이미지 없음) |
| `first_image2` | String | default `""` | 썸네일 이미지 URL |
| `created_time` | String | default `""` | 원본 등록 시각 (YYYYMMDDHHmmss) |
| `modified_time` | String | default `""` | 원본 수정 시각 |

**적재 현황**: 총 1,365건 (관광지 335 · 음식점 516 · 쇼핑 258 · 문화시설 82 · 레포츠 68 · 숙박 52 · 여행코스 28 · 축제공연행사 26)

---

## 2. posts — 리뷰 게시글

익명 작성. 수정용 비밀번호(평문)로만 권한 확인.

| 컬럼 | 타입 | 제약 | 설명 |
|------|------|------|------|
| `id` | Integer | **PK**, AUTO | 게시글 ID |
| `category` | String | NOT NULL, INDEX | 게시판 카테고리 |
| `title` | String | NOT NULL | 제목 (1~200자) |
| `content` | Text | NOT NULL | 내용 |
| `password` | String | NOT NULL | 수정용 비밀번호 (**평문 저장, 의도된 설계**) |
| `rating` | Integer | nullable | 평점 1~5 (선택) |
| `view_count` | Integer | NOT NULL, default 0 | 조회수 |
| `location_id` | String | FK→locations.content_id, nullable, INDEX | 리뷰 대상 장소 |
| `created_at` | DateTime | NOT NULL | 작성 시각 |
| `updated_at` | DateTime | NOT NULL, onupdate | 수정 시각 (자동 갱신) |

- **장소별 평균 평점**: `rating` 을 `location_id` 로 GROUP BY 하여 `AVG()` 계산 (별도 컬럼 없음)
- **복합 인덱스**: `(category, created_at DESC)` — 카테고리별 최신순 목록 조회 최적화

---

## 3. comments — 댓글

| 컬럼 | 타입 | 제약 | 설명 |
|------|------|------|------|
| `id` | Integer | **PK**, AUTO | 댓글 ID |
| `post_id` | Integer | FK→posts.id, NOT NULL, INDEX | 소속 게시글 |
| `content` | Text | NOT NULL | 댓글 내용 |
| `password` | String | NOT NULL | 수정용 비밀번호 (평문) |
| `created_at` | DateTime | NOT NULL | 작성 시각 |

- 게시글 삭제 시 해당 댓글 자동 삭제 (`cascade="all, delete-orphan"`)

---

## 비밀번호 정책 (전 테이블 공통)

- `posts.password`, `comments.password` 는 **암호화 없이 평문 저장**
- RFP III-2-나 기준 **교육 목적의 의도된 설계**
- 수정/삭제 요청 시 입력값과 저장값의 단순 일치 비교로만 권한 확인
- API 응답에는 `password` 를 절대 포함하지 않음
