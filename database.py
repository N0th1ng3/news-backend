import sqlite3

DB_NAME = "news.db"

def init_db():
    # Подключаемся к файлу базы данных (если его нет, он создастся сам)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Создаем таблицу для новостей, если её еще не было
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            text TEXT NOT NULL,
            image_url TEXT,
            source_url TEXT UNIQUE,  -- Тут спрятана магия против дубликатов
            published_at TEXT
        )
    ''')
    
    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()
    print("База данных успешно инициализирована.")

if __name__ == "__main__":
    init_db()
