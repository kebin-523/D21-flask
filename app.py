# 컴퓨터 설정값(환경변수)을 읽을 때 쓰는 os 도구를 꺼내 와요.
import os

# python-dotenv 도구에서 .env 파일을 읽어 주는 load_dotenv를 꺼내 와요.
from dotenv import load_dotenv

# .env 파일의 값을 환경변수로 불러와요. 그래서 아래에서 환경변수를 읽기 전에 먼저 불러야 해요.
# 서버에는 .env 없이 진짜 환경변수를 넣어요. (.env가 없으면 그냥 아무 일도 안 해요)
load_dotenv()

# Flask 도구 상자에서 Flask와 render_template(템플릿으로 화면 만들기)을 꺼내 와요.
# request는 주소 뒤 ?category=공예 같은 질문(쿼리)을 읽을 때 써요.
# abort는 "여기서 멈추고 오류 번호(예: 404)를 보내!"라고 할 때 써요.
# jsonify는 파이썬 딕셔너리를 JSON(프로그램끼리 주고받는 글자 형식)으로 바꿔서 보내 줘요.
# redirect는 "이 주소로 다시 가 줘!"라고 브라우저에게 알려 줄 때 써요.
# url_for는 함수 이름으로 주소(예: /class/1)를 만들어 줘요.
# flash는 다음 화면에 딱 한 번만 보여 줄 안내 메시지를 맡겨 둬요.
# session은 브라우저마다 따로 기억하는 작은 보관함이에요. (찜 목록을 여기에 담아요)
from flask import Flask, render_template, request, abort, jsonify, redirect, url_for, flash, session

# 우리가 만든 data.py에서 클래스 데이터를 다루는 함수들을 꺼내 와요.
# get_stats는 전체 통계(평균 가격, 평균 평점 등)를 만들어 주는 함수예요.
from data import load_classes, get_categories, filter_and_sort, get_class, get_stats
# 우리가 만든 db.py에서 후기 저장소(SQLite)를 다루는 함수들을 꺼내 와요.
# init_db는 표 만들기, add_review는 후기 저장하기, get_reviews는 후기 꺼내 오기예요.
from db import init_db, add_review, get_reviews

# 우리 웹 가게(앱)를 하나 만들어요. __name__은 "이 파일"을 가리켜요.
app = Flask(__name__)
# JSON에서 한글을 공 같은 암호 글자 말고 "공예"처럼 그대로 보여 주게 해요.
app.json.ensure_ascii = False
# JSON의 이름표(키) 순서를 가나다순으로 바꾸지 말고, 우리가 적은 순서 그대로 두게 해요.
app.json.sort_keys = False
# flash가 안내를 잠깐 맡겨 두는 곳(세션 쿠키)을 잠그는 열쇠예요.
# 환경변수 SECRET_KEY에서 아무도 모르는 긴 값을 읽어 와요. 없으면 None(없음)이에요.
secret_key = os.environ.get("SECRET_KEY")
# 열쇠가 없으면 연습용 값으로 몰래 켜지지 않고, 여기서 바로 멈춰서 알려 줘요.
if not secret_key:
    # RuntimeError는 "이대로는 실행할 수 없어요!"라는 오류예요. 안내 문장을 함께 보여 줘요.
    raise RuntimeError("SECRET_KEY가 없어요. .env.example을 보고 .env 파일을 만들어 주세요.")
# 읽어 온 열쇠를 앱에 끼워요.
app.secret_key = secret_key

# 앱이 켜질 때 표가 없으면 만들어요. (이미 있으면 그대로 두고, 저장된 후기도 지워지지 않아요.)
init_db()


# 이 브라우저의 찜 목록(클래스 번호들)을 꺼내 주는 함수예요.
def get_wishlist():
    # 보관함(session)에서 "wishlist"를 꺼내요. 아직 없으면 빈 목록([])이에요.
    # list(...)로 복사본을 만들어요. 꺼낸 목록을 고친 뒤 다시 넣어야 Flask가 바뀐 걸 알아채요.
    return list(session.get("wishlist", []))


# 모든 템플릿에서 쓸 수 있는 값을 미리 넣어 주는 표시예요. (메뉴의 찜 개수에 써요)
@app.context_processor
# 찜 개수를 모든 화면에 넣어 주는 함수예요.
def inject_wish_count():
    # wish_count라는 이름으로 찜한 클래스 개수를 넘겨줘요. 템플릿에서 {{ wish_count }}로 써요.
    return {"wish_count": len(get_wishlist())}


