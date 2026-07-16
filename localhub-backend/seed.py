"""
제공 JSON(한국관광공사 TourAPI) 8개 파일을 locations 테이블에 적재한다.
실행: python seed.py
결과: .env 의 DATABASE_URL 경로에 초기 데이터가 포함된 .db 생성 (제출 산출물).

데이터 파일은 ./data/ 폴더에 아래 이름으로 위치시킨다:
  대전_충청권_관광지.json, 대전_충청권_레포츠.json, ... (8개)
"""
import json
from datetime import datetime, timedelta
from pathlib import Path

from app.database import Base, engine, SessionLocal
from app.models import Location, Post

DATA_DIR = Path(__file__).parent.parent / "data"

FILES = [
    "대전_충청권_관광지.json",
    "대전_충청권_레포츠.json",
    "대전_충청권_문화시설.json",
    "대전_충청권_쇼핑.json",
    "대전_충청권_숙박.json",
    "대전_충청권_여행코스.json",
    "대전_충청권_음식점.json",
    "대전_충청권_축제공연행사.json",
]


def to_float(v):
    """mapx/mapy 는 string 이라 float 변환. 빈 값이면 None."""
    try:
        return float(v) if str(v).strip() else None
    except (ValueError, TypeError):
        return None


# 대전에서 실제로 유명한 장소 20곳 위주로 넣은 데모 리뷰. password는 이 값으로만 식별해서
# seed.py를 다시 돌려도 실사용자 게시글은 안 건드리고 데모 리뷰만 지웠다 다시 넣는다.
DEMO_REVIEW_PASSWORD = "demo-seed-1234"

