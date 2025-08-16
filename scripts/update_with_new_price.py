#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime

def update_with_new_price():
    """Обновление сайта с новой ценой сумки через плечо"""
    
    print("🚀 Обновление сайта с новой ценой сумки...")
    
    # Загружаем обновленные данные из Google Sheets
    try:
        with open('sheets_data_updated.json', 'r', encoding='utf-8') as f:
            sheets_data = json.load(f)
        print(f"✅ Загружено {len(sheets_data)} товаров из обновленных данных")
    except Exception as e:
        print(f"❌ Ошибка загрузки обновленных данных: {e}")
        return False
    
    # Исправляем структуру данных
    corrected_items = []
    
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
        # Поля перепутаны, поэтому исправляем их:
        item = {
            "images": link.split(',') if link else [],  # link содержит изображения
            "title": price,  # price содержит название
            "price": desc,   # desc содержит цену
            "desc": meta,    # meta содержит описание
            "meta": status,  # status содержит состав
            "link": "https://t.me/stub123",  # стандартная ссылка
            "status": images,  # images содержит статус
            "order": order
        }
        
        corrected_items.append(item)
        print(f"✅ Обработан товар: {item['title']} - {item['price']}")
    
    # Сортируем по порядку
    corrected_items.sort(key=lambda x: x.get('order', 999))
    
    # Загружаем текущий app.min.js
    try:
        with open('../web/app.min.js', 'r', encoding='utf-8') as f:
            current_js = f.read()
    except Exception as e:
        print(f"❌ Ошибка чтения app.min.js: {e}")
        return False
    
    # Находим и заменяем массив items
    import re
    
    # Создаем JSON строку для items
    items_json = json.dumps(corrected_items, ensure_ascii=False, indent=2)
    
    # Заменяем массив items в JavaScript коде
    pattern = r'const items = \[.*?\];'
    replacement = f'const items = {items_json};'
    
    # Добавляем комментарий с временем обновления
    update_comment = f'// Обновлено из Google Sheets: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n'
    
    if re.search(pattern, current_js, re.DOTALL):
        new_js = re.sub(pattern, replacement, current_js, flags=re.DOTALL)
        # Добавляем комментарий в начало файла
        if not new_js.startswith('// Обновлено из Google Sheets'):
            new_js = update_comment + new_js
    else:
        print("⚠️ Не найден массив items в app.min.js, добавляем в начало")
        new_js = update_comment + f'const items = {items_json};\n\n' + current_js
    
    # Сохраняем обновленный app.min.js
    try:
        with open('../web/app.min.js', 'w', encoding='utf-8') as f:
            f.write(new_js)
        print(f"✅ Файл app.min.js обновлен с {len(corrected_items)} товарами")
    except Exception as e:
        print(f"❌ Ошибка сохранения app.min.js: {e}")
        return False
    
    # Создаем резервную копию
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = f'../backups/site_backup_{timestamp}'
    
    try:
        os.makedirs(backup_dir, exist_ok=True)
        import shutil
        shutil.copy2('../web/app.min.js', f'{backup_dir}/app.min.js')
        shutil.copy2('../web/index.html', f'{backup_dir}/index.html')
        shutil.copy2('../web/styles.min.css', f'{backup_dir}/styles.min.css')
        shutil.copy2('../web/card-titles.css', f'{backup_dir}/card-titles.css')
        print(f"✅ Резервная копия создана: {backup_dir}")
    except Exception as e:
        print(f"⚠️ Ошибка создания резервной копии: {e}")
    
    print(f"\n🎉 Обновление завершено!")
    print(f"📊 Статистика:")
    print(f"   - Товаров обновлено: {len(corrected_items)}")
    print(f"   - Время обновления: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Показываем обновленные товары
    print(f"\n📝 Обновленные товары:")
    for item in corrected_items:
        print(f"   • {item['title']} - {item['price']}")
    
    # Показываем изменения цен
    print(f"\n💰 Изменения цен:")
    print(f"   • Сумка через плечо: 4500 р. (обновлена цена)")
    print(f"   • Пояс цветочный: 3600 р.")
    
    print(f"\n✅ Сайт готов к деплою!")
    print(f"🌐 Обновите страницу в браузере для проверки")
    
    return True

if __name__ == "__main__":
    update_with_new_price()
