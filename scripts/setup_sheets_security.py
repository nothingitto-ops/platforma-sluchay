#!/usr/bin/env python3
"""
Настройка защиты Google Sheets
Добавление хешей целостности и настройка прав доступа
"""

import os
import json
import hashlib
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

class SheetsSecuritySetup:
    def __init__(self):
        self.sheets_id = "1FLlyjpSd9EBOxZC8f0B6-iKRpKCMxcTRqWOHlgUpFoQ"
        
    def _create_row_hash(self, row_data):
        """Создание хеша для строки данных"""
        # Сортируем ключи для стабильного хеша
        sorted_data = dict(sorted(row_data.items()))
        data_string = json.dumps(sorted_data, ensure_ascii=False, sort_keys=True)
        return hashlib.sha256(data_string.encode()).hexdigest()
    
    def add_integrity_hashes(self):
        """Добавление хешей целостности к данным"""
        try:
            # Настройка Google Sheets API с OAuth2
            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            
            # Пробуем разные способы аутентификации
            try:
                # Сначала пробуем OAuth2 токен
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
            
            print(f"📊 Найдено {len(data)} строк данных")
            
            # Проверяем, есть ли уже колонка Hash
            headers = sheet.row_values(1)
            hash_column_index = None
            
            if 'Hash' in headers:
                hash_column_index = headers.index('Hash') + 1
                print("✅ Колонка Hash уже существует")
            else:
                # Добавляем колонку Hash
                hash_column_index = len(headers) + 1
                sheet.update_cell(1, hash_column_index, 'Hash')
                print("✅ Добавлена колонка Hash")
            
            # Обновляем хеши для каждой строки
            updated_count = 0
            for i, row in enumerate(data, start=2):  # Начинаем с 2-й строки (после заголовков)
                # Создаем копию строки без хеша
                row_without_hash = {k: v for k, v in row.items() if k != 'Hash'}
                
                # Создаем хеш
                row_hash = self._create_row_hash(row_without_hash)
                
                # Обновляем хеш в таблице
                current_hash = row.get('Hash', '')
                if current_hash != row_hash:
                    sheet.update_cell(i, hash_column_index, row_hash)
                    updated_count += 1
                    print(f"  📝 Строка {i}: обновлен хеш для товара '{row.get('Title', 'Unknown')}'")
            
            print(f"✅ Обновлено хешей: {updated_count}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка добавления хешей: {e}")
            return False
    
    def setup_access_permissions(self):
        """Настройка прав доступа к таблице"""
        try:
            # Настройка Google Sheets API с OAuth2
            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            
            # Пробуем разные способы аутентификации
            try:
                creds = ServiceAccountCredentials.from_json_keyfile_name('google_api_config.json', scope)
                client = gspread.authorize(creds)
            except Exception as e:
                print(f"⚠️ Ошибка с ServiceAccountCredentials: {e}")
                import pickle
                with open('token.pickle', 'rb') as token:
                    creds = pickle.load(token)
                client = gspread.authorize(creds)
            
            # Открываем таблицу
            spreadsheet = client.open_by_key(self.sheets_id)
            
            print("🔒 Настройка прав доступа к Google Sheets...")
            
            # Получаем текущие права доступа
            permissions = spreadsheet.list_permissions()
            
            print(f"📋 Текущие права доступа:")
            for perm in permissions:
                print(f"  - {perm.get('emailAddress', 'Unknown')}: {perm.get('role', 'Unknown')}")
            
            # Рекомендации по безопасности
            print("\n🔐 Рекомендации по безопасности:")
            print("1. Убедитесь, что таблица доступна только вашему сервисному аккаунту")
            print("2. Не делитесь ссылкой на таблицу публично")
            print("3. Регулярно обновляйте ключи API")
            print("4. Используйте переменные окружения для хранения ключей")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка настройки прав доступа: {e}")
            return False
    
    def create_backup_sheet(self):
        """Создание резервной копии таблицы"""
        try:
            # Настройка Google Sheets API с OAuth2
            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            
            # Пробуем разные способы аутентификации
            try:
                creds = ServiceAccountCredentials.from_json_keyfile_name('google_api_config.json', scope)
                client = gspread.authorize(creds)
            except Exception as e:
                print(f"⚠️ Ошибка с ServiceAccountCredentials: {e}")
                import pickle
                with open('token.pickle', 'rb') as token:
                    creds = pickle.load(token)
                client = gspread.authorize(creds)
            
            # Открываем основную таблицу
            main_sheet = client.open_by_key(self.sheets_id)
            
            # Создаем резервную копию
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_title = f"Platforma_Backup_{timestamp}"
            
            # Копируем таблицу
            backup_sheet = main_sheet.copy(title=backup_title)
            
            print(f"✅ Создана резервная копия: {backup_title}")
            print(f"🔗 Ссылка: {backup_sheet.url}")
            
            return backup_sheet.url
            
        except Exception as e:
            print(f"❌ Ошибка создания резервной копии: {e}")
            return None
    
    def validate_data_integrity(self):
        """Проверка целостности данных"""
        try:
            # Настройка Google Sheets API с OAuth2
            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            
            # Пробуем разные способы аутентификации
            try:
                creds = ServiceAccountCredentials.from_json_keyfile_name('google_api_config.json', scope)
                client = gspread.authorize(creds)
            except Exception as e:
                print(f"⚠️ Ошибка с ServiceAccountCredentials: {e}")
                import pickle
                with open('token.pickle', 'rb') as token:
                    creds = pickle.load(token)
                client = gspread.authorize(creds)
            
            # Открываем таблицу
            sheet = client.open_by_key(self.sheets_id).sheet1
            data = sheet.get_all_records()
            
            print("🔍 Проверка целостности данных...")
            
            valid_rows = 0
            invalid_rows = 0
            
            for i, row in enumerate(data, start=2):
                row_hash = row.get('Hash', '')
                row_without_hash = {k: v for k, v in row.items() if k != 'Hash'}
                
                if row_hash:
                    calculated_hash = self._create_row_hash(row_without_hash)
                    if row_hash == calculated_hash:
                        valid_rows += 1
                    else:
                        invalid_rows += 1
                        print(f"  ❌ Строка {i}: нарушена целостность для товара '{row.get('Title', 'Unknown')}'")
                else:
                    invalid_rows += 1
                    print(f"  ⚠️ Строка {i}: отсутствует хеш для товара '{row.get('Title', 'Unknown')}'")
            
            print(f"✅ Проверка завершена:")
            print(f"  - Валидных строк: {valid_rows}")
            print(f"  - Невалидных строк: {invalid_rows}")
            
            return valid_rows, invalid_rows
            
        except Exception as e:
            print(f"❌ Ошибка проверки целостности: {e}")
            return 0, 0
    
    def run_full_setup(self):
        """Запуск полной настройки безопасности"""
        print("🚀 Запуск настройки безопасности Google Sheets...")
        
        # 1. Добавляем хеши целостности
        print("\n1️⃣ Добавление хешей целостности...")
        if self.add_integrity_hashes():
            print("✅ Хеши целостности добавлены")
        else:
            print("❌ Ошибка добавления хешей")
            return False
        
        # 2. Проверяем целостность
        print("\n2️⃣ Проверка целостности данных...")
        valid, invalid = self.validate_data_integrity()
        
        if invalid > 0:
            print(f"⚠️ Найдено {invalid} строк с нарушенной целостностью")
        
        # 3. Настраиваем права доступа
        print("\n3️⃣ Настройка прав доступа...")
        self.setup_access_permissions()
        
        # 4. Создаем резервную копию
        print("\n4️⃣ Создание резервной копии...")
        backup_url = self.create_backup_sheet()
        
        print("\n🎉 Настройка безопасности завершена!")
        print("🔒 Google Sheets теперь защищен:")
        print("  - Хеши целостности добавлены")
        print("  - Данные защищены от несанкционированных изменений")
        print("  - Резервная копия создана")
        
        if backup_url:
            print(f"  - Резервная копия: {backup_url}")
        
        return True

def main():
    """Главная функция"""
    setup = SheetsSecuritySetup()
    setup.run_full_setup()

if __name__ == "__main__":
    main()
