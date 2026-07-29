from fastapi import FastAPI, HTTPException
import sqlite3

app = FastAPI(title="News API")
DB_NAME = "news.db"

def init_db_on_server():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            text TEXT NOT NULL,
            image_url TEXT,
            source_url TEXT UNIQUE,
            published_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db_on_server()

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col] = row[idx]
    return d

@app.get("/news")
def get_all_news(limit: int = 10, offset: int = 0):
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM news LIMIT ? OFFSET ?", (limit, offset))
        news = cursor.fetchall()
        conn.close()
        return news
    except Exception:
        return []

@app.get("/news/{news_id}")
def get_one_news(news_id: int):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM news WHERE id = ?", (news_id,))
    news_item = cursor.fetchone()
    conn.close()
    if news_item is None:
        raise HTTPException(status_code=404, detail="Новость не найдена")
    return news_item

@app.post("/refresh")
def refresh_news():
    try:
        from parser import fetch_news
        fetch_news()
        return {"status": "success", "message": "Новости успешно обновлены"}
    except Exception as e:
        return {"status": "error", "message": f"Ошибка при обновлении: {str(e)}"}
