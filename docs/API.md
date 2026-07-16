# LocalHub API 명세

대전/충청권 지역 정보 공유 커뮤니티 백엔드 API 문서.

- Base URL (로컬): `http://127.0.0.1:8000`
- Swagger 자동 문서: `http://127.0.0.1:8000/docs`
- 공통: 요청/응답 모두 `application/json`, 인증 없음(익명 서비스)

---

## 공통 규칙

### 카테고리 값
`관광지` · `레포츠` · `문화시설` · `쇼핑` · `숙박` · `여행코스` · `음식점` · `축제공연행사`

### 비밀번호 정책
- 게시글·댓글은 작성 시 등록한 **수정용 비밀번호(평문)** 로만 수정/삭제 권한 확인
- RFP III-2-나 기준 의도된 설계(암호화 없음). 비밀번호 분실 시 수정/삭제 불가

### 에러 응답 형식
```json
{ "detail": "에러 메시지" }
```

| 상태 코드 | 의미 |
|-----------|------|
| 400 | 잘못된 요청 |
| 403 | 비밀번호 불일치 |
| 404 | 리소스 없음 |
| 422 | 입력값 검증 실패 (필수 누락, 범위 초과 등) |

---

## 1. 공공데이터 (locations) — 읽기 전용

한국관광공사 TourAPI 데이터. 조회만 가능.

### 1-1. 목록 조회
```
GET /api/locations
```

| 쿼리 파라미터 | 타입 | 기본값 | 설명 |
|---------------|------|--------|------|
| `category` | string | (전체) | 카테고리 필터 |
| `keyword` | string | (없음) | 장소명 검색 |
| `page` | int | 1 | 페이지 번호 (1~) |
| `size` | int | 20 | 페이지당 개수 (1~100) |

**응답 200**
```json
{
  "total": 335,
  "page": 1,
  "size": 20,
  "items": [
    {
      "content_id": "741957",
      "category": "관광지",
      "title": "대전솔로몬로파크",
      "addr1": "대전광역시 유성구 엑스포로 219-39 (원촌동)",
      "tel": "",
      "lng": 127.4015597328,
      "lat": 36.3773585309,
      "first_image": "https://tong.visitkorea.or.kr/..."
    }
  ]
}
```
> `first_image` 가 빈 문자열이면 이미지 없음 → FE에서 placeholder 처리 필요

### 1-2. 상세 조회 (장소별 평균 평점 포함)
```
GET /api/locations/{content_id}
```

**응답 200**
```json
{
  "content_id": "741957",
  "category": "관광지",
  "title": "대전솔로몬로파크",
  "addr1": "대전광역시 유성구 엑스포로 219-39 (원촌동)",
  "tel": "",
  "lng": 127.4015597328,
  "lat": 36.3773585309,
  "first_image": "https://tong.visitkorea.or.kr/...",
  "avg_rating": 4.5,
  "review_count": 2
}
```
> `avg_rating` 은 이 장소를 `location_id` 로 지정한 게시글들의 평점 평균. 리뷰 없으면 `null`

---

## 2. 게시판 (posts)

### 2-1. 목록 조회
```
GET /api/posts
```

| 쿼리 파라미터 | 타입 | 기본값 | 설명 |
|---------------|------|--------|------|
| `category` | string | (전체) | 카테고리 필터 |
| `keyword` | string | (없음) | 제목·내용 검색 |
| `sort` | string | `latest` | 정렬: `latest`(최신) / `rating`(평점순) / `views`(조회순) |
| `page` | int | 1 | 페이지 번호 |
| `size` | int | 10 | 페이지당 개수 (1~50) |

**응답 200**
```json
{
  "total": 42,
  "page": 1,
  "size": 10,
  "items": [
    {
      "id": 1,
      "category": "음식점",
      "title": "성심당 꼭 가세요",
      "rating": 5,
      "view_count": 12,
      "created_at": "2026-07-14T08:25:02"
    }
  ]
}
```
> 목록에는 본문(`content`) 미포함

### 2-2. 상세 조회 (조회수 +1)
```
GET /api/posts/{id}
```
> 호출할 때마다 `view_count` 가 1 증가

