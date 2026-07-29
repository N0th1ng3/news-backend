import sqlite3

def fetch_news():
    print("Запуск сборщика новостей...")
    
    # Наш фейковый ответ от чужого API (две новости)
    mock_external_api_response = [
        {
            "id": 1,
            "title": "Космический корабль отправился на Марс",
            "body": "Сегодня утром состоялся успешный запуск ракеты нового поколения, которая доставит исследовательский марсоход.",
            "url": "https://news-site.com",
            "image": "https://news-site.com",
            "published_at": "2026-07-29 12:00:00"
        },
        {
            "id": 2,
            "title": "Вышла новая версия Python 3.14",
            "body": "Разработчики представили финальный релиз языка. В нем исправили работу с сетевыми протоколами и SSL в Windows.",
            "url": "https://news-site.com",
            "image": "https://news-site.com",
            "published_at": "2026-07-29 14:30:00"
        }
    ]
    
    # Подключаемся к нашей созданной базе данных news.db
    conn = sqlite3.connect("news.db")
    cursor = conn.cursor()
    
    # Считаем, сколько новостей мы успешно добавим
    added_count = 0
    
    for item in mock_external_api_response:
        title = item.get('title')
        text = item.get('body')
        source_url = item.get('url')
        image_url = item.get('image')
        date = item.get('published_at')
        
        try:
            # Пробуем вставить строку в таблицу news
            cursor.execute('''
                INSERT INTO news (title, text, image_url, source_url, published_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (title, text, image_url, source_url, date))
            added_count += 1
            print(f"Успешно добавлена новость: {title}")
            
        except sqlite3.IntegrityError:
            # Эта ошибка сработает, если UNIQUE заблокирует дубликат ссылки!
            print(f"Новость уже есть в базе (дубликат пропущен): {title}")
            
    # Сохраняем изменения в файле базы данных и закрываем её
    conn.commit()
    conn.close()
    print(f"Сборка завершена. Добавлено новых новостей: {added_count}")

if __name__ == "__main__":
    fetch_news()
