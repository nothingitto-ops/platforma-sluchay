#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime

def update_js_from_json():
    """Обновляет app.min.js из products.json"""
    
    print("🔄 Обновление app.min.js из products.json...")
    
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
            js_content = f.read()
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
    
    # Создаем новый JavaScript код
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Создаем JSON строку и убираем внешние скобки
    json_str = json.dumps(items_array, ensure_ascii=False, indent=2)
    # Убираем первую и последнюю строки (открывающую и закрывающую скобки)
    json_lines = json_str.split('\n')
    json_content = '\n'.join(json_lines[1:-1])  # Убираем первую и последнюю строки
    
    new_items_js = f"""// Обновлено из products.json: {timestamp}
const DEFAULT_TG = 'https://t.me/stub123';
/* ===== DATA (главная) ===== */
const items = [
{json_content}
];"""
    
    # Находим и заменяем старый массив items
    import re
    pattern = r'// Обновлено из products\.json:.*?\nconst DEFAULT_TG =.*?\n/\* ===== DATA \(главная\) ===== \*/\nconst items = \[\n.*?\n\];'
    
    if re.search(pattern, js_content, re.DOTALL):
        new_js_content = re.sub(pattern, new_items_js, js_content, flags=re.DOTALL)
        print("✅ Найден и заменен массив items")
    else:
        print("⚠️ Не найден старый массив items, добавляем в начало")
        # Если не нашли, добавляем в начало файла
        new_js_content = new_items_js + "\n\n" + js_content
    
    # Сохраняем обновленный файл
    try:
        with open('app.min.js', 'w', encoding='utf-8') as f:
            f.write(new_js_content)
        print("✅ app.min.js обновлен")
        
        # Создаем резервную копию
        backup_name = f"app.min.js.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        with open(backup_name, 'w', encoding='utf-8') as f:
            f.write(js_content)
        print(f"✅ Создана резервная копия: {backup_name}")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка сохранения: {e}")
        return False

if __name__ == "__main__":
    success = update_js_from_json()
    if success:
        print("\n🎉 JavaScript файл успешно обновлен!")
        print("🔄 Обновите страницу в браузере для применения изменений")
    else:
        print("\n❌ Обновление не удалось")
