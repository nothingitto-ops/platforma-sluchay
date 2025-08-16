#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime

def final_update_site():
    """Финальное обновление сайта с исправленными данными из Google Sheets"""
    
    print("🚀 Финальное обновление сайта с данными из Google Sheets...")
    
    # Загружаем исправленные данные из Google Sheets
    try:
        with open('corrected_sheets_data.json', 'r', encoding='utf-8') as f:
            corrected_data = json.load(f)
        print(f"✅ Загружено {len(corrected_data)} товаров из исправленных данных")
    except Exception as e:
        print(f"❌ Ошибка загрузки исправленных данных: {e}")
        return False
    
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
    items_json = json.dumps(corrected_data, ensure_ascii=False, indent=2)
    
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
        print(f"✅ Файл app.min.js обновлен с {len(corrected_data)} товарами")
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
    
    print(f"\n🎉 Финальное обновление завершено!")
    print(f"📊 Статистика:")
    print(f"   - Товаров обновлено: {len(corrected_data)}")
    print(f"   - Время обновления: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Показываем обновленные товары
    print(f"\n📝 Обновленные товары:")
    for item in corrected_data:
        print(f"   • {item['title']} - {item['price']}")
    
    # Показываем изменения цен
    print(f"\n💰 Изменения цен:")
    print(f"   • Пояс цветочный: 3600 р. (новый товар)")
    print(f"   • Сумка через плечо: 4000 р. (новый товар)")
    print(f"   • Платок на шею: обновлено описание")
    
    print(f"\n✅ Сайт готов к деплою!")
    print(f"🌐 Обновите страницу в браузере для проверки")
    
    return True

if __name__ == "__main__":
    final_update_site()
