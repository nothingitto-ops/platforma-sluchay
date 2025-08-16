#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime
import requests

class GoogleSheetsAPI:
    def __init__(self):
        # ID вашей Google таблицы (из URL)
        self.spreadsheet_id = "1RGdW7QcHV6BgZHJnSMzXKkmsXDYZulMojN312tgvI6PK86H8dRjReYUOHI2l_aVYzLg2NIjAcir89g"
        self.api_key = None
        self.access_token = None
        
    def setup_api_key(self):
        """Настройка API ключа"""
        print("🔑 НАСТРОЙКА GOOGLE SHEETS API")
        print("=" * 50)
        print("1. Перейдите в Google Cloud Console:")
        print("   https://console.cloud.google.com/")
        print()
        print("2. Создайте новый проект или выберите существующий")
        print()
        print("3. Включите Google Sheets API:")
        print("   - Перейдите в 'APIs & Services' > 'Library'")
        print("   - Найдите 'Google Sheets API' и включите его")
        print()
        print("4. Создайте учетные данные:")
        print("   - Перейдите в 'APIs & Services' > 'Credentials'")
        print("   - Нажмите 'Create Credentials' > 'API Key'")
        print("   - Скопируйте API ключ")
        print()
        
        api_key = input("Введите ваш API ключ: ").strip()
        if api_key:
            self.api_key = api_key
            self.save_config()
            print("✅ API ключ сохранен!")
            return True
        return False
    
    def setup_oauth(self):
        """Настройка OAuth 2.0 для полного доступа"""
        print("🔐 НАСТРОЙКА OAUTH 2.0")
        print("=" * 50)
        print("Для полного доступа к таблице нужно настроить OAuth 2.0:")
        print()
        print("1. В Google Cloud Console создайте OAuth 2.0 credentials:")
        print("   - 'APIs & Services' > 'Credentials'")
        print("   - 'Create Credentials' > 'OAuth 2.0 Client IDs'")
        print("   - Выберите 'Desktop application'")
        print()
        print("2. Скачайте JSON файл с credentials")
        print("3. Переименуйте его в 'credentials.json' и поместите в папку проекта")
        print()
        
        if os.path.exists('credentials.json'):
            print("✅ Файл credentials.json найден!")
            return True
        else:
            print("❌ Файл credentials.json не найден")
            return False
    
    def save_config(self):
        """Сохранение конфигурации"""
        config = {
            'api_key': self.api_key,
            'spreadsheet_id': self.spreadsheet_id
        }
        with open('google_sheets_config.json', 'w') as f:
            json.dump(config, f)
    
    def load_config(self):
        """Загрузка конфигурации"""
        try:
            with open('google_sheets_config.json', 'r') as f:
                config = json.load(f)
                self.api_key = config.get('api_key')
                self.spreadsheet_id = config.get('spreadsheet_id')
                return True
        except:
            return False
    
    def update_sheets_simple(self):
        """Простое обновление через публичный доступ"""
        try:
            # Загружаем наши товары
            with open('products.json', 'r', encoding='utf-8') as f:
                products = json.load(f)
            
            # Создаем TSV данные
            tsv_lines = ["Section\tTitle\tPrice\tDesc\tMeta\tStatus\tImages\tLink"]
            
            for product in products:
                tsv_line = f"home\t{product['title']}\t{product.get('price', '')}\t{product.get('desc', '')}\t{product.get('meta', '')}\t{product.get('status', '')}\t{product['images']}\thttps://t.me/stub123"
                tsv_lines.append(tsv_line)
            
            tsv_content = "\n".join(tsv_lines)
            
            # Сохраняем файл
            filename = f"sheets-update-{datetime.now().strftime('%Y%m%d-%H%M%S')}.tsv"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(tsv_content)
            
            print(f"✅ Файл создан: {filename}")
            print(f"📊 Товаров: {len(products)}")
            print()
            print("📋 Для автоматического обновления:")
            print("1. Откройте Google Sheets")
            print("2. Выделите все данные (Ctrl+A)")
            print("3. Удалите (Delete)")
            print("4. Скопируйте содержимое файла выше")
            print("5. Вставьте в Google Sheets (Ctrl+V)")
            print("6. Сохраните (Ctrl+S)")
            
            return filename
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return None
    
    def update_sheets_api(self):
        """Обновление через Google Sheets API"""
        if not self.api_key:
            print("❌ API ключ не настроен")
            return False
        
        try:
            # Загружаем наши товары
            with open('products.json', 'r', encoding='utf-8') as f:
                products = json.load(f)
            
            # Подготавливаем данные
            values = [["Section", "Title", "Price", "Desc", "Meta", "Status", "Images", "Link"]]
            
            for product in products:
                row = [
                    "home",
                    product['title'],
                    product.get('price', ''),
                    product.get('desc', ''),
                    product.get('meta', ''),
                    product.get('status', ''),
                    product['images'],
                    "https://t.me/stub123"
                ]
                values.append(row)
            
            # URL для обновления
            url = f"https://sheets.googleapis.com/v4/spreadsheets/{self.spreadsheet_id}/values/A1:Z1000?valueInputOption=RAW&key={self.api_key}"
            
            # Данные для отправки
            data = {
                "values": values
            }
            
            # Отправляем запрос
            response = requests.put(url, json=data)
            
            if response.status_code == 200:
                print("✅ Google Sheets обновлен успешно!")
                print(f"📊 Обновлено товаров: {len(products)}")
                return True
            else:
                print(f"❌ Ошибка обновления: {response.status_code}")
                print(f"Ответ: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return False

    async def update_product_order(self, product_id: str, new_order: int):
        """Обновить порядок товара в Google Sheets"""
        try:
            if not self.api_key:
                print(f"❌ API ключ не настроен для обновления порядка товара {product_id}")
                return False
            
            # Загружаем текущие данные из Sheets
            url = f"https://sheets.googleapis.com/v4/spreadsheets/{self.spreadsheet_id}/values/A1:Z1000?key={self.api_key}"
            response = requests.get(url)
            
            if response.status_code != 200:
                print(f"❌ Ошибка получения данных из Sheets: {response.status_code}")
                return False
            
            data = response.json()
            values = data.get('values', [])
            
            if not values:
                print("❌ Данные в таблице не найдены")
                return False
            
            # Ищем строку с товаром по ID
            target_row = None
            for i, row in enumerate(values):
                if len(row) > 0 and str(product_id) in str(row):
                    target_row = i
                    break
            
            if target_row is None:
                print(f"❌ Товар с ID {product_id} не найден в таблице")
                return False
            
            # Обновляем порядок в найденной строке
            # Предполагаем, что порядок находится в определенной колонке
            # Нужно добавить колонку order если её нет
            if len(values[target_row]) < 9:  # Если нет колонки order
                values[target_row].append(str(new_order))
            else:
                values[target_row][8] = str(new_order)  # Колонка I (индекс 8)
            
            # Отправляем обновленные данные
            update_url = f"https://sheets.googleapis.com/v4/spreadsheets/{self.spreadsheet_id}/values/A1:Z1000?valueInputOption=RAW&key={self.api_key}"
            update_data = {"values": values}
            
            update_response = requests.put(update_url, json=update_data)
            
            if update_response.status_code == 200:
                print(f"✅ Порядок товара {product_id} обновлен в Sheets: {new_order}")
                return True
            else:
                print(f"❌ Ошибка обновления порядка: {update_response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка обновления порядка товара {product_id}: {e}")
            return False

    async def add_product_row(self, row_data: list):
        """Добавить новую строку с товаром в Google Sheets"""
        try:
            if not self.api_key:
                print(f"❌ API ключ не настроен для добавления товара")
                return False
            
            # Добавляем новую строку в конец таблицы
            url = f"https://sheets.googleapis.com/v4/spreadsheets/{self.spreadsheet_id}/values/A:Z:append?valueInputOption=RAW&key={self.api_key}"
            
            data = {
                "values": [row_data]
            }
            
            response = requests.post(url, json=data)
            
            if response.status_code == 200:
                print(f"✅ Товар добавлен в Google Sheets")
                return True
            else:
                print(f"❌ Ошибка добавления товара: {response.status_code}")
                print(f"Ответ: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка добавления товара: {e}")
            return False

def main():
    api = GoogleSheetsAPI()
    
    # Пытаемся загрузить конфигурацию
    if not api.load_config():
        print("🔧 Первый запуск - настройка API")
        if not api.setup_api_key():
            print("❌ Настройка не завершена")
            return
    
    print("📊 ОБНОВЛЕНИЕ GOOGLE SHEETS")
    print("=" * 30)
    
    # Пробуем обновить через API
    if api.api_key:
        print("🔄 Попытка обновления через API...")
        if api.update_sheets_api():
            return
    
    # Если API не работает, создаем файл
    print("📁 Создание файла для ручного обновления...")
    api.update_sheets_simple()

if __name__ == "__main__":
    main()