**응답 200**
```json
{
  "id": 1,
  "category": "음식점",
  "title": "성심당 꼭 가세요",
  "content": "대전 오면 여기부터",
  "rating": 5,
  "view_count": 13,
  "location_id": null,
  "created_at": "2026-07-14T08:25:02",
  "updated_at": "2026-07-14T08:25:02",
  "comments": [
    { "id": 1, "post_id": 1, "content": "동의합니다", "created_at": "2026-07-14T09:00:00" }
  ]
}
```
> 응답에 `password` 는 절대 포함되지 않음

### 2-3. 작성
```
POST /api/posts
```

**요청 body**
```json
{
  "category": "음식점",
  "title": "성심당 꼭 가세요",
  "content": "대전 오면 여기부터",
  "password": "1234",
  "rating": 5,
  "location_id": null
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `category` | string | ✅ | 카테고리 |
| `title` | string | ✅ | 제목 (1~200자) |
| `content` | string | ✅ | 내용 |
| `password` | string | ✅ | 수정용 비밀번호 |
| `rating` | int | ❌ | 평점 (1~5) |
| `location_id` | string | ❌ | 리뷰 대상 장소의 content_id |

**응답 201** → 2-2 상세와 동일 형식

### 2-4. 수정 (비밀번호 필요)
```
PUT /api/posts/{id}
```

**요청 body** — `password` 필수, 나머지는 바꿀 것만
```json
{ "password": "1234", "title": "수정된 제목", "content": "수정된 내용", "rating": 4 }
```

- **200**: 수정 성공 → 상세 형식 반환
- **403**: 비밀번호 불일치
- **404**: 게시글 없음

### 2-5. 삭제 (비밀번호 필요)
```
POST /api/posts/{id}/delete
```
> DELETE 메서드 대신 POST 사용 (body로 비밀번호를 안정적으로 전달하기 위함)

**요청 body**
```json
{ "password": "1234" }
```

- **204**: 삭제 성공 (본문 없음)
- **403**: 비밀번호 불일치
- **404**: 게시글 없음

---

## 3. 댓글 (comments)

### 3-1. 작성
```
POST /api/posts/{post_id}/comments
```

**요청 body**
```json
{ "content": "동의합니다", "password": "1234" }
```

**응답 201**
```json
{ "id": 1, "post_id": 1, "content": "동의합니다", "created_at": "2026-07-14T09:00:00" }
```

### 3-2. 삭제 (비밀번호 필요)
```
POST /api/posts/comments/{comment_id}/delete
```

**요청 body**
```json
{ "password": "1234" }
```

- **204**: 삭제 성공
- **403**: 비밀번호 불일치
- **404**: 댓글 없음

---

## 4. 챗봇 (chat)

### 4-1. 챗봇 상태

```text
GET /api/chat/health
```

키 값 자체는 반환하지 않으며, 설정 여부만 확인할 수 있습니다.

```json
{
  "status": "ok",
  "locations_loaded": 1365,
  "openai_configured": true,
  "model": "gpt-5-mini",
  "data_source": "bundled JSON + LocalHub SQLite"
}
```

### 4-2. 자연어 질의응답

```text
POST /api/chat
```

**요청 body**

```json
{
  "message": "대전 관광지랑 음식점 숙소 하나씩 알려줘",
  "history": [],
  "mode": "auto"
}
```

`mode`는 `auto`, `recommend`, `posts`, `faq` 중 하나이며 기본값은 `auto`입니다. `history`에는 최근 사용자·챗봇 메시지를 최대 20개 전달합니다.

**응답 200 주요 필드**

| 필드 | 설명 |
|------|------|
| `answer` | 사용자에게 표시할 한국어 답변 |
| `sources` | 장소 또는 게시글 카드 데이터 |
| `suggestions` | 후속 질문 버튼 |
| `engine` | `openai` 또는 로컬 검색 답변인 `local` |
| `notice` | 키·권한·한도·연결 오류 안내 |
| `error_code` | 프론트엔드에서 구분 가능한 오류 코드 |

챗봇은 제공 JSON, LocalHub 평점, LocalHub 게시글만 근거로 답하며 웹 검색·예약·게시글 작성은 수행하지 않습니다.

---

## 데이터 출처

한국관광공사 Tour API(TourAPI 4.0) 활용.
출처: 한국관광공사 (https://www.data.go.kr/data/15101578/openapi.do)
라이선스: 공공누리 제3유형 (출처표시 + 변경금지)
