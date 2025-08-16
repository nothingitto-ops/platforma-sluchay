#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import shutil
from datetime import datetime
import gspread
from google.oauth2.credentials import Credentials
import zipfile

def update_prices_in_products():
    """Обновление цен в файле products.json"""
    print("🔄 Обновление цен в products.json...")
    
    # Загружаем текущие данные
    with open('products.json', 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    updated_count = 0
    
    # Обновляем цены
    for product in products:
        product_id = product.get('id', '')
        title = product.get('title', '').lower()
        section = product.get('section', '')
        
        # Платки на шею (ID 9 и 12)
        if product_id in ['9', '12'] and 'платок' in title:
            if product['price'] != '1000 р.':
                old_price = product['price']
                product['price'] = '1000 р.'
                product['updated'] = datetime.now().isoformat()
                print(f"✅ Платок (ID {product_id}): {old_price} → 1000 р.")
                updated_count += 1
        
        # Пояс цветочный (ID 1 в разделе nessffo)
        elif product_id == '1' and section == 'nessffo' and 'цветочный' in title:
            if product['price'] != '3000 р.':
                old_price = product['price']
                product['price'] = '3000 р.'
                product['updated'] = datetime.now().isoformat()
                print(f"✅ Пояс цветочный (ID {product_id}): {old_price} → 3000 р.")
                updated_count += 1
    
    # Сохраняем обновленные данные
    with open('products.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Обновлено {updated_count} товаров в products.json")
    return products

def update_google_sheets(products):
    """Обновление Google Sheets с новыми ценами"""
    try:
        print("🔄 Обновление Google Sheets...")
        
        # Проверяем наличие файлов OAuth2
        if not os.path.exists('token.json') or not os.path.exists('google_api_config.json'):
            print("❌ Файлы OAuth2 не найдены")
            return False
        
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
            print("❌ Таблица пуста!")
            return False
        
        headers = all_values[0]
        data = all_values[1:]
        
        # Создаем словарь обновленных товаров
        updated_products = {}
        for product in products:
            product_id = str(product.get('id', ''))
            title = product.get('title', '').lower()
            section = product.get('section', '')
            
            # Только товары с обновленными ценами
            if (product_id in ['9', '12'] and 'платок' in title) or \
               (product_id == '1' and section == 'nessffo' and 'цветочный' in title):
                updated_products[product_id] = product
        
        # Обновляем строки в таблице
        updated_count = 0
        for i, row in enumerate(data, 2):  # Начинаем с 2, так как 1 - заголовки
            if len(row) > 0:
                product_id = str(row[0])
                if product_id in updated_products:
                    product = updated_products[product_id]
                    
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
                    worksheet.update(f'A{i}:J{i}', [update_data])
                    updated_count += 1
                    print(f"📝 Обновлена строка {i}: {product.get('title', '')} → {product.get('price', '')}")
        
        print(f"✅ Обновлено {updated_count} товаров в Google Sheets")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка обновления Google Sheets: {e}")
        return False

def create_deploy_archive():
    """Создание архива для деплоя"""
    try:
        print("📦 Создание архива для деплоя...")
        
        # Создаем папку для деплоя
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        deploy_folder = f"deploy_{timestamp}"
        os.makedirs(deploy_folder, exist_ok=True)
        
        # Копируем файлы сайта
        web_files = [
            'web/index.html',
            'web/app.min.js',
            'web/styles.min.css',
            'web/mobile.overrides.css',
            'web/card-titles.css'
        ]
        
        for file_path in web_files:
            if os.path.exists(file_path):
                # Создаем папки если нужно
                dest_path = os.path.join(deploy_folder, file_path.replace('web/', ''))
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                shutil.copy2(file_path, dest_path)
                print(f"📄 Скопирован: {file_path}")
        
        # Копируем изображения
        if os.path.exists('web/img'):
            shutil.copytree('web/img', os.path.join(deploy_folder, 'img'))
            print("📁 Скопированы изображения")
        
        # Копируем обновленный products.json
        shutil.copy2('products.json', os.path.join(deploy_folder, 'products.json'))
        print("📄 Скопирован products.json")
        
        # Создаем архив
        archive_name = f"platforma_deploy_{timestamp}.zip"
        with zipfile.ZipFile(archive_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(deploy_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, deploy_folder)
                    zipf.write(file_path, arcname)
        
        # Удаляем временную папку
        shutil.rmtree(deploy_folder)
        
        print(f"✅ Архив создан: {archive_name}")
        return archive_name
        
    except Exception as e:
        print(f"❌ Ошибка создания архива: {e}")
        return None

def main():
    """Основная функция"""
    print("🚀 Начинаем обновление цен и деплой...")
    print("=" * 50)
    
    # 1. Обновляем цены в products.json
    products = update_prices_in_products()
    
    # 2. Обновляем Google Sheets
    sheets_updated = update_google_sheets(products)
    
    # 3. Создаем архив для деплоя
    archive_name = create_deploy_archive()
    
    print("=" * 50)
    print("✅ Обновление завершено!")
    
    if sheets_updated:
        print("✅ Google Sheets обновлен")
    else:
        print("⚠️ Google Sheets не обновлен (проверьте настройки OAuth2)")
    
    if archive_name:
        print(f"✅ Архив для деплоя: {archive_name}")
    else:
        print("❌ Ошибка создания архива")
    
    print("\n📋 Что было обновлено:")
    print("• Платки на шею (ID 9, 12): 1500 р. → 1000 р.")
    print("• Пояс цветочный (ID 1): 3600 р. → 3000 р.")

if __name__ == "__main__":
    main()