# 누군가 주소 "/" (첫 화면)로 들어오면 바로 아래 함수를 실행하라는 표시예요.
@app.route("/")
# 첫 화면을 담당하는 함수를 만들어요. 이름은 home이에요.
def home():
    # CSV에서 클래스 목록을 모두 읽어 와요.
    all_classes = load_classes()
    # 카테고리 이름 목록을 가져와요.
    categories = get_categories()
    # templates 폴더의 index.html로 화면을 만들어 돌려줘요. 전체 개수와 카테고리도 넘겨줘요.
    return render_template("index.html", total=len(all_classes), categories=categories)


# 누군가 주소 "/about"으로 들어오면 바로 아래 함수를 실행해요.
@app.route("/about")
# 서비스 소개를 담당하는 함수예요.
def about():
    # templates 폴더의 about.html로 화면을 만들어 돌려줘요.
    return render_template("about.html")


# "/hello/" 뒤에 오는 글자를 name이라는 이름표에 담아요. 예: /hello/민수 → name은 "민수"
@app.route("/hello/<name>")
# 주소에서 꺼낸 name을 받아서 쓰는 함수예요.
def hello(name):
    # hello.html에 name을 넘겨줘요. 템플릿 안의 {{ name }} 자리에 이 값이 들어가요.
    return render_template("hello.html", name=name)


# 누군가 주소 "/classes"로 들어오면 바로 아래 함수를 실행해요.
@app.route("/classes")
# 클래스 목록을 보여 주는 함수예요.
def classes():
    # 주소의 ?category=... 값을 읽어요. 없으면 빈 글자("")예요.
    category = request.args.get("category", "")
    # 주소의 ?sort=... 값을 읽어요. 없으면 빈 글자("")예요.
    sort = request.args.get("sort", "")
    # CSV에서 클래스 목록을 모두 읽어 와요.
    all_classes = load_classes()
    # 고른 카테고리로 거르고, 고른 순서로 정렬해요.
    result = filter_and_sort(all_classes, category, sort)
    # 선택 상자에 보여 줄 카테고리 이름 목록을 가져와요.
    categories = get_categories()
    # classes.html에 목록, 카테고리, 지금 고른 값, 개수를 넘겨줘요.
    return render_template(
        "classes.html",
        classes=result,
        categories=categories,
        selected_category=category,
        selected_sort=sort,
        count=len(result),
    )


