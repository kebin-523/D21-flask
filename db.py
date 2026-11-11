# 파이썬에 처음부터 들어 있는 SQLite 도구를 꺼내 와요. 따로 설치할 필요가 없어요.
import sqlite3
# 파일 위치를 쉽게 다루는 Path 도구를 꺼내 와요.
from pathlib import Path

# 이 파일(db.py)이 있는 폴더 안의 reviews.db 파일을 가리켜요. 후기가 이 파일에 저장돼요.
DB_PATH = Path(__file__).resolve().parent / "reviews.db"


# 데이터베이스 파일과 연결(전화선 같은 것)을 하나 열어 주는 도우미 함수예요.
def get_connection():
    # DB_PATH 파일과 연결해요. 파일이 없으면 SQLite가 새로 만들어 줘요.
    conn = sqlite3.connect(DB_PATH)
    # 꺼낸 줄을 r["nickname"]처럼 이름표로 읽을 수 있게 설정해요.
    conn.row_factory = sqlite3.Row
    # 연결을 돌려줘요.
    return conn


# 후기를 담을 표(reviews)가 없으면 새로 만드는 함수예요.
def init_db():
    # 데이터베이스와 연결을 열어요.
    conn = get_connection()
    # try 안의 일을 하다가 오류가 나도, 아래 finally는 꼭 실행돼요.
    try:
        # 아래 SQL은 "reviews 표가 없을 때만(IF NOT EXISTS) 새로 만들어요"라는 뜻이에요.
        # id: 후기마다 자동으로 1, 2, 3… 붙는 고유 번호예요.
        # class_id: 어느 클래스의 후기인지 적는 번호예요. 비워 둘 수 없어요(NOT NULL).
        # nickname: 닉네임이에요. CHECK로 1~20자만 들어가게 막아요.
        # rating: 별점이에요. CHECK로 1~5점만 들어가게 막아요.
        # content: 후기 내용이에요. CHECK로 1~500자만 들어가게 막아요.
        # created_at: 저장한 시각이에요. 안 적으면 지금 시각(우리 컴퓨터 시간)이 자동으로 들어가요.
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_id INTEGER NOT NULL,
                nickname TEXT NOT NULL CHECK (length(nickname) BETWEEN 1 AND 20),
                rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
                content TEXT NOT NULL CHECK (length(content) BETWEEN 1 AND 500),
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            )
            """
        )
        # 바꾼 내용을 파일에 진짜로 저장(확정)해요.
        conn.commit()
    # 일이 잘 끝나든 오류가 나든 마지막에 꼭 실행되는 부분이에요.
    finally:
        # 다 쓴 연결은 꼭 닫아요. 안 닫으면 파일이 계속 붙잡혀 있어요.
        conn.close()


# 후기 하나를 표에 새로 저장하는 함수예요.
def add_review(class_id, nickname, rating, content):
    # 데이터베이스와 연결을 열어요.
    conn = get_connection()
    # try 안의 일을 하다가 오류가 나도, 아래 finally는 꼭 실행돼요.
    try:
        # 아래 SQL은 "reviews 표에 class_id, nickname, rating, content 값을 가진 줄을 하나 넣어요"라는 뜻이에요.
        # 값 자리에는 ?(물음표)를 두고, 진짜 값은 뒤의 괄호(튜플)로 따로 넘겨요.
        # 이렇게 하면 SQLite가 값을 "그냥 글자"로만 다뤄서, 누가 닉네임에 SQL 명령을 적어도 실행되지 않아요.
        # (이런 공격을 SQL 인젝션이라고 해요. 그래서 f-string 등으로 값을 SQL 글자에 직접 붙이면 안 돼요!)
        conn.execute(
            "INSERT INTO reviews (class_id, nickname, rating, content) VALUES (?, ?, ?, ?)",
            (class_id, nickname, rating, content),
        )
        # 넣은 내용을 파일에 진짜로 저장(확정)해요.
        conn.commit()
    # 일이 잘 끝나든 오류가 나든 마지막에 꼭 실행되는 부분이에요.
    finally:
        # 다 쓴 연결은 꼭 닫아요.
        conn.close()


# 클래스 하나(class_id)의 후기들을 최신순으로 꺼내 오는 함수예요.
def get_reviews(class_id):
    # 데이터베이스와 연결을 열어요.
    conn = get_connection()
    # try 안의 일을 하다가 오류가 나도, 아래 finally는 꼭 실행돼요.
    try:
        # 아래 SQL은 "reviews 표에서 class_id가 같은 줄만(WHERE) 골라서,
        # 저장 시각이 늦은 것부터(created_at DESC), 시각이 같으면 번호가 큰 것부터(id DESC) 꺼내요"라는 뜻이에요.
        # 여기서도 class_id 값은 ? 자리에 따로 넘겨서 안전하게 써요. (값이 하나여도 끝에 쉼표를 붙여야 튜플이 돼요.)
        rows = conn.execute(
            "SELECT id, class_id, nickname, rating, content, created_at FROM reviews WHERE class_id = ? ORDER BY created_at DESC, id DESC",
            (class_id,),
        ).fetchall()
        # 꺼낸 줄 하나하나를 평범한 딕셔너리로 바꿔서 목록으로 돌려줘요.
        return [dict(row) for row in rows]
    # 일이 잘 끝나든 오류가 나든(return 한 뒤에도) 마지막에 꼭 실행되는 부분이에요.
    finally:
        # 다 쓴 연결은 꼭 닫아요.
        conn.close()