# 장소별 detail은 실제로 있을 법한 후기 문장 5개씩. 아래 build_demo_reviews()가
# 장소당 10건(문장 2회씩 순환)씩 만들어 총 20곳 * 10건 = 200건을 생성한다.
FAMOUS_LOCATIONS = [
    dict(location_id="1796079", category="음식점", place="성심당", details=[
        "튀김소보로가 진짜 맛있어요.",
        "보문산메아리도 별미예요.",
        "웨이팅이 있어도 갈 가치가 있어요.",
        "대전 여행 필수 코스입니다.",
        "빵 종류가 다양해서 고르는 재미가 있어요.",
    ]),
    dict(location_id="125994", category="관광지", place="대전엑스포과학공원", details=[
        "한빛탑 보면서 산책하기 좋아요.",
        "아이들이랑 오기 딱 좋은 곳이에요.",
        "야경이 예뻐서 저녁에 가도 좋아요.",
        "과학관이랑 같이 둘러보기 좋아요.",
        "잔디밭이 넓어서 돗자리 펴기 좋아요.",
    ]),
    dict(location_id="741658", category="관광지", place="한밭수목원", details=[
        "도심 속에서 산책하기 정말 좋아요.",
        "계절마다 분위기가 달라서 자주 가게 돼요.",
        "반려동물이랑 산책하기도 좋아요.",
        "온실 구경하는 재미도 있어요.",
        "주차하기 편해서 좋았어요.",
    ]),
    dict(location_id="127641", category="관광지", place="대전오월드", details=[
        "플라워랜드 시즌에 가면 완전 예뻐요.",
        "동물원 구경하는 재미가 쏠쏠해요.",
        "놀이기구 종류가 다양해서 좋아요.",
        "아이들이 정말 좋아했어요.",
        "하루 코스로 딱 좋아요.",
    ]),
    dict(location_id="126838", category="관광지", place="뿌리공원", details=[
        "성씨별 조형물 구경하는 재미가 있어요.",
        "가족 단위로 가기 좋은 곳이에요.",
        "넓어서 산책하기 좋아요.",
        "효 체험 프로그램이 인상 깊었어요.",
        "단풍철에 가면 정말 예뻐요.",
    ]),
    dict(location_id="2760707", category="관광지", place="유성온천공원", details=[
        "무료 족욕 체험이 좋았어요.",
        "산책하다가 쉬어가기 좋아요.",
        "겨울에 특히 추천합니다.",
        "야간에 조명이 예뻐요.",
        "근처 맛집도 많아서 좋아요.",
    ]),
    dict(location_id="129438", category="관광지", place="장태산자연휴양림", details=[
        "메타세쿼이아 숲길이 인상적이었어요.",
        "스카이웨이에서 보는 뷰가 최고예요.",
        "캠핑장도 잘 되어있어요.",
        "공기가 맑아서 힐링됐어요.",
        "아이들이랑 숲 체험하기 좋아요.",
    ]),
    dict(location_id="1720749", category="레포츠", place="계족산 황톳길", details=[
        "맨발로 걸으니 스트레스가 풀려요.",
        "세족장이 잘 되어있어요.",
        "숲길이 잘 정비되어 있어요.",
        "주말마다 사람이 많아요.",
        "가볍게 산책하기 좋아요.",
    ]),
    dict(location_id="1964622", category="관광지", place="스카이로드", details=[
        "LED 영상 나올 때 진짜 예뻐요.",
        "은행동 갈 때 꼭 들르는 곳이에요.",
        "사진 찍기 좋은 명소예요.",
        "밤에 보면 더 예뻐요.",
        "주변에 먹거리도 많아요.",
    ]),
    dict(location_id="126846", category="관광지", place="대청호", details=[
        "드라이브 코스로 최고예요.",
        "둘레길 따라 걷기 좋아요.",
        "노을 질 때 풍경이 예술이에요.",
        "자전거 타기도 좋아요.",
        "사진 찍기 좋은 포인트가 많아요.",
    ]),
    dict(location_id="130551", category="문화시설", place="대전시립미술관", details=[
        "기획전 퀄리티가 항상 좋아요.",
        "조용히 힐링하기 좋은 곳이에요.",
        "아이랑 같이 가도 좋아요.",
        "카페도 분위기가 좋아요.",
        "전시 구성이 알차요.",
    ]),
    dict(location_id="130069", category="문화시설", place="카이스트 캠퍼스", details=[
        "캠퍼스가 넓고 조용해요.",
        "산책하기 좋은 분위기예요.",
        "가끔 공연도 열려요.",
        "사진 찍기 좋은 장소예요.",
        "조용히 시간 보내기 좋아요.",
    ]),
    dict(location_id="2905382", category="음식점", place="홍두깨칼국수", details=[
        "국물이 진하고 깊어요.",
        "면발이 쫄깃해서 좋아요.",
        "양이 푸짐해서 만족스러워요.",
        "반찬도 깔끔하게 나와요.",
        "가격 대비 만족도가 높아요.",
    ]),
    dict(location_id="2582526", category="음식점", place="풍년삼계탕", details=[
        "삼계탕 국물이 깊은 맛이에요.",
        "여름 보양식으로 딱이에요.",
        "닭이 부드럽고 실해요.",
        "찹쌀죽도 같이 나와서 좋아요.",
        "가족 식사로도 좋아요.",
    ]),
    dict(location_id="2581540", category="음식점", place="신선만두애", details=[
        "만두 속이 꽉 차 있어요.",
        "피가 얇아서 맛있어요.",
        "국물 만두도 별미예요.",
        "포장해가기도 좋아요.",
        "가격도 합리적이에요.",
    ]),
    dict(location_id="1270240", category="축제공연행사", place="유성온천문화축제", details=[
        "온천 체험 프로그램이 다양해요.",
        "볼거리가 많아서 시간 가는 줄 몰랐어요.",
        "가족끼리 가기 좋아요.",
        "야간 프로그램도 볼만해요.",
        "겨울철 축제로 딱이에요.",
    ]),
    dict(location_id="3085028", category="숙박", place="저스트슬립호텔 유성온천점", details=[
        "온천 근처라 접근성이 좋아요.",
        "객실이 깔끔했어요.",
        "직원분들이 친절했어요.",
        "가성비가 좋은 숙소예요.",
        "온천 여행 할 때 묵기 좋아요.",
    ]),
    dict(location_id="1434477", category="쇼핑", place="대전 중앙시장", details=[
        "먹거리가 정말 다양해요.",
        "옛날 시장 감성이 느껴져요.",
        "가격이 착해서 좋아요.",
        "구경하는 재미가 쏠쏠해요.",
        "활기찬 분위기가 좋아요.",
    ]),
    dict(location_id="1927292", category="여행코스", place="장태산 여행코스", details=[
        "코스가 알차게 구성되어 있어요.",
        "하루 코스로 딱 좋았어요.",
        "자연을 느끼기 좋은 코스예요.",
        "천천히 둘러보기 좋아요.",
        "사진 찍을 곳이 많아요.",
    ]),
    dict(location_id="2931882", category="관광지", place="대전신세계 아트앤사이언스", details=[
        "스카이 전망대 뷰가 좋아요.",
        "쇼핑하기도 편해요.",
        "아이들이랑 놀거리도 많아요.",
        "맛집도 많아서 좋아요.",
        "주차가 편리해요.",
    ]),
]

NICKNAMES = [
    "빵순이", "대전토박이", "두아이맘", "산책러버", "주말나들이", "효자손자", "온천마니아", "등산초보",
    "맨발산책", "야경덕후", "드라이브광", "전시덕후", "산책객", "칼국수러버", "보양식매니아", "만두킬러",
    "축제매니아", "숙박여행자", "시장투어러", "여행코스러", "힐링추구자", "사진러버", "맛집헌터", "동네주민",
    "여행에미친자", "가족여행러", "혼행러", "커플여행자", "반려동물집사", "캠핑러", "자연인", "도시탈출러",
    "봄나들이족", "가을단풍러", "겨울여행자", "여름휴가족", "주말러너", "산책메이트", "힐링족", "소소한행복",
]

