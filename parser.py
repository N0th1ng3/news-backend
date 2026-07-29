import os
import sqlite3
import subprocess
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

URL = "https://admprom.ru"

def ensure_chromium_installed():
    """Проверяет наличие браузера Chromium и ставит его программно при отсутствии"""
    try:
        print("Проверка готовности невидимого браузера...")
        with sync_playwright() as p:
            p.chromium.launch(headless=True).close()
        print("Браузер Chromium обнаружен и готов к работе.")
    except Exception:
        print("Браузер не найден в системе. Запуск автоматической установки Chromium...")
        try:
            # Вызываем системную команду установки браузера прямо из Python
            subprocess.run(["playwright", "install", "chromium"], check=True)
            print("Chromium успешно установлен силами скрипта!")
        except Exception as install_error:
            print(f"Критическая ошибка программной установки браузера: {install_error}")

def fetch_news():
    print("Запуск сборщика реальных новостей с admprom.ru...")
    
    # Скрипт сам накатит браузер на сервер Render в реальном времени!
    ensure_chromium_installed()
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            print("Подключаемся к сайту в режиме реального времени...")
            page.goto(URL, timeout=30000)
            page.wait_for_timeout(3000)
            
            html_content = page.content()
            browser.close()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            links = soup.find_all('a')
            
            conn = sqlite3.connect("news.db")
            cursor = conn.cursor()
            added_count = 0
            
            for index, link in enumerate(links):
                href = link.get('href', '')
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
