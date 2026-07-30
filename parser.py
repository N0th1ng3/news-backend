import sqlite3
import requests
from bs4 import BeautifulSoup
import urllib3
from datetime import datetime
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://admprom.ru"

def fetch_inner_news_details(news_url, headers):
    """Заходит внутрь новости, собирает ОРИГИНАЛЬНЫЙ ПОЛНЫЙ заголовок, текст статьи и ВСЕ картинки"""
    try:
        if not news_url.startswith("http"):
            news_url = BASE_URL + news_url
            
        response = requests.get(news_url, headers=headers, verify=False, timeout=10)
        if response.status_code != 200:
            return None, "Текст новости временно недоступен.", "https://admprom.ru"
            
        inner_soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Поиск главного тега заголовка
        title_tag = inner_soup.find('h1', class_='entry-title') or inner_soup.find('h1') or inner_soup.find('h2')
        full_title = title_tag.get_text(strip=True) if title_tag else None

        content_div = inner_soup.find('div', class_='entry-content') or inner_soup.find('article')
        
        # 2. Сбор полноценного текста новости (раздельно по абзацам)
        if content_div:
            paragraphs = [p.get_text(strip=True) for p in content_div.find_all('p')]
            clean_paragraphs = [p for p in paragraphs if len(p) > 5 and "Подробнее" not in p]
            full_text = "\n\n".join(clean_paragraphs)
        else:
            full_text = "Не удалось извлечь содержимое статьи."

        # КРАСИВЫЙ ХОД: Если заголовка h1 нет или он содержит три точки на конце, генерируем его из первого предложения полного текста
        if not full_title or "..." in full_title or "…" in full_title:
            if clean_paragraphs:
                first_paragraph = clean_paragraphs[0]
                # Берем первое предложение до точки
                if "." in first_paragraph:
                    full_title = first_paragraph.split(".")[0].strip() + "."
                else:
                    full_title = first_paragraph[:100].strip()
            else:
                full_title = "Новость округа"

        # Окончательно очищаем заголовок от любых случайных троеточий на конце
        full_title = full_title.rstrip(".… ").strip()

        # 3. Сбор ВСЕХ картинок внутри новости
        images_found = []
        if content_div:
            img_tags = content_div.find_all('img')
            for img in img_tags:
                src = img.get('src')
                if src and src.startswith("http") and "logo" not in src:
                    images_found.append(src)
                elif src and src.startswith("/"):
                    images_found.append(BASE_URL + src)

        if not images_found:
            featured_img = inner_soup.find('img', class_='wp-post-image')
            if featured_img and featured_img.get('src'):
                src = featured_img.get('src')
                images_found.append(src if src.startswith("http") else BASE_URL + src)

        if not images_found:
            images_found.append("https://admprom.ru")

        all_images_str = ",".join(images_found)

        return full_title, full_text, all_images_str
    except Exception as e:
        print(f"Ошибка при глубоком парсинге статьи {news_url}: {e}")
        return "Новость округа", "Ошибка загрузки текста.", "https://admprom.ru"

def fetch_news():
    print("Запуск парсинга полных заголовков, текстов и галерей...")
    
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
        
        # Очищаем базу, чтобы заново перекачать с чистыми заголовками
        cursor.execute("DELETE FROM news")
        conn.commit()
        
        added_count = 0
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for index, link in enumerate(links):
            if "Подробнее" in link.get_text():
                source_url = link.get('href', '')
                if not source_url:
                    continue
                    
                if not source_url.startswith("http"):
                    source_url = BASE_URL + source_url

                # Заходим внутрь статьи за полными данными
                inner_title, full_text, image_urls_list = fetch_inner_news_details(source_url, headers)

                try:
                    cursor.execute('''
                        INSERT INTO news (title, text, image_url, source_url, published_at)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (inner_title, full_text, image_urls_list, source_url, current_date))
                    added_count += 1
                    print(f"-> Сохранена статья: {inner_title}")
                    time.sleep(1)
                except sqlite3.IntegrityError:
                    pass

        conn.commit()
        conn.close()
        print(f"Сбор завершен! Добавлено полноценных новостей: {added_count}")
        
    except Exception as e:
        print(f"Ошибка при работе живого сборщика: {e}")

if __name__ == "__main__":
    fetch_news()
