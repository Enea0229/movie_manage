import json
import sqlite3
from sqlite3 import Connection

DB_PATH = "movies.db"
JSON_IN_PATH = "movies.json"
JSON_OUT_PATH = "exported.json"


# 連接資料庫
def connect_db() -> Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    with conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                director TEXT NOT NULL,
                genre TEXT NOT NULL,
                year INTEGER NOT NULL,
                rating REAL CHECK (rating >= 1.0 AND rating <= 10.0)
            )
        """)
    return conn


# 匯入電影資料
def import_movies(conn: Connection, json_path: str):
    try:
        with open(json_path, "r", encoding="utf-8") as file:
            movies = json.load(file)
            cursor = conn.cursor()
            for movie in movies:
                cursor.execute("""
                    INSERT INTO movies (title, director, genre, year, rating)
                    VALUES (?, ?, ?, ?, ?)
                """, (movie["title"], movie["director"], movie["genre"], movie["year"], movie["rating"]))
            conn.commit()
            print("電影已匯入")
    except FileNotFoundError:
        print("檔案不存在")
    except json.JSONDecodeError:
        print("JSON 解析錯誤")
    except (sqlite3.OperationalError, sqlite3.DatabaseError) as e:
        print(f"資料庫錯誤: {e}")


# 以電影名稱尋找電影
def search_movies(conn: Connection):
    cursor = conn.cursor()
    search_all = input("查詢全部電影嗎？(y/n): ").lower()
    if search_all == 'y':
        cursor.execute("SELECT * FROM movies")
    else:
        movie_title = input("請輸入電影名稱: ")
        cursor.execute("SELECT * FROM movies WHERE title LIKE ?", (f'%{movie_title}%',))
    results = cursor.fetchall()
    if results:
        list_rpt(results)
    else:
        print("查無資料")


# 增加電影
def add_movie(conn: Connection):
    title = input("電影名稱: ")
    director = input("導演: ")
    genre = input("類型: ")
    year = int(input("上映年份: "))
    rating = float(input("評分 (1.0 - 10.0): "))
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO movies (title, director, genre, year, rating)
        VALUES (?, ?, ?, ?, ?)
    """, (title, director, genre, year, rating))
    conn.commit()
    print("電影已新增")


# 修改電影
def modify_movie(conn: Connection):
    movie_title = input("請輸入要修改的電影名稱: ")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM movies WHERE title LIKE ?", (f'%{movie_title}%',))
    results = cursor.fetchall()

    if results:
        list_rpt(results)

        title = input("請輸入新的電影名稱 (若不修改請直接按 Enter): ") or results[0]["title"]
        director = input("請輸入新的導演 (若不修改請直接按 Enter): ") or results[0]["director"]
        genre = input("請輸入新的類型 (若不修改請直接按 Enter): ") or results[0]["genre"]
        year = input("請輸入新的上映年份 (若不修改請直接按 Enter): ") or results[0]["year"]
        rating = input("請輸入新的評分 (1.0 - 10.0) (若不修改請直接按 Enter): ") or results[0]["rating"]

        cursor.execute("""
            UPDATE movies SET title = ?, director = ?, genre = ?, year = ?, rating = ?
            WHERE id = ?
        """, (title, director, genre, year, rating, results[0]["id"]))
        conn.commit()
        print("資料已修改")
    else:
        print("查無資料")


# 刪除電影
def delete_movie(conn: Connection):
    delete_all = input("刪除全部電影嗎？(y/n): ").lower()
    cursor = conn.cursor()
    if delete_all == 'y':
        cursor.execute("DELETE FROM movies")
        print("全部電影已刪除")
    else:
        movie_title = input("請輸入要刪除的電影名稱: ")
        cursor.execute("SELECT * FROM movies WHERE title LIKE ?", (f'%{movie_title}%',))
        results = cursor.fetchall()
        if results:
            list_rpt(results)
            confirm = input("是否要刪除(y/n): ")
            if confirm.lower() == 'y':
                cursor.execute("DELETE FROM movies WHERE id = ?", (results[0]["id"],))
                conn.commit()
                print("電影已刪除")
        else:
            print("查無資料")


# 匯出電影資料的json檔
def export_movies(conn: Connection, json_out_path: str):
    cursor = conn.cursor()
    export_all = input("匯出全部電影嗎？(y/n): ").lower()
    if export_all == 'y':
        cursor.execute("SELECT * FROM movies")
    else:
        movie_title = input("請輸入要匯出的電影名稱: ")
        cursor.execute("SELECT * FROM movies WHERE title LIKE ?", (f'%{movie_title}%',))

    movies = [dict(row) for row in cursor.fetchall()]
    if movies:
        with open(json_out_path, "w", encoding="utf-8") as file:
            json.dump(movies, file, ensure_ascii=False, indent=4)
        print(f"電影資料已匯出至 {json_out_path}")
    else:
        print("查無資料")


# 列出電影清單
def list_rpt(results):
    print(
        f"{'電影名稱':{chr(12288)}<10}{'導演':{chr(12288)}<15}{'類型':{chr(12288)}<7}{'上映年份':{chr(12288)}<6}{'評分':{chr(12288)}<5}")
    print("------------------------------------------------------------------------")
    for row in results:
        print(
            f"{row['title']:{chr(12288)}<10}{row['director']:{chr(12288)}<15}{row['genre']:<10}{row['year']:<10}{row['rating']:<5}")
