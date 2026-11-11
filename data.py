# 파일 위치를 쉽게 다루는 Path 도구를 꺼내 와요.
from pathlib import Path

# 표(CSV)를 읽는 데 쓰는 pandas를 pd라는 짧은 이름으로 꺼내 와요.
import pandas as pd

# 이 파일(data.py)이 있는 폴더 안의 data/classes.csv를 가리켜요.
# 데이터를 프로젝트 안에 두어야 서버에 올릴 때 함께 올라가요.
CSV_PATH = Path(__file__).resolve().parent / "data" / "classes.csv"


# 칸이 비어 있으면(NaN) None으로, 아니면 원래 값을 그대로 돌려주는 도우미 함수예요.
def clean(value):
    # pd.isna는 "비어 있나요?"를 물어보는 함수예요.
    if pd.isna(value):
        # 비어 있으면 파이썬의 "없음"인 None을 돌려줘요.
        return None
    # 비어 있지 않으면 값을 그대로 돌려줘요.
    return value


# 가격 칸을 정수(예: 39000)로 바꾸는 도우미 함수예요. 비어 있으면 None이에요.
def to_price(value):
    # 먼저 빈칸을 None으로 바꿔요.
    value = clean(value)
    # 값이 없으면 None을 그대로 돌려줘요.
    if value is None:
        return None
    # 39000.0 같은 소수를 39000 같은 정수로 바꿔서 돌려줘요.
    return int(value)


# CSV 파일을 읽어서 클래스 목록(딕셔너리들의 리스트)으로 돌려주는 함수예요.
def load_classes():
    # CSV를 읽어요. utf-8-sig는 파일 맨 앞의 보이지 않는 표시(BOM)를 지워 줘요.
    df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")

    # 클래스들을 하나씩 담을 빈 리스트를 만들어요.
    classes = []

    # 표의 줄을 위에서부터 한 줄씩 꺼내요.
    for _, row in df.iterrows():
        # 정가를 정수 또는 None으로 꺼내요.
        list_price = to_price(row["정가"])
        # 할인가를 정수 또는 None으로 꺼내요.
        discount_price = to_price(row["할인가"])

        # 실제로 내는 가격: 할인가가 있으면 할인가, 없으면 정가예요.
        if discount_price is not None:
            price = discount_price
        else:
            price = list_price

        # 정가와 할인가가 둘 다 있고, 할인가가 더 싸면 "할인 중"이에요.
        on_sale = False
        if list_price is not None and discount_price is not None:
            if discount_price < list_price:
                on_sale = True

        # 리뷰 수를 꺼내요. 비어 있으면 0개로 봐요.
        review_count = clean(row["리뷰수"])
        if review_count is None:
            review_count = 0
        # 리뷰 수는 정수로 바꿔요.
        review_count = int(review_count)

        # 평점을 꺼내요. 비어 있으면 None이에요.
        rating = clean(row["평점"])
        # 리뷰가 하나도 없으면 평점도 없는 것으로 봐요.
        if review_count == 0:
            rating = None
        # 평점이 있으면 소수 첫째 자리까지 반올림해요. 예: 4.0
        if rating is not None:
            rating = round(float(rating), 1)

        # 한 클래스의 정보를 영어 이름표를 붙인 딕셔너리로 만들어요.
        item = {
            "id": int(row["id"]),
            "category": clean(row["카테고리"]),
            "region": clean(row["지역"]),
            "name": clean(row["클래스명"]),
            "list_price": list_price,
            "discount_price": discount_price,
            "price": price,
            "on_sale": on_sale,
            "rating": rating,
            "review_count": review_count,
        }

        # 완성된 클래스를 리스트에 넣어요.
        classes.append(item)

    # 다 모은 클래스 목록을 돌려줘요.
    return classes


# 번호(id)로 클래스 하나를 찾아서 돌려주는 함수예요. 없으면 None을 돌려줘요.
def get_class(class_id):
    # 클래스를 하나씩 꺼내요.
    for c in load_classes():
        # 번호가 같으면 그 클래스를 바로 돌려줘요.
        if c["id"] == class_id:
            return c
    # 끝까지 찾아도 없으면 "없음"을 돌려줘요.
    return None


# 카테고리 이름들을 겹치지 않게 모아서 가나다순으로 돌려주는 함수예요.
def get_categories():
    # 카테고리를 담을 빈 리스트를 만들어요.
    categories = []
    # 클래스를 하나씩 꺼내요.
    for c in load_classes():
        # 아직 리스트에 없는 카테고리면 넣어요.
        if c["category"] not in categories:
            categories.append(c["category"])
    # 가나다순으로 정렬해서 돌려줘요.
    return sorted(categories)


# 가격순 정렬에 쓰는 기준 함수예요. 가격이 없는 클래스는 맨 뒤로 보내요.
def price_key(c):
    # 가격이 없으면 (1, 0): 앞 숫자가 1이라 뒤로 가요.
    if c["price"] is None:
        return (1, 0)
    # 가격이 있으면 (0, 가격): 싼 것부터 앞에 와요.
    return (0, c["price"])


