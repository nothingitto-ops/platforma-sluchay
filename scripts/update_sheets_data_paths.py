#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import time

def update_sheets_data():
    """Обновляем пути к изображениям в sheets_data.json согласно новой системе ID"""
    
    # Загружаем текущие данные
    with open('sheets_data.json', 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    print("📝 Обновляем пути к изображениям в sheets_data.json...")
    
    # Маппинг ID -> количество изображений (из текущих данных)
    id_image_counts = {
        "1": 4,  # shawl-2
        "2": 4,  # apron-1  
        "3": 3,  # belt-trousers
        "4": 3,  # shawl-1
        "5": 4,  # shirt-pants-white
        "6": 5,  # nessffo-bag
        "7": 6,  # shirt-olive
        "8": 5,  # pants-with-belt-skirt-U2
        "9": 6,  # shirt-white
        "10": 4, # belt-bag-p1
        "11": 4, # belt-skirt-1
        "12": 4  # belt-nessffo-1
    }
    
    for product in products:
        if product['id'] and product['id'].isdigit():
            product_id = product['id']
            
            if product_id in id_image_counts:
                # Создаем новые пути к изображениям
                image_count = id_image_counts[product_id]
                new_images = []
                
                for i in range(1, image_count + 1):
                    new_images.append(f"product_{product_id}/product_{product_id}_{i}.jpg")
                
                product['images'] = '|'.join(new_images)
                print(f"🔄 ID {product_id}: обновлены пути к изображениям ({image_count} файлов)")
    
    # Сохраняем обновленные данные
    with open('sheets_data.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    print("✅ sheets_data.json обновлен!")

def create_tsv_for_sheets():
    """Создаем TSV файл для обновления Google Sheets"""
    with open('sheets_data.json', 'r', encoding='utf-8') as f:
        products = json.load(f)
    
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
    print("🚀 Обновляем данные для новой системы ID...")
    
    # 1. Обновляем sheets_data.json
    update_sheets_data()
    
    # 2. Создаем TSV для Google Sheets
    tsv_file = create_tsv_for_sheets()
    
    print(f"\n🎉 Обновление завершено!")
    print(f"📁 TSV файл для Google Sheets: {tsv_file}")
    print(f"📝 Обновите Google Sheets, используя данные из файла {tsv_file}")
