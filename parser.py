import sqlite3
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

URL = "https://admprom.ru"

def fetch_news():
    print("Запуск скрытого браузера для обхода защиты admprom.ru...")
    
    # 1. Запускаем инструменты Playwright
    with sync_playwright() as p:
        try:
            # Запускаем невидимый браузер (headless=True означает без открытия окна)
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Открываем сайт администрации
            print("Подключаемся к сайту в режиме реального времени...")
            page.goto(URL, timeout=30000)
            
            # Ждем 3 секунды, чтобы сайт прогрузил все скрипты защиты
            page.wait_for_timeout(3000)
            
            # Забираем чистый HTML, который прошел все проверки
            html_content = page.content()
            browser.close()
            
            # 2. Передаем код страницы в BeautifulSoup для разбора новостей
            soup = BeautifulSoup(html_content, 'html.parser')
            links = soup.find_all('a')
            
            conn = sqlite3.connect("news.db")
            cursor = conn.cursor()
            added_count = 0
            
            for index, link in enumerate(links):
                href = link.get('href', '')
                # Ищем ссылки с текстом "Подробнее" (так на сайте оформлены пресс-релизы)
                if "Подробнее" in link.get_text():
                    parent = link.find_parent()
                    if parent:
                        full_text = parent.get_text(strip=True).replace("Подробнее", "")
                        
                        if len(full_text) > 20:
                            title = full_text[:50] + "..." if len(full_text) > 50 else full_text
                            source_url = href if href else f"https://admprom.rulive_news_{index}"
                            image_url = "https://admprom.ruassets/logo.png"
                            date = "2026-07-29"
                            
                            try:
                                cursor.execute('''
                                    INSERT INTO news (title, text, image_url, source_url, published_at)
                                    VALUES (?, ?, ?, ?, ?)
                                ''', (title, full_text, image_url, source_url, date))
                                added_count += 1
                                print(f"-> Добавлена живая новость: {title}")
                            except sqlite3.IntegrityError:
                                pass

            conn.commit()
            conn.close()
            print(f"Сборка завершена успешно! Добавлено новых новостей: {added_count}")
            
        except Exception as e:
            print(f"Ошибка при работе живого сборщика: {e}")

if __name__ == "__main__":
    fetch_news()
