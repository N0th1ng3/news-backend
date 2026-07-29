import sqlite3
import requests
from bs4 import BeautifulSoup
import urllib3
from datetime import datetime
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://admprom.ru"

def fetch_full_news_data(news_url, headers):
    """Заходит внутрь новости и забирает полный текст статьи и картинку"""
    try:
        # Если ссылка относительная, превращаем её в абсолютную
        if not news_url.startswith("http"):
            news_url = BASE_URL + news_url
            
        response = requests.get(news_url, headers=headers, verify=False, timeout=10)
        if response.status_code != 200:
            return None, None
            
        inner_soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Поиск полноценного текста новости (ориентируемся на теги абзацев внутри контента)
        content_div = inner_soup.find('div', class_='entry-content') or inner_soup.find('article')
        if content_div:
            # Собираем текст всех абзацев внутри статьи
            paragraphs = [p.get_text(strip=True) for p in content_div.find_all('p')]
            full_text = "\n\n".join([p for p in paragraphs if len(p) > 5])
        else:
            full_text = inner_soup.get_text(strip=True)[:1000] # Заглушка, если структура сломалась

        # 2. Поиск оригинальной картинки новости
        image_url = None
        if content_div:
            img_tag = content_div.find('img')
            if img_tag:
                image_url = img_tag.get('src')
        
        # Если внутри текста нет картинки, ищем главное превью (featured image)
        if not image_url:
            img_tag = inner_soup.find('img', class_='wp-post-image') or inner_soup.find('img')
            if img_tag:
                image_url = img_tag.get('src')

        # Делаем ссылку на картинку абсолютной
        if image_url and not image_url.startswith("http"):
            image_url = BASE_URL + image_url

        return full_text, image_url
    except Exception as e:
        print(f"Ошибка при парсинге страницы новости {news_url}: {e}")
        return None, None

def fetch_news():
    print("Запуск глубокого сетевого парсинга новостей...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ru"
    }
    
    try:
        response = requests.get(BASE_URL, headers=headers, verify=False, timeout=15)
        if response.status_code != 200:
            print(f"Сайт заблокировал запрос. Статус-код: {response.status_code}")
            return
            
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a')
        
        conn = sqlite3.connect("news.db")
        cursor = conn.cursor()
        added_count = 0
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for index, link in enumerate(links):
            if "Подробнее" in link.get_text():
                source_url = link.get('href', '')
                if not source_url:
                    continue
                    
                if not source_url.startswith("http"):
                    source_url = BASE_URL + source_url

                # Проверяем, есть ли уже эта новость в нашей базе, чтобы не тратить время на парсинг текста заново
                cursor.execute("SELECT id FROM news WHERE source_url = ?", (source_url,))
                if cursor.fetchone():
                    continue

                parent = link.find_parent()
                title = parent.get_text(strip=True).replace("Подробнее", "")[:80] + "..." if parent else "Новость округа"

                print(f"Парсинг статьи: {title}")
                # Переходим внутрь ссылки за полным текстом и картинкой
                full_text, image_url = fetch_full_news_data(source_url, headers)
                
                # Если текст не собрался, берем короткий кусок с главной
                if not full_text:
                    full_text = parent.get_text(strip=True).replace("Подробнее", "") if parent else "Текст отсутствует"
                if not image_url:
                    image_url = "https://admprom.ru"

                try:
                    cursor.execute('''
                        INSERT INTO news (title, text, image_url, source_url, published_at)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (title, full_text, image_url, source_url, current_date))
                    added_count += 1
                    time.sleep(1) # Небольшая пауза, чтобы сайт администрации не забанил сервер за спам-запросы
                except sqlite3.IntegrityError:
                    pass

        conn.commit()
        conn.close()
        print(f"Глубокий сбор завершен! Добавлено полноценных новостей: {added_count}")
        
    except Exception as e:
        print(f"Ошибка при работе живого сборщика: {e}")

if __name__ == "__main__":
    fetch_news()
