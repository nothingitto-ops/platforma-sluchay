#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import gspread
from google.oauth2.credentials import Credentials
from datetime import datetime

def sync_from_sheets():
    """Синхронизация данных из Google Sheets"""
    try:
        print("📥 Загрузка данных из Google Sheets...")
        
        # Загружаем конфигурацию
        with open('google_api_config.json', 'r') as f:
            config = json.load(f)
            spreadsheet_id = config.get('spreadsheet_id')
        
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        creds = Credentials.from_authorized_user_file('token.json', scopes=SCOPES)
        client = gspread.authorize(creds)
        
        spreadsheet = client.open_by_key(spreadsheet_id)
        worksheet = spreadsheet.sheet1
        all_values = worksheet.get_all_values()
        
        if not all_values:
            print("❌ Таблица пуста!")
            return False
        
        headers = all_values[0]
        data = all_values[1:]
        
        print(f"📊 Найдено строк данных: {len(data)}")
        
        products = []
        for i, row in enumerate(data, 1):
            if not row or len(row) < 4:
                continue
            
            try:
                product_id = row[0] if len(row) > 0 else ""
                order = row[1] if len(row) > 1 else ""
                section = row[2] if len(row) > 2 else ""
                title = row[3] if len(row) > 3 else ""
                price = row[4] if len(row) > 4 else ""
                desc = row[5] if len(row) > 5 else ""
                meta = row[6] if len(row) > 6 else ""
                status = row[7] if len(row) > 7 else ""
                images = row[8] if len(row) > 8 else ""
                link = row[9] if len(row) > 9 else ""
                
                if not title:
                    continue
                
                product = {
                    'id': product_id,
                    'order': order,
                    'section': section,
                    'title': title,
                    'price': price,
                    'desc': desc,
                    'meta': meta,
                    'status': status,
                    'images': images,
                    'link': link,
                    'updated': datetime.now().isoformat()
                }
                
                products.append(product)
                print(f"✅ Загружен: {title} - {price}")
                
            except Exception as e:
                print(f"❌ Ошибка строки {i}: {e}")
                continue
        
        # Сохраняем в products.json
        with open('products.json', 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        
        # Сохраняем в web/products.json
        with open('web/products.json', 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Синхронизация завершена! Сохранено {len(products)} товаров")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка синхронизации: {e}")
        return False

def update_app_js():
    """Обновление app.min.js с новыми данными"""
    try:
        print("📝 Обновление app.min.js...")
        
        # Загружаем данные
        with open('products.json', 'r', encoding='utf-8') as f:
            products = json.load(f)
        
        # Читаем текущий app.min.js
        with open('web/app.min.js', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Находим начало данных
        start_marker = 'const items = ['
        end_marker = '];'
        
        start_pos = content.find(start_marker)
        if start_pos == -1:
            print("❌ Не найден маркер начала данных")
            return False
        
        end_pos = content.find(end_marker, start_pos)
        if end_pos == -1:
            print("❌ Не найден маркер конца данных")
            return False
        
        # Формируем новые данные
        items_data = []
        for product in products:
            # Преобразуем изображения в массив
            images = product.get('images', '').split(',') if product.get('images') else []
            images = [img.strip() for img in images if img.strip()]
            
            item = {
                "images": images,
                "title": product.get('title', ''),
                "price": product.get('price', ''),
                "desc": product.get('desc', ''),
                "meta": product.get('meta', ''),
                "link": product.get('link', ''),
                "status": product.get('status', ''),
                "order": int(product.get('order', 0)),
                "section": product.get('section', 'home')
            }
            items_data.append(item)
        
        # Создаем новое содержимое
        new_items_json = json.dumps(items_data, ensure_ascii=False, indent=2)
        
        # Обновляем файл
        new_content = content[:start_pos + len(start_marker)] + '\n' + new_items_json + '\n' + content[end_pos:]
        
        # Добавляем комментарий с датой обновления
        update_comment = f"// Обновлено из products.json: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        new_content = update_comment + new_content
        
        # Сохраняем
        with open('web/app.min.js', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ app.min.js обновлен")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка обновления app.min.js: {e}")
        return False

def main():
    print("🔄 Синхронизация и деплой")
    print("=" * 40)
    
    # Синхронизируем данные
    if not sync_from_sheets():
        print("❌ Синхронизация не удалась")
        return
    
    # Обновляем app.min.js
    if not update_app_js():
        print("❌ Обновление app.min.js не удалось")
        return
    
    print("\n✅ Все файлы обновлены!")
    print("🚀 Теперь можно деплоить на GitHub")
    
    # Запускаем деплой
    try:
        print("\n🐙 Запуск GitHub деплоя...")
        from github_deploy import GitHubDeployer
        deployer = GitHubDeployer()
        success = deployer.deploy(auto_commit=True, open_desktop=False)
        
        if success:
            print("✅ Деплой завершен успешно!")
        else:
            print("❌ Ошибка деплоя")
            
    except Exception as e:
        print(f"❌ Ошибка деплоя: {e}")

if __name__ == "__main__":
    main()
