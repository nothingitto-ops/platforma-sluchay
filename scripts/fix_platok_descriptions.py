#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import re
from datetime import datetime

def fix_platok_descriptions():
    """Меняем описания платков местами"""
    
    print("🔄 Меняем описания платков местами...")
    
    # Загружаем текущий app.min.js
    try:
        with open('../web/app.min.js', 'r', encoding='utf-8') as f:
            current_js = f.read()
    except Exception as e:
        print(f"❌ Ошибка чтения app.min.js: {e}")
        return False
    
    # Находим массив items
    pattern = r'const items = \[(.*?)\];'
    match = re.search(pattern, current_js, re.DOTALL)
    
    if not match:
        print("❌ Не найден массив items в app.min.js")
        return False
    
    items_text = match.group(1)
    
    # Парсим JSON
    try:
        items = json.loads(f'[{items_text}]')
    except Exception as e:
        print(f"❌ Ошибка парсинга JSON: {e}")
        return False
    
    # Находим платки и меняем описания местами
    platok_9 = None
    platok_12 = None
    
    for item in items:
        if item.get('title') == 'Платок на шею':
            if item.get('order') == 9:
                platok_9 = item
            elif item.get('order') == 12:
                platok_12 = item
    
    if platok_9 and platok_12:
        print(f"📝 Найдены платки:")
        print(f"   • Платок 9: {platok_9['desc']}")
        print(f"   • Платок 12: {platok_12['desc']}")
        
        # Меняем описания местами
        temp_desc = platok_9['desc']
        platok_9['desc'] = platok_12['desc']
        platok_12['desc'] = temp_desc
        
        print(f"🔄 Описания поменяны местами:")
        print(f"   • Платок 9: {platok_9['desc']}")
        print(f"   • Платок 12: {platok_12['desc']}")
    else:
        print("❌ Не найдены оба платка")
        return False
    
    # Создаем новый JSON
    items_json = json.dumps(items, ensure_ascii=False, indent=2)
    
    # Заменяем массив items в JavaScript коде
    replacement = f'const items = {items_json};'
    new_js = re.sub(pattern, replacement, current_js, flags=re.DOTALL)
    
    # Добавляем комментарий с временем обновления
    update_comment = f'// Обновлено из Google Sheets: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n'
    
    if not new_js.startswith('// Обновлено из Google Sheets'):
        new_js = update_comment + new_js
    
    # Сохраняем обновленный app.min.js
    try:
        with open('../web/app.min.js', 'w', encoding='utf-8') as f:
            f.write(new_js)
        print(f"✅ Файл app.min.js обновлен")
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
    
    print(f"\n🎉 Описания платков поменяны местами!")
    print(f"📊 Статистика:")
    print(f"   - Время обновления: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Показываем изменения платков
    print(f"\n🧣 Изменения платков:")
    print(f"   • Платок на шею (product_9): {platok_9['desc']}")
    print(f"   • Платок на шею (product_12): {platok_12['desc']}")
    
    print(f"\n✅ Сайт готов к деплою!")
    print(f"🌐 Обновите страницу в браузере для проверки")
    
    return True

if __name__ == "__main__":
    fix_platok_descriptions()
