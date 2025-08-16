#!/usr/bin/env python3
"""
Создание статического сайта из Google Sheets
Google Sheets используется только для управления, сайт работает статически
"""

import os
import json
import shutil
import zipfile
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

class StaticSiteCreator:
    def __init__(self):
        self.sheets_id = "1FLlyjpSd9EBOxZC8f0B6-iKRpKCMxcTRqWOHlgUpFoQ"
        
    def load_products_from_sheets(self):
        """Загрузка данных из Google Sheets"""
        try:
            # Настройка Google Sheets API с OAuth2
            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            
            # Пробуем разные способы аутентификации
            try:
                creds = ServiceAccountCredentials.from_json_keyfile_name('google_api_config.json', scope)
                client = gspread.authorize(creds)
            except Exception as e:
                print(f"⚠️ Ошибка с ServiceAccountCredentials: {e}")
                # Пробуем с токеном OAuth2
                import pickle
                with open('token.pickle', 'rb') as token:
                    creds = pickle.load(token)
                client = gspread.authorize(creds)
            
            # Открываем таблицу
            sheet = client.open_by_key(self.sheets_id).sheet1
            data = sheet.get_all_records()
            
            # Преобразуем данные в нужный формат
            products = []
            for row in data:
                # Пропускаем строки без ID
                if not row.get('ID'):
                    continue
                    
                # Преобразуем изображения из строки в массив
                images_str = row.get('Images', '')
                if images_str:
                    images = [img.strip() for img in images_str.split('|') if img.strip()]
                else:
                    images = []
                
                # Создаем объект товара
                product = {
                    "id": str(row.get('ID', '')),
                    "order": str(row.get('Order', '')),
                    "section": row.get('Section', 'home'),
                    "title": row.get('Title', ''),
                    "price": row.get('Price', ''),
                    "desc": row.get('Desc', ''),
                    "meta": row.get('Meta', ''),
                    "status": row.get('Status', 'preorder'),
                    "images": images,
                    "link": row.get('Link', 'https://t.me/stub123')
                }
                
                products.append(product)
            
            # Сортируем по порядку
            products.sort(key=lambda x: int(x.get('order', 0)))
            
            print(f"✅ Загружено {len(products)} товаров из Google Sheets")
            return products
            
        except Exception as e:
            print(f"❌ Ошибка загрузки из Google Sheets: {e}")
            return []
    
    def create_static_site(self, products):
        """Создание статического сайта"""
        try:
            # Читаем оригинальный файл app.min.js
            original_file = 'web/app.min.js'
            if not os.path.exists(original_file):
                print(f"❌ Файл {original_file} не найден")
                return False
            
            with open(original_file, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Находим начало данных
            data_start = original_content.find('const items = [')
            if data_start == -1:
                print("❌ Не найдена секция с данными в app.min.js")
                return False
            
            # Находим конец массива items
            brace_count = 0
            in_items = False
            data_end = data_start
            for i, char in enumerate(original_content[data_start:], data_start):
                if char == '[':
                    brace_count += 1
                    in_items = True
                elif char == ']':
                    brace_count -= 1
                    if in_items and brace_count == 0:
                        data_end = i + 1
                        break
            
            # Создаем новые данные
            new_data = f"""const items = {json.dumps(products, ensure_ascii=False, indent=2)};"""
            
            # Заменяем данные в файле
            new_content = original_content[:data_start] + new_data + original_content[data_end:]
            
            # Сохраняем обновленный файл
            with open('web/app.min.js', 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            # Создаем файл с информацией об обновлении
            update_info = {
                'timestamp': datetime.now().isoformat(),
                'products_count': len(products),
                'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'sections': list(set(p.get('section', '') for p in products)),
                'note': 'Сайт создан из Google Sheets, работает статически'
            }
            
            with open('web/site_info.json', 'w', encoding='utf-8') as f:
                json.dump(update_info, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Статический сайт создан: {len(products)} товаров")
            print(f"📝 Файл app.min.js обновлен")
            print(f"📊 Разделы: {', '.join(update_info['sections'])}")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка создания статического сайта: {e}")
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
            zip_filename = f'platforma_static_deploy_{timestamp}.zip'
            with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(deploy_folder):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, deploy_folder)
                        zipf.write(file_path, arcname)
            
            # Очищаем временную папку
            shutil.rmtree(deploy_folder)
            
            print(f'✅ Создан статический деплой: {zip_filename}')
            return zip_filename
            
        except Exception as e:
            print(f"❌ Ошибка создания деплоя: {e}")
            return None
    
    def run_creation(self):
        """Запуск создания статического сайта"""
        print("🚀 Создание статического сайта из Google Sheets...")
        print("📋 Google Sheets используется только для управления")
        print("🌐 Сайт будет работать статически без связи с Google Sheets")
        
        # Загружаем данные из Google Sheets
        products = self.load_products_from_sheets()
        
        if not products:
            print("❌ Не удалось загрузить данные из Google Sheets")
            return False
        
        # Создаем статический сайт
        success = self.create_static_site(products)
        
        if success:
            # Создаем деплой
            deploy_file = self.create_deploy()
            
            print("\n🎉 Статический сайт создан успешно!")
            print("📊 Статистика:")
            print(f"   - Товаров: {len(products)}")
            print(f"   - Разделов: {len(set(p.get('section', '') for p in products))}")
            if deploy_file:
                print(f"   - Деплой: {deploy_file}")
            print("\n💡 Как использовать:")
            print("   1. Управляйте товарами в Google Sheets")
            print("   2. Запускайте этот скрипт для обновления сайта")
            print("   3. Загружайте деплой на хостинг")
            print("   4. Сайт работает статически без связи с Google Sheets")
        else:
            print("❌ Ошибка создания статического сайта")
        
        return success

def main():
    """Главная функция"""
    creator = StaticSiteCreator()
    creator.run_creation()

if __name__ == "__main__":
    main()
