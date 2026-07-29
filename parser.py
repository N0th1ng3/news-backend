def fetch_news():
    print("Запуск сборщика новостей...")
    
    # Имитируем ответ чужого API. Будто мы сделали запрос и получили такой JSON-список:
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
    
    # Проходим циклом по каждой новости из полученного "ответа"
    for item in mock_external_api_response:
        title = item.get('title')
        text = item.get('body')
        source_url = item.get('url')
        image_url = item.get('image')
        date = item.get('published_at')
        
        # Печатаем всё в консоль строго по ТЗ
        print("-" * 40)
        print(f"ЗАГОЛОВОК: {title}")
        print(f"ТЕКСТ: {text}")
        print(f"КАРТИНКА: {image_url}")
        print(f"ОРИГИНАЛ: {source_url}")
        print(f"ДАТА: {date}")

if __name__ == "__main__":
    fetch_news()
