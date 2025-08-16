#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Обновление данных на сайте из Google Sheets
"""

import os
import json
import shutil
from datetime import datetime

def load_products_from_sheets():
    """Загрузка данных из Google Sheets"""
    try:
        from auto_update_oauth2 import full_sync_oauth2
        print("📥 Синхронизация с Google Sheets...")
        full_sync_oauth2()
        
        if os.path.exists('products.json'):
            with open('products.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print("❌ Файл products.json не найден после синхронизации")
            return []
            
    except Exception as e:
        print(f"❌ Ошибка загрузки из Sheets: {e}")
        return []

def convert_to_website_format(products):
    """Конвертация данных в формат для сайта"""
    website_items = []
    
    for product in products:
        # Получаем изображения
        images = []
        if product.get('images'):
            # Обрабатываем изображения - они могут быть строкой с разделителями
            images_str = product['images']
            if isinstance(images_str, str):
                # Разбиваем по запятой, а затем по вертикальной черте
                image_parts = images_str.split(',')
                for part in image_parts:
                    part = part.strip()
                    if '|' in part:
                        # Если есть вертикальная черта, разбиваем по ней
                        sub_images = part.split('|')
                        for img in sub_images:
                            img = img.strip()
                            if img:
                                images.append(img)
                    else:
                        # Если нет вертикальной черты, добавляем как есть
                        if part:
                            images.append(part)
            elif isinstance(images_str, list):
                # Если это уже список
                images = images_str
        
        # Создаем объект товара для сайта
        item = {
            'images': images,  # Теперь это массив
            'title': product.get('title', ''),
            'price': product.get('price', ''),
            'desc': product.get('desc', ''),
            'meta': product.get('meta', ''),
            'link': product.get('link', 'https://t.me/stub123'),
            'status': product.get('status', 'stock'),
            'order': int(product.get('order', 0)),
            'section': product.get('section', 'home')
        }
        
        website_items.append(item)
    
    # Сортируем по порядку
    website_items.sort(key=lambda x: x['order'])
    
    return website_items

def update_website_files(products):
    """Обновление файлов сайта"""
    try:
        # Конвертируем данные
        website_items = convert_to_website_format(products)
        
        print(f"📦 Подготовлено {len(website_items)} товаров для сайта")
        
        # Создаем JavaScript код с данными
        js_code = f"""const DEFAULT_TG = 'https://t.me/stub123';
/* ===== DATA (главная) ===== */
const items = {json.dumps(website_items, ensure_ascii=False, indent=2)};
"""
        
        # Читаем остальную часть файла app.min.js
        if os.path.exists('web/app.min.js'):
            with open('web/app.min.js', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Находим начало данных и конец
            start_marker = "/* ===== DATA (главная) ===== */"
            end_marker = "/* ===== DATA (конец) ===== */"
            
            if start_marker in content:
                start_pos = content.find(start_marker)
                if end_marker in content:
                    end_pos = content.find(end_marker) + len(end_marker)
                    # Заменяем секцию данных
                    new_content = content[:start_pos] + js_code + content[end_pos:]
                else:
                    # Если нет маркера конца, ищем конец массива items
                    items_start = content.find("const items = [")
                    if items_start != -1:
                        # Ищем закрывающую скобку массива
                        brace_count = 0
                        end_pos = items_start
                        for i, char in enumerate(content[items_start:], items_start):
                            if char == '[':
                                brace_count += 1
                            elif char == ']':
                                brace_count -= 1
                                if brace_count == 0:
                                    end_pos = i + 1
                                    break
                        
                        # Ищем точку с запятой после массива
                        semicolon_pos = content.find(';', end_pos)
                        if semicolon_pos != -1:
                            end_pos = semicolon_pos + 1
                        
                        new_content = content[:items_start] + js_code + content[end_pos:]
                    else:
                        print("❌ Не удалось найти секцию данных в app.min.js")
                        return False
            else:
                print("❌ Не найден маркер данных в app.min.js")
                return False
            
            # Создаем резервную копию
            backup_name = f"web/app.min.js.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2('web/app.min.js', backup_name)
            print(f"💾 Создана резервная копия: {backup_name}")
            
            # Записываем обновленный файл
            with open('web/app.min.js', 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("✅ Файл app.min.js обновлен")
            return True
            
        else:
            print("❌ Файл web/app.min.js не найден")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка обновления файлов сайта: {e}")
        return False

def main():
    """Основная функция"""
    print("🌐 Обновление данных на сайте")
    print("=" * 40)
    
    # Загружаем данные из Google Sheets
    products = load_products_from_sheets()
    
    if not products:
        print("❌ Не удалось загрузить данные")
        return
    
    print(f"📊 Загружено {len(products)} товаров")
    
    # Показываем порядок товаров
    print("\n📋 Порядок товаров:")
    for product in sorted(products, key=lambda x: int(x.get('order', 0))):
        print(f"  {product.get('order', 'N/A')}. {product.get('title', 'N/A')} (ID: {product.get('id', 'N/A')})")
    
    # Обновляем файлы сайта
    if update_website_files(products):
        print("\n✅ Данные на сайте обновлены!")
        print("🔄 Обновите страницу в браузере для просмотра изменений")
    else:
        print("\n❌ Ошибка обновления данных на сайте")

if __name__ == "__main__":
    main()
