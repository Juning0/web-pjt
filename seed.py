"""
제공 JSON(한국관광공사 TourAPI) 8개 파일을 locations 테이블에 적재한다.
실행: python seed.py
결과: .env 의 DATABASE_URL 경로에 초기 데이터가 포함된 .db 생성 (제출 산출물).

데이터 파일은 ./data/ 폴더에 아래 이름으로 위치시킨다:
  대전_충청권_관광지.json, 대전_충청권_레포츠.json, ... (8개)
"""
import json
from pathlib import Path

from app.database import Base, engine, SessionLocal
from app.models import Location

DATA_DIR = Path(__file__).parent / "data"

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


def run():
    # 테이블 재생성 (개발 편의: 매번 깨끗하게 시드)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # locations 만 초기화 (posts/comments 는 건드리지 않음)
    deleted = db.query(Location).delete()
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
    db.close()


if __name__ == "__main__":
    run()
