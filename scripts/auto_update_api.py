#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import requests
from datetime import datetime

def auto_update_google_sheets_api():
    """Полностью автоматическое обновление Google Sheets через API"""
    
    print("🚀 ПОЛНОСТЬЮ АВТОМАТИЧЕСКОЕ ОБНОВЛЕНИЕ")
    print("=" * 50)
    
    # Загружаем конфигурацию
    try:
        # Ищем конфигурацию в разных местах
        config_paths = [
            'google_api_config.json',
            'scripts/google_api_config.json',
            os.path.join(os.path.dirname(__file__), 'google_api_config.json')
        ]
        
        config = None
        for path in config_paths:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    config = json.load(f)
                    break
        
        if not config:
            raise FileNotFoundError("Конфигурация не найдена")
            
        api_key = config.get('api_key')
        spreadsheet_id = config.get('spreadsheet_id')
    except FileNotFoundError:
        print("❌ Конфигурация не найдена!")
        print("Запустите: python scripts/setup_google_api.py")
        return False
    except Exception as e:
        print(f"❌ Ошибка загрузки конфигурации: {e}")
        return False
    
    if not api_key or not spreadsheet_id:
        print("❌ API ключ или ID таблицы не настроены!")
        print("Запустите: python scripts/setup_google_api.py")
        return False
    
    # Загружаем наши товары
    try:
        with open('products.json', 'r', encoding='utf-8') as f:
            products = json.load(f)
    except Exception as e:
        print(f"❌ Ошибка загрузки товаров: {e}")
        return False
    
    print(f"📊 Найдено товаров: {len(products)}")
    print(f"🔑 API ключ: {api_key[:10]}...")
    print(f"📋 Таблица: {spreadsheet_id}")
    print()
    
    # Сначала получаем существующие данные из таблицы
    print("📥 Получаю существующие данные из таблицы...")
    try:
        read_url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/A1:Z1000?key={api_key}"
        read_response = requests.get(read_url, timeout=30)
        
        if read_response.status_code != 200:
            print(f"❌ Ошибка чтения таблицы: {read_response.status_code}")
            return False
            
        existing_data = read_response.json().get('values', [])
        print(f"📋 Найдено существующих строк: {len(existing_data)}")
        
        # Если таблица пустая, добавляем заголовок
        if not existing_data:
            existing_data = [["Section", "Title", "Price", "Desc", "Meta", "Status", "Images", "Link"]]
        
    except Exception as e:
        print(f"❌ Ошибка получения данных: {e}")
        return False
    
    # Подготавливаем новые данные
    print("📝 Подготавливаю новые данные...")
    new_rows = []
    
    for product in products:
        # Проверяем, есть ли уже такой товар в таблице
        product_exists = any(
            row[1] == product['title'] if len(row) > 1 else False 
            for row in existing_data[1:]  # Пропускаем заголовок
        )
        
        if not product_exists:
            row = [
                "home",
                product['title'],
                product.get('price', ''),
                product.get('desc', ''),
                product.get('meta', ''),
                product.get('status', ''),
                product['images'],
                "https://t.me/stub123"
            ]
            new_rows.append(row)
    
    if not new_rows:
        print("✅ Все товары уже есть в таблице!")
        return True
    
    print(f"🆕 Новых товаров для добавления: {len(new_rows)}")
    
    # Добавляем новые строки в конец таблицы
    try:
        # Определяем диапазон для добавления (после последней строки)
        start_row = len(existing_data) + 1
        end_row = start_row + len(new_rows) - 1
        
        append_url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/A{start_row}:Z{end_row}?valueInputOption=RAW&key={api_key}"
        
        append_data = {
            "values": new_rows
        }
        
        print(f"🔄 Добавляю новые товары в строки {start_row}-{end_row}...")
        
        append_response = requests.put(append_url, json=append_data, timeout=30)
        
        if append_response.status_code == 200:
            result = append_response.json()
            updated_cells = result.get('updatedCells', 0)
            updated_rows = result.get('updatedRows', 0)
            
            print("✅ УСПЕШНО ДОБАВЛЕНО!")
            print("=" * 30)
            print(f"📊 Товаров добавлено: {len(new_rows)}")
            print(f"📋 Обновлено ячеек: {updated_cells}")
            print(f"📋 Обновлено строк: {updated_rows}")
            print(f"⏰ Время: {datetime.now().strftime('%H:%M:%S')}")
            print()
            
            # Создаем TSV файл для локального использования
            tsv_filename = f"sheets-update-{datetime.now().strftime('%Y%m%d-%H%M%S')}.tsv"
            with open(tsv_filename, 'w', encoding='utf-8') as f:
                # Записываем заголовок
                f.write("Section\tTitle\tPrice\tDesc\tMeta\tStatus\tImages\tLink\n")
                # Записываем все данные (существующие + новые)
                all_data = existing_data[1:] + new_rows  # Пропускаем заголовок из existing_data
                for row in all_data:
                    f.write("\t".join(str(cell) for cell in row) + "\n")
            
            print(f"💾 TSV файл создан: {tsv_filename}")
            return True
            
        else:
            print(f"❌ Ошибка добавления: {append_response.status_code}")
            print(f"Ответ: {append_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при добавлении данных: {e}")
        return False

