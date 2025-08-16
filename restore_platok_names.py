#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import gspread
from google.oauth2.credentials import Credentials
from datetime import datetime

def restore_platok_names():
    """Восстановление оригинальных названий платков с уникальными ID"""
    print("🔄 Восстановление названий платков...")
    
    # Загружаем данные
    with open('products.json', 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    # Восстанавливаем оригинальные названия
    updated = False
    
    for product in products:
        title = product.get('title', '')
        product_id = product.get('id', '')
        
        if "Платок на шею (серый)" in title:
            new_title = "Платок на шею"
            if product.get('title') != new_title:
                product['title'] = new_title
                product['updated'] = datetime.now().isoformat()
                updated = True
                print(f"✅ Восстановлено название: ID {product_id} → {new_title}")
        
        elif "Платок на шею (молочный)" in title:
            new_title = "Платок на шею"
            if product.get('title') != new_title:
                product['title'] = new_title
                product['updated'] = datetime.now().isoformat()
                updated = True
                print(f"✅ Восстановлено название: ID {product_id} → {new_title}")
    
    if updated:
        # Сохраняем обновленные данные
        with open('products.json', 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        print("✅ products.json обновлен")
        
        # Обновляем Google Sheets
        update_google_sheets(products)
        
        return True
    else:
        print("ℹ️ Изменений не требуется")
        return False

def update_google_sheets(products):
    """Обновление Google Sheets"""
    try:
        print("📊 Обновление Google Sheets...")
        
        # Настройка OAuth2
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        CREDENTIALS_FILE = 'token.json'
        
        # Используем правильный способ авторизации
        creds = Credentials.from_authorized_user_file(CREDENTIALS_FILE, scopes=SCOPES)
        client = gspread.authorize(creds)
        
        # Открываем таблицу
        sheet = client.open_by_key('1FLlyjpSd9EBOxZC8f0B6-iKRpKCMxcTRqWOHlgUpFoQ').sheet1
        
        # Получаем заголовки
        headers = sheet.row_values(1)
        print(f"📋 Заголовки: {headers}")
        
        # Находим индексы колонок
        title_idx = headers.index('Title') if 'Title' in headers else -1
        
        if title_idx == -1:
            print("❌ Не найдена колонка Title в таблице")
            return False
        
        # Обновляем названия в таблице
        updated_rows = 0
        
        for product in products:
            title = product.get('title', '')
            product_id = product.get('id', '')
            
            # Ищем строку с этим товаром по ID
            try:
                cell = sheet.find(product_id)
                row_num = cell.row
                
                # Обновляем название
                sheet.update_cell(row_num, title_idx + 1, title)
                
                updated_rows += 1
                print(f"✅ Обновлена строка {row_num}: ID {product_id} → {title}")
                
            except gspread.exceptions.CellNotFound:
                print(f"⚠️ Товар с ID {product_id} не найден в таблице")
        
        print(f"✅ Обновлено строк в Google Sheets: {updated_rows}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка обновления Google Sheets: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Восстановление названий платков...")
    
    if restore_platok_names():
        print("\n✅ Восстановление завершено успешно!")
        print("\n📋 Итоговые изменения:")
        print("• Платок на шею (ID 9): оригинальное название")
        print("• Платок на шею (ID 12): оригинальное название")
        print("• Уникальные ID сохранены")
    else:
        print("\nℹ️ Восстановление не требуется")
