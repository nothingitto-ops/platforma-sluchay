#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import webbrowser

def setup_google_api():
    """Настройка Google Sheets API"""
    
    print("🔑 НАСТРОЙКА GOOGLE SHEETS API")
    print("=" * 50)
    print("Это БЕСПЛАТНО и БЕЗОПАСНО!")
    print("1000 запросов в день - бесплатно")
    print()
    
    # Открываем Google Cloud Console
    print("1. Открываю Google Cloud Console...")
    webbrowser.open("https://console.cloud.google.com/")
    
    print()
    print("📋 ПОШАГОВАЯ ИНСТРУКЦИЯ:")
    print("=" * 30)
    print("1. Создайте новый проект:")
    print("   - Нажмите 'Select a project'")
    print("   - Нажмите 'New Project'")
    print("   - Назовите проект: 'Platforma Catalog'")
    print("   - Нажмите 'Create'")
    print()
    print("2. Включите Google Sheets API:")
    print("   - В меню слева: 'APIs & Services' > 'Library'")
    print("   - Найдите 'Google Sheets API'")
    print("   - Нажмите на него и нажмите 'Enable'")
    print()
    print("3. Создайте API ключ:")
    print("   - В меню слева: 'APIs & Services' > 'Credentials'")
    print("   - Нажмите 'Create Credentials' > 'API Key'")
    print("   - Скопируйте API ключ (начинается с 'AIza...')")
    print()
    print("4. Ограничьте API ключ (рекомендуется):")
    print("   - Нажмите на созданный API ключ")
    print("   - В 'Application restrictions' выберите 'HTTP referrers'")
    print("   - Добавьте: *.google.com")
    print("   - В 'API restrictions' выберите 'Restrict key'")
    print("   - Выберите 'Google Sheets API'")
    print("   - Нажмите 'Save'")
    print()
    
    # Получаем API ключ
    api_key = input("Введите ваш API ключ: ").strip()
    
    if not api_key:
        print("❌ API ключ не введен")
        return False
    
    if not api_key.startswith('AIza'):
        print("❌ Неверный формат API ключа")
        return False
    
    # Получаем ID таблицы
    print()
    print("📊 ID ТАБЛИЦЫ GOOGLE SHEETS")
    print("=" * 30)
    print("1. Откройте вашу Google таблицу")
    print("2. Из URL скопируйте ID (между /d/ и /edit)")
    print("   Пример: https://docs.google.com/spreadsheets/d/1ABC123.../edit")
    print("   ID: 1ABC123...")
    print()
    
    spreadsheet_id = input("Введите ID таблицы: ").strip()
    
    if not spreadsheet_id:
        print("❌ ID таблицы не введен")
        return False
    
    # Сохраняем конфигурацию
    config = {
        'api_key': api_key,
        'spreadsheet_id': spreadsheet_id
    }
    
    with open('google_api_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print()
    print("✅ НАСТРОЙКА ЗАВЕРШЕНА!")
    print("=" * 30)
    print("API ключ сохранен в google_api_config.json")
    print("Теперь можно обновлять Google Sheets автоматически!")
    
    return True

if __name__ == "__main__":
    setup_google_api()