def sync_google_sheets_complete():
    """Полная синхронизация Google Sheets с локальными данными (включая удаление)"""
    
    print("🔄 ПОЛНАЯ СИНХРОНИЗАЦИЯ GOOGLE SHEETS")
    print("=" * 50)
    
    # Загружаем конфигурацию
    try:
        config_paths = [
            'google_api_config.json',
            'scripts/google_api_config.json',
            os.path.join(os.path.dirname(__file__), 'google_api_config.json')
        ]
        
        config = None
        for path in config_paths:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    config = json.load(f)
                    break
        
        if not config:
            raise FileNotFoundError("Конфигурация не найдена")
            
        api_key = config.get('api_key')
        spreadsheet_id = config.get('spreadsheet_id')
    except FileNotFoundError:
        print("❌ Конфигурация не найдена!")
        print("Запустите: python scripts/setup_google_api.py")
        return False
    except Exception as e:
        print(f"❌ Ошибка загрузки конфигурации: {e}")
        return False
    
    if not api_key or not spreadsheet_id:
        print("❌ API ключ или ID таблицы не настроены!")
        print("Запустите: python scripts/setup_google_api.py")
        return False
    
    # Загружаем наши товары
    try:
        with open('products.json', 'r', encoding='utf-8') as f:
            products = json.load(f)
    except Exception as e:
        print(f"❌ Ошибка загрузки товаров: {e}")
        return False
    
    print(f"📊 Локальных товаров: {len(products)}")
    print(f"🔑 API ключ: {api_key[:10]}...")
    print(f"📋 Таблица: {spreadsheet_id}")
    print()
    
    # Подготавливаем данные для полной перезаписи
    print("📝 Подготавливаю данные для полной синхронизации...")
    values = [["Section", "Title", "Price", "Desc", "Meta", "Status", "Images", "Link"]]
    
    for product in products:
        row = [
            "home",
            product['title'],
            product.get('price', ''),
            product.get('desc', ''),
            product.get('meta', ''),
            product.get('status', ''),
            product['images'],
            "https://t.me/stub123"
        ]
        values.append(row)
    
    # URL для полной перезаписи
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/A1:Z1000?valueInputOption=RAW&key={api_key}"
    
    # Данные для отправки
    data = {
        "values": values
    }
    
    print("🔄 Полная синхронизация Google Sheets...")
    
    try:
        # Отправляем запрос на полную перезапись
        response = requests.put(url, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            updated_cells = result.get('updatedCells', 0)
            updated_rows = result.get('updatedRows', 0)
            
            print("✅ ПОЛНАЯ СИНХРОНИЗАЦИЯ ЗАВЕРШЕНА!")
            print("=" * 40)
            print(f"📊 Товаров в таблице: {len(products)}")
            print(f"📋 Обновлено ячеек: {updated_cells}")
            print(f"📋 Обновлено строк: {updated_rows}")
            print(f"⏰ Время: {datetime.now().strftime('%H:%M:%S')}")
            print()
            print("🎉 Google Sheets полностью синхронизирован!")
            print("Удаленные товары убраны из таблицы!")
            
            # Создаем TSV файл для локального использования
            tsv_filename = f"sheets-sync-{datetime.now().strftime('%Y%m%d-%H%M%S')}.tsv"
            with open(tsv_filename, 'w', encoding='utf-8') as f:
                for row in values:
                    f.write("\t".join(str(cell) for cell in row) + "\n")
            
            print(f"💾 TSV файл создан: {tsv_filename}")
            return True
            
        else:
            print(f"❌ Ошибка синхронизации: {response.status_code}")
            print(f"Ответ: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при синхронизации: {e}")
        return False

def test_api_connection():
    """Тест подключения к API"""
    try:
        # Ищем конфигурацию в разных местах
        config_paths = [
            'google_api_config.json',
            'scripts/google_api_config.json',
            os.path.join(os.path.dirname(__file__), 'google_api_config.json')
        ]
        
        print(f"🔍 Ищу конфигурацию в: {config_paths}")
        
        config = None
        for path in config_paths:
            if os.path.exists(path):
                print(f"✅ Найден файл: {path}")
                with open(path, 'r') as f:
                    config = json.load(f)
                    break
            else:
                print(f"❌ Файл не найден: {path}")
        
        if not config:
            print("❌ Конфигурация не найдена")
            return False
            
        api_key = config.get('api_key')
        spreadsheet_id = config.get('spreadsheet_id')
        
        print(f"🔑 API ключ: {api_key[:10]}..." if api_key else "❌ API ключ не найден")
        print(f"📋 ID таблицы: {spreadsheet_id}" if spreadsheet_id else "❌ ID таблицы не найден")
        
        if not api_key or not spreadsheet_id:
            return False
        
        # Тестовый запрос
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}?key={api_key}"
        print(f"🌐 Тестирую URL: {url[:50]}...")
        response = requests.get(url, timeout=10)
        
        print(f"📡 Статус ответа: {response.status_code}")
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Ошибка теста: {e}")
        return False

if __name__ == "__main__":
    # Проверяем подключение
    print("🔍 Проверяю подключение к API...")
    if not test_api_connection():
        print("🔧 НАСТРОЙКА ТРЕБУЕТСЯ")
        print("=" * 30)
        print("Запустите настройку:")
        print("python setup_google_api.py")
        print()
        print("Это займет 5 минут и БЕСПЛАТНО!")
    else:
        print("✅ Подключение к API успешно!")
        # Запускаем обновление
        auto_update_google_sheets_api()
