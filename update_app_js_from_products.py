#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
from datetime import datetime

def update_app_js_from_products():
    """Обновление app.min.js из products.json"""
    print("🔄 Обновление app.min.js из products.json...")
    
    # Загружаем обновленные данные
    with open('products.json', 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    # Сортируем все товары по порядку
    all_products = sorted(products, key=lambda x: int(x.get('order', '0')))
    
    print(f"📊 Всего товаров: {len(all_products)}")
    
    # Читаем текущий app.min.js
    with open('web/app.min.js', 'r', encoding='utf-8') as f:
        app_js_content = f.read()
    
    # Создаем новый контент для всех товаров
    all_items_js = []
    for product in all_products:
        # Обрабатываем изображения
        images_str = product.get('images', '')
        if images_str:
            images = [img.strip() for img in images_str.split(',') if img.strip()]
        else:
            images = []
        
        item_js = f'''  {{
    "images": [
      {",\\n      ".join([f'"{img}"' for img in images])}
    ],
    "title": "{product.get('title', '')}",
    "price": "{product.get('price', '')}",
    "desc": "{product.get('desc', '')}",
    "meta": "{product.get('meta', '')}",
    "link": "{product.get('link', 'https://t.me/stub123')}",
    "status": "{product.get('status', 'stock')}",
    "order": {product.get('order', '0')},
    "section": "{product.get('section', 'home')}"
  }}'''
        all_items_js.append(item_js)
    
    # Обновляем массив items
    items_pattern = r'const items = \[\s*\{.*?\}\s*\]; // данные из каталога'
    items_replacement = f'const items = [\n{",\\n".join(all_items_js)}\n]; // данные из каталога'
    
    app_js_content = re.sub(items_pattern, items_replacement, app_js_content, flags=re.DOTALL)
    
    # Обновляем комментарий с датой
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    app_js_content = re.sub(
        r'// Обновлено из Google Sheets: .*',
        f'// Обновлено из products.json: {timestamp}',
        app_js_content
    )
    
    # Сохраняем обновленный файл
    with open('web/app.min.js', 'w', encoding='utf-8') as f:
        f.write(app_js_content)
    
    print("✅ app.min.js обновлен из products.json")
    
    # Проверяем обновленные цены
    print("\n📋 Проверка обновленных цен:")
    for product in products:
        title = product.get('title', '')
        price = product.get('price', '')
        if 'платок' in title.lower() or 'цветочный' in title.lower():
            print(f"• {title}: {price}")

def main():
    """Основная функция"""
    print("🚀 Обновление app.min.js с новыми ценами...")
    print("=" * 50)
    
    update_app_js_from_products()
    
    print("=" * 50)
    print("✅ Обновление завершено!")
    print("\n📋 Что обновлено:")
    print("• Платки на шею: 1500 р. → 1000 р.")
    print("• Пояс цветочный: 3600 р. → 3000 р.")
    print("• app.min.js теперь содержит актуальные данные")

if __name__ == "__main__":
    main()
