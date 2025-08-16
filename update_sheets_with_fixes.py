#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import gspread
from google.oauth2.credentials import Credentials
from datetime import datetime

def update_sheets_with_fixes():
    """Обновление Google Sheets с исправленными данными"""
    try:
        print("🔄 Обновление Google Sheets с исправленными данными...")
        
        # Загружаем конфигурацию
        with open('google_api_config.json', 'r') as f:
            config = json.load(f)
            spreadsheet_id = config.get('spreadsheet_id')
        
        if not spreadsheet_id:
            print("❌ ID таблицы не найден в конфигурации")
            return False
        
        # Настройки Google Sheets API
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        CREDENTIALS_FILE = 'token.json'
        
        # Получаем клиент для работы с Google Sheets
        creds = Credentials.from_authorized_user_file(CREDENTIALS_FILE, scopes=SCOPES)
        client = gspread.authorize(creds)
        
        # Открываем таблицу
        spreadsheet = client.open_by_key(spreadsheet_id)
        worksheet = spreadsheet.sheet1
        
        # Загружаем исправленные данные из products.json
        with open('products.json', 'r', encoding='utf-8') as f:
            products = json.load(f)
        
        print(f"📊 Загружено {len(products)} товаров для обновления")
        
        # Получаем все данные из таблицы
        all_values = worksheet.get_all_values()
        if not all_values:
            print("❌ Таблица пуста!")
            return False
        
        headers = all_values[0]
        existing_data = all_values[1:]
        
        # Обновляем данные в таблице
        updated_count = 0
        
        for product in products:
            product_id = str(product.get('id', ''))
            
            # Ищем строку по ID
            row_to_update = None
            for i, row in enumerate(existing_data):
                if len(row) > 0 and str(row[0]) == product_id:
                    row_to_update = i + 2  # +2 потому что 1 - заголовки, и индексация с 0
                    break
            
            if row_to_update:
                # Подготавливаем данные для обновления
                update_data = [
                    product.get('id', ''),
                    product.get('order', ''),
                    product.get('section', ''),
                    product.get('title', ''),
                    product.get('price', ''),
                    product.get('desc', ''),
                    product.get('meta', ''),
                    product.get('status', ''),
                    product.get('images', ''),
                    product.get('link', '')
                ]
                
                # Обновляем строку в таблице
                worksheet.update(f'A{row_to_update}:J{row_to_update}', [update_data])
                updated_count += 1
                print(f"✅ Обновлен товар: {product.get('title', 'Unknown')} (ID: {product_id})")
            else:
                print(f"⚠️ Товар с ID {product_id} не найден в таблице")
        
        print(f"✅ Обновление завершено! Обновлено товаров: {updated_count}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка обновления Google Sheets: {e}")
        return False

if __name__ == "__main__":
    update_sheets_with_fixes()
