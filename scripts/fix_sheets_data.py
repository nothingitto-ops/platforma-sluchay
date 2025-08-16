#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from datetime import datetime

def fix_sheets_data():
    """Исправление структуры данных из Google Sheets"""
    
    print("🔧 Исправление структуры данных из Google Sheets...")
    
    # Загружаем данные из Google Sheets
    try:
        with open('sheets_data.json', 'r', encoding='utf-8') as f:
            sheets_data = json.load(f)
        print(f"✅ Загружено {len(sheets_data)} товаров из Google Sheets")
    except Exception as e:
        print(f"❌ Ошибка загрузки данных Google Sheets: {e}")
        return False
    
    # Исправляем структуру данных
    fixed_items = []
    
    for sheet_product in sheets_data:
        # Правильная структура данных из Google Sheets:
        # id, section, title, price, desc, meta, status, images, link
        
        product_id = sheet_product.get('id', '')
        section = sheet_product.get('section', '')
        title = sheet_product.get('title', '')
        price = sheet_product.get('price', '')
        desc = sheet_product.get('desc', '')
        meta = sheet_product.get('meta', '')
        status = sheet_product.get('status', '')
        images = sheet_product.get('images', '')
        link = sheet_product.get('link', '')
        
        # Определяем порядок на основе ID
        try:
            order = int(product_id) if product_id.isdigit() else 999
        except:
            order = 999
        
        # Создаем правильную структуру товара
        item = {
            "images": images.split(',') if images else [],
            "title": title,
            "price": price,
            "desc": desc,
            "meta": meta,
            "link": link,
            "status": status,
            "order": order
        }
        
        fixed_items.append(item)
        print(f"✅ Исправлен товар: {title} - {price}")
    
    # Сортируем по порядку
    fixed_items.sort(key=lambda x: x.get('order', 999))
    
    # Сохраняем исправленные данные
    try:
        with open('fixed_sheets_data.json', 'w', encoding='utf-8') as f:
            json.dump(fixed_items, f, ensure_ascii=False, indent=2)
        print(f"✅ Исправленные данные сохранены в fixed_sheets_data.json")
    except Exception as e:
        print(f"❌ Ошибка сохранения: {e}")
        return False
    
    print(f"\n🎉 Исправление завершено!")
    print(f"📊 Статистика:")
    print(f"   - Товаров исправлено: {len(fixed_items)}")
    print(f"   - Время исправления: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Показываем исправленные товары
    print(f"\n📝 Исправленные товары:")
    for item in fixed_items:
        print(f"   • {item['title']} - {item['price']}")
    
    return True

if __name__ == "__main__":
    fix_sheets_data()