# "/class/" 뒤의 숫자를 class_id에 담아요. <int:...>라서 숫자만 받아요. 예: /class/2 → class_id는 2
# methods에 "POST"도 적어서, 화면 보기(GET)와 후기 보내기(POST)를 둘 다 받아요.
@app.route("/class/<int:class_id>", methods=["GET", "POST"])
# 클래스 하나의 상세 화면을 보여 주고, 수강 후기도 받는 함수예요.
def class_detail(class_id):
    # 번호로 클래스를 찾아요.
    item = get_class(class_id)
    # 못 찾았으면 여기서 멈추고 404(없는 페이지) 오류를 보내요. (보기든 보내기든 똑같아요)
    if item is None:
        abort(404)

    # 잘못 적은 부분을 알려 줄 오류 메시지들을 담을 빈 목록이에요.
    errors = []
    # 입력 칸에 미리 채워 둘 값이에요. 처음에는 모두 빈칸이에요.
    form = {"nickname": "", "rating": "", "content": ""}

    # 사용자가 후기 폼을 보내서(POST) 들어온 경우에만 아래를 실행해요.
    if request.method == "POST":
        # 폼에서 닉네임을 꺼내요. 없으면 빈 글자이고, .strip()으로 앞뒤 빈칸을 지워요.
        nickname = request.form.get("nickname", "").strip()
        # 폼에서 별점을 꺼내요. 아직은 "4" 같은 글자예요.
        rating_text = request.form.get("rating", "").strip()
        # 폼에서 후기 내용을 꺼내요.
        content = request.form.get("content", "").strip()

        # 닉네임이 비어 있으면 오류 메시지를 넣어요.
        if nickname == "":
            # 오류 목록에 안내 문장을 하나 추가해요.
            errors.append("닉네임을 적어 주세요.")
        # 닉네임이 20자보다 길면 오류 메시지를 넣어요.
        elif len(nickname) > 20:
            # 오류 목록에 안내 문장을 하나 추가해요.
            errors.append("닉네임은 20자까지 쓸 수 있어요.")

        # 별점이 "1"~"5" 중 하나가 아니면 오류 메시지를 넣어요.
        if rating_text not in ["1", "2", "3", "4", "5"]:
            # 오류 목록에 안내 문장을 하나 추가해요.
            errors.append("별점을 1~5점 중에서 골라 주세요.")

        # 후기 내용이 비어 있으면 오류 메시지를 넣어요.
        if content == "":
            # 오류 목록에 안내 문장을 하나 추가해요.
            errors.append("후기 내용을 적어 주세요.")
        # 후기 내용이 500자보다 길면 오류 메시지를 넣어요.
        elif len(content) > 500:
            # 오류 목록에 안내 문장을 하나 추가해요.
            errors.append("후기는 500자까지 쓸 수 있어요.")

        # 오류가 하나도 없으면 후기를 저장해요.
        if len(errors) == 0:
            # 후기를 데이터베이스(reviews.db 파일)에 저장해요. 별점 글자("4")는 숫자(4)로 바꿔서 넘겨요.
            # 파일에 저장하니까 서버를 껐다 켜도 후기가 사라지지 않아요.
            add_review(class_id, nickname, int(rating_text), content)
            # 다음 화면에서 딱 한 번 보여 줄 "저장됐어요" 안내를 맡겨 둬요.
            flash("후기가 저장됐어요")
            # 저장(POST) 뒤 바로 화면을 주지 않고 GET 주소(#reviews 후기 부분)로 다시 보내요.
            # 그래서 새로고침해도 마지막 요청은 GET이라 후기가 다시 저장되지 않아요. (Post/Redirect/Get)
            return redirect(url_for("class_detail", class_id=class_id, _anchor="reviews"))

        # 오류가 있으면, 사용자가 적은 값을 그대로 다시 채워 줘서 처음부터 안 써도 되게 해요.
        form = {"nickname": nickname, "rating": rating_text, "content": content}

    # 데이터베이스에서 이 클래스(class_id)의 후기만 꺼내 와요. 이미 가장 최근 후기가 맨 위에 와요.
    class_reviews = get_reviews(class_id)

    # 오류가 있으면 400(잘못된 요청), 없으면 200(성공) 상태 코드를 써요.
    status = 400 if errors else 200
    # class_detail.html에 클래스(c), 후기 목록, 오류 메시지, 입력값을 넘겨주고, 상태 코드도 함께 보내요.
    # is_wished는 이 클래스 번호가 찜 목록에 들어 있으면 True(참)예요. 버튼 모양을 바꿀 때 써요.
    return render_template("class_detail.html", c=item, reviews=class_reviews, errors=errors, form=form, is_wished=class_id in get_wishlist()), status


# "/class/번호/wish" 주소로 POST(보내기)가 오면 찜하기/찜 취소를 해요.
# methods가 POST뿐이라서, 주소창에 그냥 들어오면(GET) 405(허용 안 된 방식) 오류가 나요.
@app.route("/class/<int:class_id>/wish", methods=["POST"])
# 찜을 켜고 끄는(토글) 함수예요.
def toggle_wish(class_id):
    # 번호로 클래스를 찾아요.
    item = get_class(class_id)
    # 없는 클래스면 여기서 멈추고 404(없는 페이지) 오류를 보내요.
    if item is None:
        abort(404)
    # 지금 찜 목록(복사본)을 꺼내요.
    wishlist = get_wishlist()
    # 이미 찜한 클래스라면
    if class_id in wishlist:
        # 목록에서 빼요. (찜 취소)
        wishlist.remove(class_id)
    # 아직 찜하지 않은 클래스라면
    else:
        # 목록 맨 뒤에 넣어요. (찜하기)
        wishlist.append(class_id)
    # 고친 목록을 보관함(session)에 다시 넣어요. 이렇게 해야 브라우저에 저장돼요.
    session["wishlist"] = wishlist
    # 보낸(POST) 뒤 상세 화면(GET)으로 다시 보내요. 새로고침해도 찜이 또 바뀌지 않아요. (Post/Redirect/Get)
    return redirect(url_for("class_detail", class_id=class_id))


# 누군가 주소 "/wishlist"로 들어오면 찜 목록 화면을 보여 줘요.
@app.route("/wishlist")
# 찜한 클래스들을 보여 주는 함수예요.
def wishlist():
    # 화면에 보여 줄 클래스들을 담을 빈 목록이에요.
    wished_classes = []
    # 찜 번호를 거꾸로(reversed) 하나씩 꺼내요. 그래서 가장 최근에 찜한 클래스가 맨 앞에 와요.
    for wished_id in reversed(get_wishlist()):
        # 번호로 클래스를 찾아요.
        item = get_class(wished_id)
        # 못 찾았으면(CSV에서 사라진 번호) 건너뛰어요.
        if item is None:
            # continue는 "이번 것은 넘기고 다음 번호로!"라는 뜻이에요.
            continue
        # 찾은 클래스를 목록에 넣어요.
        wished_classes.append(item)
    # wishlist.html에 찜한 클래스 목록과 개수를 넘겨줘요.
    return render_template("wishlist.html", classes=wished_classes, count=len(wished_classes))


