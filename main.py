from fastapi import FastAPI, HTTPException
import sqlite3
from parser import fetch_news


app = FastAPI(title="News API")
DB_NAME = "news.db"

# Функция-помощник для превращения строк из базы в удобные словари Python
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

@app.get("/news")
def get_all_news(limit: int = 10, offset: int = 0):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = dict_factory  # Чтобы база отдавала данные как json-словари
    cursor = conn.cursor()
    
    # Делаем запрос к базе с учетом лимита и отступа (пагинация)
    cursor.execute("SELECT * FROM news LIMIT ? OFFSET ?", (limit, offset))
    news = cursor.fetchall()
    
    conn.close()
    return news

@app.get("/news/{news_id}")
def get_one_news(news_id: int):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM news WHERE id = ?", (news_id,))
    news_item = cursor.fetchone()
    
    conn.close()
    
    # Если новость с таким ID не нашлась, возвращаем красивую ошибку 404
    if news_item is None:
        raise HTTPException(status_code=404, detail="Новость не найдена")
        
    return news_item

@app.post("/refresh")
def refresh_news():
    try:
        # Дергаем функцию сбора из нашего parser.py
        fetch_news()
        return {"status": "success", "message": "Новости успешно обновлены"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обновления: {str(e)}")
