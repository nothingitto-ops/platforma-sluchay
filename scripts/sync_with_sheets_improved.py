#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import re

def clean_filename(name):
    """Очистка имени файла"""
    return re.sub(r'[^a-zA-Z0-9а-яА-Я]', '-', name.lower()).strip('-')

def sync_with_sheets_improved():
    """Улучшенная синхронизация данных из Google Sheets с нашими товарами"""
    
    # Загружаем данные из Google Sheets
    try:
        with open('sheets_data.json', 'r', encoding='utf-8') as f:
            sheets_data = json.load(f)
    except Exception as e:
        print(f"❌ Ошибка загрузки данных Google Sheets: {e}")
        return
    
    # Загружаем наши товары
    try:
        with open('products.json', 'r', encoding='utf-8') as f:
            our_products = json.load(f)
    except Exception as e:
        print(f"❌ Ошибка загрузки наших товаров: {e}")
        return
    
    print(f"📊 Найдено {len(sheets_data)} товаров в Google Sheets")
    print(f"📦 Найдено {len(our_products)} товаров в нашем каталоге")
    
    # Создаем словарь для сопоставления по папкам и изображениям
    sheets_by_folder = {}
    sheets_by_images = {}
    
    for sheet_product in sheets_data:
        # Извлекаем имя папки из изображений
        images = sheet_product.get('images', '')
        if images:
            # Берем первое изображение и извлекаем папку
            first_image = images.split('|')[0]
            if '/' in first_image:
                folder_name = first_image.split('/')[0]
                sheets_by_folder[folder_name] = sheet_product
            
            # Также создаем сопоставление по первым изображениям
            for img in images.split('|'):
                if img.strip():
                    sheets_by_images[img.strip()] = sheet_product
    
    print(f"📁 Найдено {len(sheets_by_folder)} товаров с папками в Google Sheets")
    print(f"🖼️ Найдено {len(sheets_by_images)} товаров по изображениям в Google Sheets")
    
    # Обновляем наши товары
    updated_count = 0
    for our_product in our_products:
        folder_path = our_product.get('folder', '')
        our_images = our_product.get('images', '')
        
        # Ищем соответствующий товар в Google Sheets
        sheet_product = None
        
        if folder_path:
            folder_name = os.path.basename(folder_path)
            sheet_product = sheets_by_folder.get(folder_name)
        
        # Если не нашли по папке, ищем по изображениям
        if not sheet_product and our_images:
            first_our_image = our_images.split('|')[0]
            sheet_product = sheets_by_images.get(first_our_image)
        
        if sheet_product:
            # Обновляем данные
            old_title = our_product['title']
            our_product['title'] = sheet_product['title']
            our_product['price'] = sheet_product['price']
            our_product['desc'] = sheet_product['desc']
            our_product['meta'] = sheet_product['meta']
            our_product['status'] = sheet_product['status']
            our_product['images'] = sheet_product['images']
            
            print(f"✅ Обновлен товар: {old_title} → {sheet_product['title']} - {sheet_product['price']}")
            updated_count += 1
        else:
            print(f"⚠️  Не найден в Google Sheets: {our_product['title']}")
    
    # Сохраняем обновленные данные
    try:
        with open('products.json', 'w', encoding='utf-8') as f:
            json.dump(our_products, f, ensure_ascii=False, indent=2)
        
        print(f"\n🎉 Синхронизация завершена!")
        print(f"📝 Обновлено товаров: {updated_count}")
        print(f"📁 Файл products.json обновлен")
        
        # Показываем статистику
        print(f"\n📊 Статистика:")
        for product in our_products:
            print(f"  • {product['title']} - {product['price']}")
        
    except Exception as e:
        print(f"❌ Ошибка сохранения: {e}")

if __name__ == "__main__":
    sync_with_sheets_improved()