# 누군가 주소 "/api/classes"로 들어오면 화면(HTML) 대신 데이터(JSON)를 돌려줘요.
@app.route("/api/classes")
# 클래스 목록을 JSON으로 돌려주는 함수예요.
def api_classes():
    # 주소의 ?category=... 값을 읽어요. 없으면 빈 글자("")예요.
    category = request.args.get("category", "")
    # CSV에서 클래스 목록을 모두 읽어 와요.
    all_classes = load_classes()
    # 고른 카테고리로 걸러요. 정렬은 하지 않아요(None).
    result = filter_and_sort(all_classes, category, None)
    # 카테고리, 개수, 목록을 JSON으로 보내요. 카테고리를 안 골랐으면 null(없음)로 보내요.
    return jsonify({"category": category or None, "count": len(result), "classes": result})


# "/api/classes/" 뒤의 숫자를 class_id에 담아요. 예: /api/classes/2 → class_id는 2
@app.route("/api/classes/<int:class_id>")
# 클래스 하나를 JSON으로 돌려주는 함수예요.
def api_class_detail(class_id):
    # 번호로 클래스를 찾아요.
    item = get_class(class_id)
    # 못 찾았으면 오류 메시지를 JSON으로 보내고, 상태 코드는 404로 보내요.
    if item is None:
        return jsonify({"error": "클래스를 찾을 수 없어요", "id": class_id}), 404
    # 찾았으면 그 클래스를 JSON으로 보내요.
    return jsonify(item)


# 누군가 주소 "/api/stats"로 들어오면 통계를 JSON으로 돌려줘요.
@app.route("/api/stats")
# 전체 통계를 JSON으로 돌려주는 함수예요.
def api_stats():
    # data.py의 get_stats로 통계를 만들어서 JSON으로 보내요.
    return jsonify(get_stats())


# 404 오류가 생기면(없는 주소, 없는 번호) 이 함수가 대신 화면을 만들어요.
@app.errorhandler(404)
# error에는 어떤 오류인지가 담겨 와요.
def page_not_found(error):
    # 주소가 "/api/"로 시작하면 프로그램이 읽는 주소라서, 화면 대신 JSON으로 오류를 알려 줘요.
    if request.path.startswith("/api/"):
        # 오류 메시지와 들어온 주소를 JSON으로 보내고, 상태 코드는 404로 보내요.
        return jsonify({"error": "찾는 주소가 없어요", "path": request.path}), 404
    # 404.html 화면을 보여 주고, 상태 코드도 진짜 404로 보내요. (뒤의 404가 없으면 200이 돼요!)
    return render_template("404.html"), 404


# 500 오류가 생기면(코드 안에서 예상하지 못한 문제) 이 함수가 대신 화면을 만들어요.
@app.errorhandler(500)
# error에는 어떤 오류인지가 담겨 와요.
def server_error(error):
    # 주소가 "/api/"로 시작하면 프로그램이 읽는 주소라서, 화면 대신 JSON으로 오류를 알려 줘요.
    if request.path.startswith("/api/"):
        # 오류 메시지를 JSON으로 보내고, 상태 코드는 500으로 보내요.
        return jsonify({"error": "서버에 문제가 생겼어요. 잠시 뒤에 다시 해 주세요."}), 500
    # 500.html 화면을 보여 주고, 상태 코드도 진짜 500으로 보내요.
    return render_template("500.html"), 500


# 이 파일을 직접 실행했을 때만 아래 줄이 동작해요.
# 서버(gunicorn)는 이 파일을 직접 실행하지 않아서, 이 아래 줄을 아예 실행하지 않아요.
if __name__ == "__main__":
    # 환경변수 FLASK_DEBUG가 "1"일 때만 True(켜짐)가 돼요.
    # .env에 FLASK_DEBUG=1이 있는 내 컴퓨터에서만 켜져요.
    debug_mode = os.environ.get("FLASK_DEBUG") == "1"
    # 가게 문을 열어요. debug가 켜지면 코드를 고칠 때 자동으로 다시 켜지고, 에러도 자세히 보여 줘요.
    # debug가 켜진 채 배포하면 누구나 오류 화면에서 코드를 실행할 수 있어 위험해요.
    app.run(debug=debug_mode)
