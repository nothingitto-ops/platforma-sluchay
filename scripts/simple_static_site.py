#!/usr/bin/env python3
"""
Простая система создания статического сайта
Google Sheets → Platforma Manager → Статический сайт → Деплой
"""

import os
import json
import shutil
import zipfile
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

class SimpleStaticSite:
    def __init__(self):
        self.sheets_id = "1FLlyjpSd9EBOxZC8f0B6-iKRpKCMxcTRqWOHlgUpFoQ"
        
    def load_products_from_sheets(self):
        """Загрузка данных из Google Sheets"""
        try:
            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            
            try:
                creds = ServiceAccountCredentials.from_json_keyfile_name('google_api_config.json', scope)
                client = gspread.authorize(creds)
            except Exception as e:
                print(f"⚠️ Ошибка с ServiceAccountCredentials: {e}")
                import pickle
                with open('token.pickle', 'rb') as token:
                    creds = pickle.load(token)
                client = gspread.authorize(creds)
            
            sheet = client.open_by_key(self.sheets_id).sheet1
            data = sheet.get_all_records()
            
            products = []
            for row in data:
                if not row.get('ID'):
                    continue
                    
                images_str = row.get('Images', '')
                if images_str:
                    images = [img.strip() for img in images_str.split('|') if img.strip()]
                else:
                    images = []
                
                product = {
                    "images": images,
                    "title": row.get('Title', ''),
                    "price": row.get('Price', ''),
                    "desc": row.get('Desc', ''),
                    "meta": row.get('Meta', ''),
                    "link": row.get('Link', 'https://t.me/stub123'),
                    "status": row.get('Status', 'preorder'),
                    "order": int(row.get('Order', 0))  # Добавляем порядок
                }
                
                products.append(product)
            
            # Сортируем по порядку
            products.sort(key=lambda x: x.get('order', 0))
            
            print(f"✅ Загружено {len(products)} товаров из Google Sheets")
            print(f"📊 Порядок карточек: {[p.get('order', 0) for p in products]}")
            return products
            
        except Exception as e:
            print(f"❌ Ошибка загрузки из Google Sheets: {e}")
            return []
    
    def update_site_data(self, products):
        """Обновление данных сайта"""
        try:
            # Читаем текущий файл
            with open('web/app.min.js', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Находим и заменяем только массив items
            start_marker = 'const items = ['
            end_marker = ']; // данные из каталога'
            
            start_pos = content.find(start_marker)
            if start_pos == -1:
                print("❌ Не найдена секция с данными")
                return False
            
            # Ищем конец массива
            end_pos = content.find(end_marker, start_pos)
            if end_pos == -1:
                end_pos = content.find('];', start_pos)
                if end_pos == -1:
                    print("❌ Не найден конец массива данных")
                    return False
                end_pos += 2
            
            # Создаем новые данные
            new_items = 'const items = [\n'
            for i, product in enumerate(products):
                new_items += f"""  {{
    images: {json.dumps(product['images'], ensure_ascii=False)},
    title: "{product['title']}",
    price: "{product['price']}",
    desc: "{product['desc']}",
    meta: "{product['meta']}",
    link: "{product['link']}",
    status: "{product['status']}"
  }}{',' if i < len(products) - 1 else ''}
"""
            new_items += ']; // данные из каталога'
            
            # Заменяем данные
            new_content = content[:start_pos] + new_items + content[end_pos:]
            
            # Сохраняем файл
            with open('web/app.min.js', 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ Данные сайта обновлены: {len(products)} товаров")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка обновления данных: {e}")
            return False
    
    def create_deploy(self):
        """Создание деплоя"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        deploy_folder = f'deploy_temp_{timestamp}'
        
        try:
            os.makedirs(deploy_folder, exist_ok=True)
            
            # Копируем файлы сайта
            web_files = ['index.html', 'styles.min.css', 'app.min.js', 'mobile.overrides.css']
            for file in web_files:
                if os.path.exists(f'web/{file}'):
                    shutil.copy2(f'web/{file}', f'{deploy_folder}/{file}')
                    print(f'✅ Скопирован: {file}')
            
            # Копируем папку img
            if os.path.exists('web/img'):
                shutil.copytree('web/img', f'{deploy_folder}/img')
                print('✅ Скопирована папка: img')
            
            # Создаем ZIP
            zip_filename = f'platforma_simple_deploy_{timestamp}.zip'
            with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(deploy_folder):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, deploy_folder)
                        zipf.write(file_path, arcname)
            
            # Очищаем временную папку
            shutil.rmtree(deploy_folder)
            
            print(f'✅ Создан деплой: {zip_filename}')
            return zip_filename
            
        except Exception as e:
            print(f"❌ Ошибка создания деплоя: {e}")
            return None
    
    def run(self):
        """Запуск создания статического сайта"""
        print("🚀 Создание статического сайта...")
        print("📋 Архитектура: Google Sheets → Platforma Manager → Статический сайт")
        
        # Загружаем данные
        products = self.load_products_from_sheets()
        
        if not products:
            print("❌ Не удалось загрузить данные")
            return False
        
        # Обновляем сайт
        success = self.update_site_data(products)
        
        if success:
            # Создаем деплой
            deploy_file = self.create_deploy()
            
            print("\n🎉 Статический сайт создан!")
            print("📊 Статистика:")
            print(f"   - Товаров: {len(products)}")
            if deploy_file:
                print(f"   - Деплой: {deploy_file}")
            print("\n🔒 Безопасность:")
            print("   ✅ Google Sheets используется только для управления")
            print("   ✅ Сайт работает статически")
            print("   ✅ Деплой не содержит API ключей")
            print("\n💡 Рабочий процесс:")
            print("   1. Управляйте товарами в Google Sheets")
            print("   2. Запускайте этот скрипт")
            print("   3. Загружайте деплой на хостинг")
        else:
            print("❌ Ошибка создания сайта")
        
        return success

def main():
    """Главная функция"""
    site = SimpleStaticSite()
    site.run()

if __name__ == "__main__":
    main()
