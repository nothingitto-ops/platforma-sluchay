#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import gspread
from google.oauth2.credentials import Credentials
from datetime import datetime

def remove_dots_final():
    """Удаление точек из всех описаний товаров"""
    print("🔧 Удаление точек из всех описаний...")
    
    # Загружаем данные
    with open('products.json', 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    # Удаляем точки из описаний
    updated = False
    
    for product in products:
        desc = product.get('desc', '')
        if desc and desc.endswith('.'):
            new_desc = desc.rstrip('.')
            if new_desc != desc:
                print(f"❌ Убираем точку из описания '{product.get('title', '')}': {desc} → {new_desc}")
                product['desc'] = new_desc
                product['updated'] = datetime.now().isoformat()
                updated = True
        else:
            print(f"✅ Описание '{product.get('title', '')}' уже без точки: {desc}")
    
    # Сохраняем изменения
    if updated:
        with open('products.json', 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        print("✅ products.json обновлен")
        
        # Обновляем Google Sheets
        try:
            SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
            CREDENTIALS_FILE = 'token.json'
            
            creds = Credentials.from_authorized_user_file(CREDENTIALS_FILE, scopes=SCOPES)
            client = gspread.authorize(creds)
            
            sheet = client.open_by_key('1FLlyjpSd9EBOxZC8f0B6-iKRpKCMxcTRqWOHlgUpFoQ').sheet1
            
            # Получаем все данные
            all_values = sheet.get_all_values()
            headers = all_values[0]
            
            # Обновляем строки с точками в описаниях
            for row_idx, row in enumerate(all_values[1:], start=2):
                if len(row) >= 6:  # Проверяем, что есть Desc
                    try:
                        current_desc = row[5]  # Desc находится в колонке F (индекс 5)
                        if current_desc and current_desc.endswith('.'):
                            new_desc = current_desc.rstrip('.')
                            if new_desc != current_desc:
                                # Обновляем только описание
                                update_data = [
                                    row[0],  # ID
                                    row[1],  # Order
                                    row[2],  # Section
                                    row[3],  # Title
                                    row[4],  # Price
                                    new_desc,   # Desc (без точки)
                                    row[6] if len(row) > 6 else '',  # Meta
                                    row[7] if len(row) > 7 else '',  # Status
                                    row[8] if len(row) > 8 else '',  # Images
                                    row[9] if len(row) > 9 else '',  # Link
                                    row[10] if len(row) > 10 else ''  # Hash
                                ]
                                
                                sheet.update(f'A{row_idx}:K{row_idx}', [update_data])
                                print(f"✅ Обновлена строка {row_idx}: убрана точка из описания")
                                
                    except (ValueError, IndexError):
                        continue
            
            print("✅ Google Sheets обновлен")
            
        except Exception as e:
            print(f"❌ Ошибка обновления Google Sheets: {e}")
    else:
        print("✅ Все описания уже без точек!")

if __name__ == "__main__":
    remove_dots_final()
