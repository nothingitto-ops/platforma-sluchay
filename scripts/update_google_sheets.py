#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime

def create_google_sheets_update():
    """Создание инструкций для обновления Google Sheets"""
    
    # Загружаем наши товары
    try:
        with open('products.json', 'r', encoding='utf-8') as f:
            products = json.load(f)
    except Exception as e:
        print(f"❌ Ошибка загрузки товаров: {e}")
        return
    
    # Создаем TSV данные
    tsv_lines = ["Section\tTitle\tPrice\tDesc\tMeta\tStatus\tImages\tLink"]
    
    for product in products:
        tsv_line = f"home\t{product['title']}\t{product.get('price', '')}\t{product.get('desc', '')}\t{product.get('meta', '')}\t{product.get('status', '')}\t{product['images']}\thttps://t.me/stub123"
        tsv_lines.append(tsv_line)
    
    tsv_content = "\n".join(tsv_lines)
    
    # Сохраняем файл
    filename = f"google-sheets-update-{datetime.now().strftime('%Y%m%d-%H%M%S')}.tsv"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(tsv_content)
    
    # Создаем инструкции
    instructions = f"""📊 ОБНОВЛЕНИЕ GOOGLE SHEETS

✅ Файл с данными создан: {filename}

📋 ИНСТРУКЦИИ ДЛЯ ОБНОВЛЕНИЯ:

1. Откройте Google Sheets: https://docs.google.com/spreadsheets/d/e/2PACX-1vRGdW7QcHV6BgZHJnSMzXKkmsXDYZulMojN312tgvI6PK86H8dRjReYUOHI2l_aVYzLg2NIjAcir89g/pub?output=tsv

2. Выделите все данные в таблице (Ctrl+A)

3. Удалите старые данные (Delete)

4. Скопируйте содержимое файла {filename}

5. Вставьте в Google Sheets (Ctrl+V)

6. Сохраните изменения (Ctrl+S)

📊 СТАТИСТИКА:
- Товаров для обновления: {len(products)}
- Файл: {filename}
- Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}

💡 АВТОМАТИЧЕСКОЕ ОБНОВЛЕНИЕ:
Для автоматического обновления через API потребуется:
- Настройка Google Sheets API
- Создание сервисного аккаунта
- Получение ключей доступа

Пока используйте ручное обновление через файл.
"""
    
    # Сохраняем инструкции
    instructions_file = f"instructions-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"
    with open(instructions_file, 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print(f"✅ Файл для Google Sheets создан: {filename}")
    print(f"📋 Инструкции сохранены: {instructions_file}")
    print(f"📊 Товаров для обновления: {len(products)}")
    
    return filename, tsv_content

if __name__ == "__main__":
    create_google_sheets_update()
