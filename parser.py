import sqlite3
import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = "https://admprom.ru"

def fetch_news():
    print("Запуск живого сборщика новостей с admprom.ru через requests...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ru"
    }
    
    try:
        response = requests.get(URL, headers=headers, verify=False, timeout=15)
        
        if response.status_code != 200:
            print(f"Сайт заблокировал запрос. Статус-код: {response.status_code}")
            return
            
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a')
        
        conn = sqlite3.connect("news.db")
        cursor = conn.cursor()
        added_count = 0
        
        for index, link in enumerate(links):
            if "Подробнее" in link.get_text():
                parent = link.find_parent()
                if parent:
                    full_text = parent.get_text(strip=True).replace("Подробнее", "")
                    if len(full_text) > 20:
                        title = full_text[:50] + "..." if len(full_text) > 50 else full_text
                        
                        # ИСПРАВЛЕНО: Добавлены пропущенные слэши после домена
                        source_url = link.get('href', f"https://admprom.ru_{index}")
                        image_url = "https://admprom.ru"
                        date = "2026-07-29"
                        
                        try:
                            cursor.execute('''
                                INSERT INTO news (title, text, image_url, source_url, published_at)
                                VALUES (?, ?, ?, ?, ?)
                            ''', (title, full_text, image_url, source_url, date))
                            added_count += 1
                            print(f"-> Найдена новость: {title}")
                        except sqlite3.IntegrityError:
                            pass

        conn.commit()
        conn.close()
        print(f"Сборка завершена успешно! Добавлено живых новостей: {added_count}")
        
    except Exception as e:
        print(f"Ошибка при работе живого сборщика: {e}")

if __name__ == "__main__":
    fetch_news()