TITLE_TEMPLATES = [
    "또 오고 싶은 곳이에요", "생각보다 좋았어요", "기대 이상이었습니다", "가족들이랑 다녀왔어요",
    "친구 추천으로 가봤어요", "혼자 가기도 좋아요", "데이트 코스로 추천", "제대로 힐링하고 왔어요",
    "다음에 또 올 예정입니다", "만족스러운 방문이었어요",
]

RATING_CYCLE = [5, 5, 4, 5, 4, 3, 5, 4, 5, 4]


def build_demo_reviews():
    """장소 20곳 * 10건 = 총 200건의 데모 리뷰를 생성한다."""
    reviews = []
    for loc_idx, loc in enumerate(FAMOUS_LOCATIONS):
        for i in range(10):
            body = loc["details"][i % len(loc["details"])]
            title_phrase = TITLE_TEMPLATES[i % len(TITLE_TEMPLATES)]
            nickname = NICKNAMES[(loc_idx * 3 + i) % len(NICKNAMES)]
            reviews.append(dict(
                location_id=loc["location_id"],
                category=loc["category"],
                title=f"{loc['place']} {title_phrase}",
                rating=RATING_CYCLE[i % len(RATING_CYCLE)],
                nickname=nickname,
                body=body,
            ))
    return reviews


DEMO_REVIEWS = build_demo_reviews()


def seed_reviews(db):
    """DEMO_REVIEWS를 posts 테이블에 적재. password로만 식별해 데모 리뷰만 지웠다 다시 넣는다."""
    deleted = db.query(Post).filter(Post.password == DEMO_REVIEW_PASSWORD).delete()
    if deleted:
        print(f"기존 데모 리뷰 {deleted}건 삭제")

    base_time = datetime.utcnow()
    for i, review in enumerate(DEMO_REVIEWS):
        # 최근 ~2개월 사이에 흩어져 등록된 것처럼 보이도록 날짜를 순환시킨다.
        created = base_time - timedelta(days=i % 60, hours=(i * 5) % 24)
        db.add(Post(
            category=review["category"],
            title=review["title"],
            content=f"[{review['nickname']}] {review['body']}",
            password=DEMO_REVIEW_PASSWORD,
            rating=review["rating"],
            location_id=review["location_id"],
            created_at=created,
            updated_at=created,
        ))
    db.commit()
    print(f"데모 리뷰 {len(DEMO_REVIEWS)}건 적재")


def run():
    # 테이블 재생성 (개발 편의: 매번 깨끗하게 시드)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # locations 만 초기화 (posts/comments 는 건드리지 않음).
    # 단, 리뷰(posts.location_id)가 참조 중인 장소는 FK 제약 때문에 지울 수 없어
    # 참조되지 않는 장소만 지우고 나머지는 아래 merge()로 갱신한다.
    referenced_ids = {
        row[0] for row in db.query(Post.location_id).filter(Post.location_id.isnot(None)).distinct()
    }
    deleted = (
        db.query(Location)
        .filter(~Location.content_id.in_(referenced_ids))
        .delete(synchronize_session=False)
    )
    db.commit()
    if deleted:
        print(f"기존 locations {deleted}건 삭제")

    total = 0
    for fname in FILES:
        fpath = DATA_DIR / fname
        if not fpath.exists():
            print(f"  [건너뜀] 파일 없음: {fpath}")
            continue

        with open(fpath, encoding="utf-8") as f:
            data = json.load(f)

        category = data["contentType"]          # 예: '관광지'
        content_type_id = data["contentTypeId"]  # 예: '12'
        items = data.get("items", [])

        for it in items:
            db.merge(Location(   # merge: content_id 중복 시 덮어씀
                content_id=it["contentid"],
                content_type_id=content_type_id,
                category=category,
                title=it.get("title", ""),
                addr1=it.get("addr1", ""),
                addr2=it.get("addr2", ""),
                zipcode=it.get("zipcode", ""),
                tel=it.get("tel", ""),
                lng=to_float(it.get("mapx")),
                lat=to_float(it.get("mapy")),
                first_image=it.get("firstimage", ""),
                first_image2=it.get("firstimage2", ""),
                created_time=it.get("createdtime", ""),
                modified_time=it.get("modifiedtime", ""),
            ))
        db.commit()
        print(f"  {category:<10} {len(items):>4}건 적재")
        total += len(items)

    print(f"\n완료: 총 {total}건 적재")

    seed_reviews(db)
    db.close()


if __name__ == "__main__":
    run()
