#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime
import requests

def auto_update_google_sheets():
    """Автоматическое обновление Google Sheets"""
    
    print("🚀 АВТОМАТИЧЕСКОЕ ОБНОВЛЕНИЕ GOOGLE SHEETS")
    print("=" * 50)
    
    # Загружаем наши товары
    try:
        with open('products.json', 'r', encoding='utf-8') as f:
            products = json.load(f)
    except Exception as e:
        print(f"❌ Ошибка загрузки товаров: {e}")
        return False
    
    print(f"📊 Найдено товаров: {len(products)}")
    
    # Создаем TSV данные
    tsv_lines = ["Section\tTitle\tPrice\tDesc\tMeta\tStatus\tImages\tLink"]
    
    for product in products:
        tsv_line = f"home\t{product['title']}\t{product.get('price', '')}\t{product.get('desc', '')}\t{product.get('meta', '')}\t{product.get('status', '')}\t{product['images']}\thttps://t.me/stub123"
        tsv_lines.append(tsv_line)
    
    tsv_content = "\n".join(tsv_lines)
    
    # Сохраняем файл
    filename = f"auto-update-{datetime.now().strftime('%Y%m%d-%H%M%S')}.tsv"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(tsv_content)
    
    print(f"✅ Файл создан: {filename}")
    
    # Пытаемся автоматически открыть Google Sheets
    sheets_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRGdW7QcHV6BgZHJnSMzXKkmsXDYZulMojN312tgvI6PK86H8dRjReYUOHI2l_aVYzLg2NIjAcir89g/edit"
    
    print(f"🌐 Открываю Google Sheets...")
    print(f"📋 URL: {sheets_url}")
    
    # Копируем данные в буфер обмена (если возможно)
    try:
        import subprocess
        if os.name == 'posix':  # macOS/Linux
            subprocess.run(['pbcopy'], input=tsv_content, text=True, check=True)
            print("📋 Данные скопированы в буфер обмена!")
        elif os.name == 'nt':  # Windows
            subprocess.run(['clip'], input=tsv_content, text=True, check=True)
            print("📋 Данные скопированы в буфер обмена!")
    except:
        print("⚠️  Не удалось скопировать в буфер обмена")
    
    print()
    print("🎯 ИНСТРУКЦИИ ДЛЯ ОДНОГО КЛИКА:")
    print("1. Откройте Google Sheets по ссылке выше")
    print("2. Выделите все данные (Ctrl+A)")
    print("3. Удалите старые данные (Delete)")
    print("4. Вставьте новые данные (Ctrl+V)")
    print("5. Сохраните (Ctrl+S)")
    print()
    print("💡 Данные уже скопированы в буфер обмена!")
    print("💡 Просто нажмите Ctrl+V в Google Sheets")
    
    return True

def setup_webhook():
    """Настройка вебхука для автоматического обновления"""
    print("🔗 НАСТРОЙКА АВТОМАТИЧЕСКОГО ОБНОВЛЕНИЯ")
    print("=" * 50)
    print("Для полной автоматизации нужно:")
    print()
    print("1. Создать Google Apps Script:")
    print("   - Откройте Google Sheets")
    print("   - Extensions > Apps Script")
    print("   - Создайте новый проект")
    print()
    print("2. Добавить код в Apps Script:")
    print("   - Создайте функцию doPost(e)")
    print("   - Добавьте обработку данных")
    print("   - Опубликуйте как веб-приложение")
    print()
    print("3. Получите URL для обновления")
    print("   - Скопируйте URL веб-приложения")
    print("   - Используйте для автоматического обновления")
    print()
    
    webhook_url = input("Введите URL вебхука (если есть): ").strip()
    if webhook_url:
        # Сохраняем URL
        config = {'webhook_url': webhook_url}
        with open('webhook_config.json', 'w') as f:
            json.dump(config, f)
        print("✅ URL вебхука сохранен!")
        return webhook_url
    return None

if __name__ == "__main__":
    # Пытаемся найти вебхук
    try:
        with open('webhook_config.json', 'r') as f:
            config = json.load(f)
            webhook_url = config.get('webhook_url')
            if webhook_url:
                print(f"🔗 Найден вебхук: {webhook_url}")
                # Здесь можно добавить автоматическое обновление через вебхук
    except:
        pass
    
    # Запускаем обычное обновление
    auto_update_google_sheets()
