# LocalHub 챗봇 구현 안내

## 구성

| 위치 | 역할 |
|------|------|
| `localhub-backend/app/routers/chat.py` | `/api/chat`, `/api/chat/health` 라우터 |
| `localhub-backend/app/chat_service.py` | 질문 의도 분석, OpenAI 답변, 로컬 대체 답변 |
| `localhub-backend/app/chat_data_service.py` | 관광 JSON 검색, 평점·게시글 SQLite 조회 |
| `localhub-backend/app/chat_schemas.py` | 요청·응답 타입 검증 |
| `localhub-frontend/src/api/chat.js` | FastAPI 호출과 오류·시간초과 처리 |
| `localhub-frontend/src/components/ChatWidget.vue` | 플로팅 UI, 모바일 화면, 대화 히스토리 |
| `localhub-frontend/src/views/MapView.vue` | 챗봇 장소 좌표를 카카오 지도 마커로 표시 |

## 처리 흐름

1. Vue가 `POST /api/chat`으로 현재 질문, 최근 대화, 선택 모드를 보냅니다.
2. 백엔드가 지역·카테고리·검색어를 판별합니다.
3. 프로젝트의 관광 JSON에서 후보를 찾고 SQLite의 평점·커뮤니티 게시글을 결합합니다.
4. OpenAI `gpt-5-mini`가 검색 결과 JSON 안의 사실만 사용해 답합니다.
5. 키나 네트워크에 문제가 있으면 같은 검색 결과를 로컬 형식으로 반환합니다.
6. Vue가 답변과 출처 카드를 저장하고, 장소는 내부 `/map` 화면의 좌표 마커로, 게시글은 게시판 검색으로 연결합니다.

## 제한 사항

- 모델은 `ALLOWED_MODEL = "gpt-5-mini"`로 고정됩니다.
- OpenAI 도구와 웹 검색은 사용하지 않으며 질의응답만 합니다.
- 축제 날짜 필드가 비어 있으면 일정을 만들어 내지 않습니다.
- 평점이 없으면 `평점 정보 없음`으로 표시합니다.
- 여러 카테고리를 `하나씩` 요청하면 카테고리별 정확히 한 곳씩 반환합니다.
- API 키는 백엔드 `.env` 또는 Render 환경변수에만 저장합니다.

## 테스트

```bash
cd localhub-backend
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

현재 챗봇 회귀 테스트는 자연어 카테고리, 숙박 복합어, 다중 카테고리 균형, 후속 질문, OpenAI 오류 처리 등을 포함합니다.
