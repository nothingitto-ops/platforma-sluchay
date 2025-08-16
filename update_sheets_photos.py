#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import gspread
from google.oauth2.credentials import Credentials
from datetime import datetime

def update_sheets_photos():
    """Обновление фотографий в Google Sheets"""
    try:
        print("📤 Обновление фотографий в Google Sheets...")
        
        # Загружаем конфигурацию
        with open('google_api_config.json', 'r') as f:
            config = json.load(f)
            spreadsheet_id = config.get('spreadsheet_id')
        
        if not spreadsheet_id:
            print("❌ ID таблицы не найден")
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
        
        # Получаем все данные
        all_values = worksheet.get_all_values()
        if not all_values:
            print("❌ Таблица пуста")
            return False
        
        headers = all_values[0]
        data = all_values[1:]
        
        # Находим строку с товаром ID=7 (Сумка через плечо)
        row_to_update = None
        for i, row in enumerate(data, 2):  # Начинаем с 2, так как 1 - заголовки
            if len(row) > 0 and str(row[0]) == "7":
                row_to_update = i
                break
        
        if row_to_update is None:
            print("❌ Товар с ID 7 не найден в таблице")
            return False
        
        # Новые данные для товара ID=7
        new_images = "product_7/product_7_1.jpg,product_7/product_7_2.jpg,product_7/product_7_3.jpg,product_7/product_7_4.jpg"
        
        # Обновляем ячейку с изображениями (колонка I, 9-я колонка)
        worksheet.update_cell(row_to_update, 9, new_images)
        
        print(f"✅ Фотографии обновлены в Google Sheets (строка {row_to_update})")
        print(f"📸 Новые фотографии: {new_images}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка обновления Google Sheets: {e}")
        return False

def main():
    print("📸 Обновление фотографий в Google Sheets")
    print("=" * 40)
    
    success = update_sheets_photos()
    
    if success:
        print("\n✅ Фотографии успешно обновлены в Google Sheets!")
        print("🔄 Теперь запустите Platforma Manager для синхронизации данных")
    else:
        print("\n❌ Ошибка обновления фотографий")

if __name__ == "__main__":
    main()
