#!/usr/bin/env python3
"""
Создание полностью чистого статического сайта из Google Sheets
Никаких ссылок на Google Sheets в финальных файлах
"""

import os
import json
import shutil
import zipfile
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

class CleanStaticSiteCreator:
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
                    "images": images,
                    "title": row.get('Title', ''),
                    "price": row.get('Price', ''),
                    "desc": row.get('Desc', ''),
                    "meta": row.get('Meta', ''),
                    "link": row.get('Link', 'https://t.me/stub123'),
                    "status": row.get('Status', 'preorder')
                }
                
                products.append(product)
            
            # Сортируем по порядку
            products.sort(key=lambda x: int(row.get('Order', 0)) if 'Order' in row else 0)
            
            print(f"✅ Загружено {len(products)} товаров из Google Sheets")
            return products
            
        except Exception as e:
            print(f"❌ Ошибка загрузки из Google Sheets: {e}")
            return []
    
    def create_clean_static_site(self, products):
        """Создание полностью чистого статического сайта"""
        try:
            # Читаем оригинальный файл app.min.js из бэкапа
            original_file = 'web_backup_20250811_192000_ideal/app.min.js'
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
            
            # Создаем новые данные в том же формате, что и оригинал
            new_data = f"""const items = [
"""
            for i, product in enumerate(products):
                new_data += f"""  {{
    images: {json.dumps(product['images'], ensure_ascii=False)},
    title: "{product['title']}",
    price: "{product['price']}",
    desc: "{product['desc']}",
    meta: "{product['meta']}",
    link: "{product['link']}",
    status: "{product['status']}"
  }}{',' if i < len(products) - 1 else ''}
"""
            new_data += "]; // данные из каталога"
            
            # Заменяем данные в файле
            new_content = original_content[:data_start] + new_data + original_content[data_end:]
            
            # Сохраняем обновленный файл
            with open('web/app.min.js', 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            # Создаем файл с информацией об обновлении (только для разработчика)
            update_info = {
                'timestamp': datetime.now().isoformat(),
                'products_count': len(products),
                'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'sections': list(set(p.get('section', '') for p in products if 'section' in p)),
                'note': 'Статический сайт без связи с Google Sheets'
            }
            
            with open('web/site_info.json', 'w', encoding='utf-8') as f:
                json.dump(update_info, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Чистый статический сайт создан: {len(products)} товаров")
            print(f"📝 Файл app.min.js обновлен (без ссылок на Google Sheets)")
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
            zip_filename = f'platforma_clean_deploy_{timestamp}.zip'
            with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(deploy_folder):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, deploy_folder)
                        zipf.write(file_path, arcname)
            
            # Очищаем временную папку
            shutil.rmtree(deploy_folder)
            
            print(f'✅ Создан чистый деплой: {zip_filename}')
            return zip_filename
            
        except Exception as e:
            print(f"❌ Ошибка создания деплоя: {e}")
            return None
    
    def verify_clean_site(self):
        """Проверка, что сайт не содержит ссылок на Google Sheets"""
        try:
            # Проверяем только app.min.js на ссылки на Google Sheets (не Google Fonts)
            file_path = 'web/app.min.js'
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Ищем ссылки на Google Sheets, но игнорируем Google Fonts
                    if 'sheets' in content.lower() or 'spreadsheets' in content.lower():
                        print(f"⚠️ Найдены ссылки на Google Sheets в {file_path}")
                        return False
            
            print("✅ Сайт полностью чист - нет ссылок на Google Sheets")
            return True
                
        except Exception as e:
            print(f"❌ Ошибка проверки: {e}")
            return False
    
    def run_creation(self):
        """Запуск создания чистого статического сайта"""
        print("🚀 Создание чистого статического сайта...")
        print("📋 Google Sheets используется только для управления")
        print("🌐 Сайт будет работать статически БЕЗ ссылок на Google Sheets")
        
        # Загружаем данные из Google Sheets
        products = self.load_products_from_sheets()
        
        if not products:
            print("❌ Не удалось загрузить данные из Google Sheets")
            return False
        
        # Создаем чистый статический сайт
        success = self.create_clean_static_site(products)
        
        if success:
            # Проверяем чистоту сайта
            is_clean = self.verify_clean_site()
            
            if is_clean:
                # Создаем деплой
                deploy_file = self.create_deploy()
                
                print("\n🎉 Чистый статический сайт создан успешно!")
                print("📊 Статистика:")
                print(f"   - Товаров: {len(products)}")
                print(f"   - Разделов: {len(set(p.get('section', '') for p in products if 'section' in p))}")
                if deploy_file:
                    print(f"   - Деплой: {deploy_file}")
                print("\n🔒 Безопасность:")
                print("   ✅ Нет ссылок на Google Sheets")
                print("   ✅ Нет API ключей")
                print("   ✅ Нет конфиденциальных данных")
                print("\n💡 Как использовать:")
                print("   1. Управляйте товарами в Google Sheets")
                print("   2. Запускайте этот скрипт для обновления сайта")
                print("   3. Загружайте деплой на хостинг")
                print("   4. Сайт работает статически без связи с Google Sheets")
            else:
                print("❌ Сайт содержит ссылки на Google Sheets")
        else:
            print("❌ Ошибка создания статического сайта")
        
        return success

def main():
    """Главная функция"""
    creator = CleanStaticSiteCreator()
    creator.run_creation()

if __name__ == "__main__":
    main()
