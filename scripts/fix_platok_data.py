#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime

def fix_platok_data():
    """Исправление данных платков - добавление серого платка и исправление описаний"""
    
    print("🔧 Исправление данных платков...")
    
    # Создаем правильные данные с двумя платками
    corrected_items = [
        {
            "images": ["product_1/product_1_1.jpg", "product_1/product_1_2.jpg", "product_1/product_1_3.jpg", "product_1/product_1_4.jpg"],
            "title": "Пояс цветочный",
            "price": "3600 р.",
            "desc": "Пояс, созданный совместно с nessffo, рисунок при помощи цианотипии",
            "meta": "Состав: 50% хлопок 50% лён",
            "link": "https://t.me/stub123",
            "status": "stock",
            "order": 1
        },
        {
            "images": ["product_2/product_2_1.jpg", "product_2/product_2_2.jpg", "product_2/product_2_3.jpg", "product_2/product_2_4.jpg"],
            "title": "Пояс-юбка",
            "price": "3000 р.",
            "desc": "Пояс-юбка из натурального материала со сборкой и широкими лентами",
            "meta": "Состав: 50% хлопок 50% лён",
            "link": "https://t.me/stub123",
            "status": "stock",
            "order": 2
        },
        {
            "images": ["product_3/product_3_1.jpg", "product_3/product_3_2.jpg", "product_3/product_3_3.jpg", "product_3/product_3_4.jpg"],
            "title": "Пояс P1",
            "price": "3500 р.",
            "desc": "Пояс, который имеет функцию мешка",
            "meta": "Состав: 100% (цвет на выбор)",
            "link": "https://t.me/stub123",
            "status": "stock",
            "order": 3
        },
        {
            "images": ["product_4/product_4_1.jpg", "product_4/product_4_2.jpg", "product_4/product_4_3.jpg", "product_4/product_4_4.jpg", "product_4/product_4_5.jpg", "product_4/product_4_6.jpg"],
            "title": "Рубашка",
            "price": "4000 р.",
            "desc": "Лёгкая рубашка со свободными рукавами",
            "meta": "Состав: 100% вареный хлопок (цвет на выбор)",
            "link": "https://t.me/stub123",
            "status": "preorder",
            "order": 4
        },
        {
            "images": ["product_5/product_5_1.jpg", "product_5/product_5_2.jpg", "product_5/product_5_3.jpg", "product_5/product_5_4.jpg", "product_5/product_5_5.jpg"],
            "title": "Штаны с поясом U2",
            "price": "5800 р.",
            "desc": "Cвободные штаны с укороченным поясом-юбкой",
            "meta": "Состав: 100% вареный хлопок",
            "link": "https://t.me/stub123",
            "status": "preorder",
            "order": 5
        },
        {
            "images": ["product_6/product_6_1.jpg", "product_6/product_6_2.jpg", "product_6/product_6_3.jpg", "product_6/product_6_4.jpg", "product_6/product_6_5.jpg", "product_6/product_6_6.jpg"],
            "title": "Рубашка с вышивкой",
            "price": "8000 р.",
            "desc": "Свободная рубашка из плотного хлопка с элементами ручной вышивки",
            "meta": "Состав: 100% хлопок · Деликатная стирка 30°C, после стирки рубашка может обрести эффект варёной ткани",
            "link": "https://t.me/stub123",
            "status": "preorder",
            "order": 6
        },
        {
            "images": ["product_7/product_7_1.jpg", "product_7/product_7_2.jpg", "product_7/product_7_3.jpg", "product_7/product_7_4.jpg"],
            "title": "Сумка через плечо",
            "price": "4500 р.",
            "desc": "Сумка, созданная совместно с nessffo, рисунок при помощи цианотипии",
            "meta": "Состав: 50% хлопок 50% лён",
            "link": "https://t.me/stub123",
            "status": "stock",
            "order": 7
        },
        {
            "images": ["product_8/product_8_1.jpg", "product_8/product_8_2.jpg", "product_8/product_8_3.jpg", "product_8/product_8_4.jpg"],
            "title": "Рубашка и шорты",
            "price": "7500 р.",
            "desc": "Комплект одежды, рубашка со свободными рукавами и шорты",
            "meta": "Состав: 100% вареный хлопок (цвет на выбор)",
            "link": "https://t.me/stub123",
            "status": "preorder",
            "order": 8
        },
        {
            "images": ["product_9/product_9_1.jpg", "product_9/product_9_2.jpg", "product_9/product_9_3.jpg"],
            "title": "Платок на шею",
            "price": "1500 р.",
            "desc": "Платок молочного цвета",
            "meta": "Состав: 100% жатая вискоза · Деликатная стирка 30°C",
            "link": "https://t.me/stub123",
            "status": "stock",
            "order": 9
        },
        {
            "images": ["product_10/product_10_1.jpg", "product_10/product_10_2.jpg", "product_10/product_10_3.jpg"],
            "title": "Штаны с поясом U1",
            "price": "6000 р.",
            "desc": "Свободные штаны с поясом-юбкой",
            "meta": "Состав: 100% вареный хлопок (цвет на выбор)",
            "link": "https://t.me/stub123",
            "status": "preorder",
            "order": 10
        },
        {
            "images": ["product_11/product_11_1.jpg", "product_11/product_11_2.jpg", "product_11/product_11_3.jpg", "product_11/product_11_4.jpg"],
            "title": "Фартук",
            "price": "3000 р.",
            "desc": "Фартук имеет карман и бретель, которая регулирует длину при помощи пуговицы",
            "meta": "Состав: 100% вареный хлопок (цвет на выбор)",
            "link": "https://t.me/stub123",
            "status": "stock",
            "order": 11
        },
        {
            "images": ["product_12/product_12_1.jpg", "product_12/product_12_2.jpg", "product_12/product_12_3.jpg", "product_12/product_12_4.jpg"],
            "title": "Платок на шею",
            "price": "1500 р.",
            "desc": "Платок серого цвета",
            "meta": "Состав: 100% жатая вискоза · Деликатная стирка 30°C",
            "link": "https://t.me/stub123",
            "status": "stock",
            "order": 12
        }
    ]
    
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
    
    print(f"\n🎉 Исправление платков завершено!")
    print(f"📊 Статистика:")
    print(f"   - Товаров обновлено: {len(corrected_items)}")
    print(f"   - Время обновления: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Показываем обновленные товары
    print(f"\n📝 Обновленные товары:")
    for item in corrected_items:
        print(f"   • {item['title']} - {item['price']}")
    
    # Показываем изменения платков
    print(f"\n🧣 Исправления платков:")
    print(f"   • Платок на шею (product_9): молочный цвет")
    print(f"   • Платок на шею (product_12): серый цвет")
    print(f"   • Оба платка добавлены в каталог")
    
    print(f"\n✅ Сайт готов к деплою!")
    print(f"🌐 Обновите страницу в браузере для проверки")
    
    return True

if __name__ == "__main__":
    fix_platok_data()
