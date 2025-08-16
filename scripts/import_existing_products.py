#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import re
from datetime import datetime

def clean_filename(name):
    """Очистка имени файла"""
    return re.sub(r'[^a-zA-Z0-9а-яА-Я]', '-', name.lower()).strip('-')

def import_existing_products():
    """Импорт существующих товаров из папок"""
    products = []
    img_dir = "img"
    
    if not os.path.exists(img_dir):
        print("❌ Папка img не найдена!")
        return
    
    # Проходим по всем папкам в img
    for folder_name in os.listdir(img_dir):
        folder_path = os.path.join(img_dir, folder_name)
        
        # Пропускаем файлы, только папки
        if not os.path.isdir(folder_path):
            continue
        
        # Пропускаем системные файлы
        if folder_name.startswith('.'):
            continue
        
        print(f"🔍 Обрабатываем папку: {folder_name}")
        
        # Ищем изображения в папке
        images = []
        for file in os.listdir(folder_path):
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                images.append(file)
        
        if not images:
            print(f"   ⚠️  Нет изображений в папке {folder_name}")
            continue
        
        # Сортируем изображения по номеру
        def sort_key(img):
            # Извлекаем номер из имени файла (например, "product-1.jpg" -> 1)
            match = re.search(r'-(\d+)\.', img)
            return int(match.group(1)) if match else 0
        
        images.sort(key=sort_key)
        
        # Создаем название товара из имени папки
        title = folder_name.replace('-', ' ').title()
        
        # Создаем товар
        product = {
            "title": title,
            "desc": f"Товар {title}",
            "price": "0",
            "status": "active",
            "images": "|".join(images),
            "folder": folder_path,
            "created": datetime.now().isoformat()
        }
        
        products.append(product)
        print(f"   ✅ Добавлен товар: {title} ({len(images)} изображений)")
    
    # Сохраняем в файл
    if products:
        with open('products.json', 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        
        print(f"\n🎉 Импортировано {len(products)} товаров!")
        print("📁 Файл products.json создан")
        print("\nТеперь запустите приложение: python catalog_app.py")
    else:
        print("❌ Не найдено товаров для импорта")

if __name__ == "__main__":
    import_existing_products()
