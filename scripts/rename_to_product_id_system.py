#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import json
from pathlib import Path

def load_sheets_data():
    """Загружаем данные из sheets_data.json"""
    with open('sheets_data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def get_id_mapping():
    """Создаем маппинг ID -> текущие папки на основе данных из sheets"""
    products = load_sheets_data()
    
    # Фильтруем только валидные записи (убираем дубликаты и тестовые)
    valid_products = []
    seen_ids = set()
    
    for product in products:
        if product['id'] and product['id'].isdigit() and product['id'] not in seen_ids:
            seen_ids.add(product['id'])
            valid_products.append(product)
    
    # Сортируем по ID
    valid_products.sort(key=lambda x: int(x['id']))
    
    # Создаем маппинг ID -> текущая папка
    id_mapping = {}
    for product in valid_products:
        product_id = product['id']
        images = product['images']
        
        # Извлекаем имя папки из первого изображения
        if images and '|' in images:
            first_image = images.split('|')[0]
            current_folder = first_image.split('/')[0]
            id_mapping[product_id] = {
                'current_folder': current_folder,
                'title': product['title'],
                'images': images.split('|')
            }
    
    return id_mapping

def rename_folders_and_files():
    """Переименовываем папки и файлы согласно новой системе ID"""
    id_mapping = get_id_mapping()
    img_dir = Path('web/img')
    
    print("🔄 Начинаем переименование папок и файлов...")
    
    for product_id, info in id_mapping.items():
        current_folder = info['current_folder']
        title = info['title']
        images = info['images']
        
        current_path = img_dir / current_folder
        new_folder_name = f"product_{product_id}"
        new_path = img_dir / new_folder_name
        
        print(f"📁 ID {product_id}: {current_folder} → {new_folder_name} ({title})")
        
        if not current_path.exists():
            print(f"⚠️  Папка {current_folder} не найдена, пропускаем")
            continue
        
        # Создаем новую папку
        if new_path.exists():
            print(f"⚠️  Папка {new_folder_name} уже существует, удаляем старую")
            shutil.rmtree(new_path)
        
        new_path.mkdir(exist_ok=True)
        
        # Переименовываем файлы
        for i, old_image_path in enumerate(images, 1):
            old_file_path = img_dir / old_image_path
            new_file_name = f"product_{product_id}_{i}.jpg"
            new_file_path = new_path / new_file_name
            
            if old_file_path.exists():
                shutil.copy2(old_file_path, new_file_path)
                print(f"  📄 {old_image_path} → {new_file_name}")
            else:
                print(f"  ⚠️  Файл {old_image_path} не найден")
        
        # Удаляем старую папку
        shutil.rmtree(current_path)
        print(f"  🗑️  Удалена старая папка {current_folder}")
    
    print("✅ Переименование завершено!")

def update_sheets_data():
    """Обновляем данные в sheets_data.json с новыми путями к изображениям"""
    products = load_sheets_data()
    
    print("📝 Обновляем пути к изображениям в sheets_data.json...")
    
    for product in products:
        if product['id'] and product['id'].isdigit():
            product_id = product['id']
            images = product['images']
            
            if images and '|' in images:
                # Создаем новые пути к изображениям
                new_images = []
                for i in range(1, len(images.split('|')) + 1):
                    new_images.append(f"product_{product_id}/product_{product_id}_{i}.jpg")
                
                product['images'] = '|'.join(new_images)
                print(f"🔄 ID {product_id}: обновлены пути к изображениям")
    
    # Сохраняем обновленные данные
    with open('sheets_data.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    print("✅ sheets_data.json обновлен!")

def create_tsv_for_sheets():
    """Создаем TSV файл для обновления Google Sheets"""
    products = load_sheets_data()
    
    print("📊 Создаем TSV файл для Google Sheets...")
    
    # Фильтруем только валидные записи
    valid_products = []
    seen_ids = set()
    
    for product in products:
        if product['id'] and product['id'].isdigit() and product['id'] not in seen_ids:
            seen_ids.add(product['id'])
            valid_products.append(product)
    
    # Сортируем по ID
    valid_products.sort(key=lambda x: int(x['id']))
    
    # Создаем TSV
    tsv_content = "ID\tSection\tTitle\tPrice\tDesc\tMeta\tStatus\tImages\tLink\n"
    
    for product in valid_products:
        row = [
            product['id'],
            product['section'],
            product['title'],
            product['price'],
            product['desc'],
            product['meta'],
            product['status'],
            product['images'],
            product['link']
        ]
        tsv_content += '\t'.join(row) + '\n'
    
    # Сохраняем TSV файл
    timestamp = int(time.time())
    filename = f"sheets-update-{timestamp}.tsv"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(tsv_content)
    
    print(f"✅ TSV файл создан: {filename}")
    return filename

if __name__ == "__main__":
    import time
    
    print("🚀 Начинаем обновление структуры файлов согласно новой системе ID...")
    
    # 1. Переименовываем папки и файлы
    rename_folders_and_files()
    
    # 2. Обновляем sheets_data.json
    update_sheets_data()
    
    # 3. Создаем TSV для Google Sheets
    tsv_file = create_tsv_for_sheets()
    
    print(f"\n🎉 Обновление завершено!")
    print(f"📁 TSV файл для Google Sheets: {tsv_file}")
    print(f"📝 Обновите Google Sheets, используя данные из файла {tsv_file}")