# 평점순 정렬에 쓰는 기준 함수예요. 평점이 없는 클래스는 맨 뒤로 보내요.
def rating_key(c):
    # 평점이 없으면 (1, 0, 0): 앞 숫자가 1이라 뒤로 가요.
    if c["rating"] is None:
        return (1, 0, 0)
    # 평점이 높은 것부터, 평점이 같으면 리뷰가 많은 것부터 오도록 마이너스를 붙여요.
    return (0, -c["rating"], -c["review_count"])


# 카테고리로 거르고(필터), 원하는 순서로 정렬하는 함수예요.
def filter_and_sort(classes, category=None, sort=None):
    # 카테고리를 고르지 않았으면 전체 목록을 그대로 써요.
    if not category:
        result = list(classes)
    # 카테고리를 골랐으면 이름이 똑같은 클래스만 골라 담아요.
    else:
        result = []
        for c in classes:
            if c["category"] == category:
                result.append(c)

    # "price"면 가격이 낮은 순서로 정렬해요.
    if sort == "price":
        result = sorted(result, key=price_key)
    # "rating"이면 평점이 높은 순서로 정렬해요.
    elif sort == "rating":
        result = sorted(result, key=rating_key)
    # 그 밖의 값이면 CSV에 적힌 순서 그대로 둬요.

    # 걸러지고 정렬된 목록을 돌려줘요.
    return result


# 전체 클래스의 통계(개수, 평균 가격, 평균 평점 등)를 모아서 돌려주는 함수예요.
def get_stats():
    # CSV에서 클래스 목록을 모두 읽어 와요.
    classes = load_classes()

    # 가격이 있는 클래스들의 가격을 모두 더할 상자예요. 처음엔 0이에요.
    price_sum = 0
    # 가격이 있는 클래스가 몇 개인지 셀 상자예요.
    price_count = 0
    # 가격이 없는('가격 문의') 클래스가 몇 개인지 셀 상자예요.
    price_inquiry_count = 0
    # 평점이 있는 클래스들의 평점을 모두 더할 상자예요.
    rating_sum = 0
    # 평점이 있는 클래스가 몇 개인지 셀 상자예요.
    rating_count = 0
    # 리뷰가 없는(평점이 없는) 클래스가 몇 개인지 셀 상자예요.
    no_review_count = 0

    # 클래스를 하나씩 꺼내요.
    for c in classes:
        # 가격이 없으면 '가격 문의' 개수를 하나 늘려요.
        if c["price"] is None:
            price_inquiry_count = price_inquiry_count + 1
        # 가격이 있으면 합계에 더하고, 개수를 하나 늘려요.
        else:
            price_sum = price_sum + c["price"]
            price_count = price_count + 1

        # 평점이 없으면 '리뷰 없음' 개수를 하나 늘려요.
        if c["rating"] is None:
            no_review_count = no_review_count + 1
        # 평점이 있으면 합계에 더하고, 개수를 하나 늘려요.
        else:
            rating_sum = rating_sum + c["rating"]
            rating_count = rating_count + 1

    # 가격이 있는 클래스가 하나라도 있으면 평균을 구해요. (0으로 나누면 오류가 나요!)
    if price_count > 0:
        # 합계 ÷ 개수 = 평균이에요. round()로 반올림해서 정수로 만들어요.
        avg_price = round(price_sum / price_count)
    # 하나도 없으면 평균도 "없음"이에요.
    else:
        avg_price = None

    # 평점이 있는 클래스가 하나라도 있으면 평균을 구해요.
    if rating_count > 0:
        # 합계 ÷ 개수 = 평균이에요. 소수 둘째 자리까지 반올림해요. 예: 4.53
        avg_rating = round(rating_sum / rating_count, 2)
    # 하나도 없으면 평균도 "없음"이에요.
    else:
        avg_rating = None

    # 카테고리별 개수를 담을 빈 딕셔너리를 만들어요.
    category_counts = {}
    # 가나다순 카테고리 이름을 하나씩 꺼내요.
    for name in get_categories():
        # 처음엔 모든 카테고리의 개수를 0으로 적어 둬요. (그래서 가나다순이 유지돼요)
        category_counts[name] = 0
    # 클래스를 하나씩 꺼내요.
    for c in classes:
        # 그 클래스의 카테고리 개수를 하나 늘려요.
        category_counts[c["category"]] = category_counts[c["category"]] + 1

    # 모은 통계를 딕셔너리 하나로 묶어서 돌려줘요.
    return {
        "total": len(classes),
        "avg_price": avg_price,
        "price_inquiry_count": price_inquiry_count,
        "avg_rating": avg_rating,
        "no_review_count": no_review_count,
        "category_counts": category_counts,
    }
