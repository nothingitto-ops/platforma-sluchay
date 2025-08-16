#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
from datetime import datetime

def update_products_data():
    """Обновляет только данные товаров в app.min.js из products.json"""
    
    print("🔄 Обновление данных товаров в app.min.js...")
    
    # Загружаем данные из products.json
    try:
        with open('products.json', 'r', encoding='utf-8') as f:
            products = json.load(f)
        print(f"✅ Загружено {len(products)} товаров из products.json")
    except Exception as e:
        print(f"❌ Ошибка загрузки products.json: {e}")
        return False
    
    # Читаем текущий app.min.js
    try:
        with open('app.min.js', 'r', encoding='utf-8') as f:
            app_js_content = f.read()
        print("✅ Загружен app.min.js")
    except Exception as e:
        print(f"❌ Ошибка загрузки app.min.js: {e}")
        return False
    
    # Создаем новый массив items
    items_array = []
    for product in products:
        # Преобразуем строку изображений в массив
        images = product.get('images', '').split(',') if isinstance(product.get('images'), str) else product.get('images', [])
        images = [img.strip() for img in images if img.strip()]
        
        item = {
            "images": images,
            "title": product.get('title', ''),
            "price": product.get('price', ''),
            "desc": product.get('desc', ''),
            "meta": product.get('meta', ''),
            "link": product.get('link', 'https://t.me/stub123'),
            "status": product.get('status', 'stock'),
            "order": int(product.get('order', 999)),
            "section": product.get('section', 'home')
        }
        items_array.append(item)
    
    # Сортируем по order
    items_array.sort(key=lambda x: x['order'])
    
    # Находим и заменяем массив products в app.min.js
    start_marker = 'const products = ['
    start_pos = app_js_content.find(start_marker)
    if start_pos == -1:
        print("❌ Не найден маркер начала данных")
        return False
    
    # Ищем конец массива
    brace_count = 0
    in_items = False
    end_pos = start_pos
    for i, char in enumerate(app_js_content[start_pos:], start_pos):
        if char == '[':
            brace_count += 1
            in_items = True
        elif char == ']':
            brace_count -= 1
            if in_items and brace_count == 0:
                end_pos = i + 1
                break
    
    # Создаем новый JavaScript код для массива products
    items_js = 'const products = [\n'
    for i, item in enumerate(items_array):
        images_str = ',\n      '.join([f'"{img}"' for img in item['images']])
        items_js += f'''  {{
    "images": [
      {images_str}
    ],
    "title": "{item['title']}",
    "price": "{item['price']}",
    "desc": "{item['desc']}",
    "meta": "{item['meta']}",
    "link": "{item['link']}",
    "status": "{item['status']}",
    "order": {item['order']},
    "section": "{item['section']}"
  }}{',' if i < len(items_array) - 1 else ''}
'''
    items_js += '];'
    
    # Заменяем данные в файле
    new_content = app_js_content[:start_pos] + items_js + app_js_content[end_pos:]
    
    # Сохраняем обновленный файл
    try:
        with open('app.min.js', 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("✅ app.min.js обновлен с новыми данными товаров")
        return True
    except Exception as e:
        print(f"❌ Ошибка сохранения app.min.js: {e}")
        return False

if __name__ == "__main__":
    update_products_data()
