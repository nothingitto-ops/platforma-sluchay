#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Быстрый запуск локального сервера для просмотра сайта
"""

import os
import sys
import subprocess
import webbrowser
from datetime import datetime

def start_server(port=8000):
    """Запуск локального сервера"""
    try:
        print("🌐 Запуск локального сервера...")
        
        # Проверяем, что папка web существует
        if not os.path.exists('web'):
            print("❌ Папка web не найдена!")
            print("💡 Убедитесь, что вы находитесь в корневой папке проекта")
            return False
        
        # Переходим в папку web
        original_dir = os.getcwd()
        os.chdir('web')
        
        # Открываем браузер
        url = f"http://localhost:{port}"
        print(f"🚀 Сервер запущен: {url}")
        print("📱 Для остановки сервера нажмите Ctrl+C")
        print("🌐 Открываю браузер...")
        
        # Открываем браузер через 2 секунды
        import threading
        import time
        
        def open_browser():
            time.sleep(2)
            webbrowser.open(url)
        
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Запускаем HTTP сервер
        subprocess.run([sys.executable, '-m', 'http.server', str(port)])
        
        return True
        
    except KeyboardInterrupt:
        print("\n⏹️ Сервер остановлен")
        return True
    except Exception as e:
        print(f"❌ Ошибка запуска сервера: {e}")
        return False
    finally:
        # Возвращаемся в исходную папку
        if 'original_dir' in locals():
            os.chdir(original_dir)

if __name__ == "__main__":
    print("🎯 Быстрый запуск локального сервера")
    print("=" * 40)
    
    # Получаем порт из аргументов или используем 8000
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"⚠️ Неверный порт: {sys.argv[1]}, используем 8000")
    
    print(f"🎯 Порт: {port}")
    print(f"📁 Папка: {os.path.abspath('web')}")
    
    start_server(port)
