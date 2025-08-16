#!/usr/bin/env python3
"""
Простой API сервер для обработки запросов к зашифрованным данным сайта
"""

import os
import json
import hashlib
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from cryptography.fernet import Fernet
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)
CORS(app)  # Разрешаем CORS для веб-сайта

class SecureAPI:
    def __init__(self):
        self.sheets_id = "1FLlyjpSd9EBOxZC8f0B6-iKRpKCMxcTRqWOHlgUpFoQ"
        self.encryption_key = self._get_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        self.cache = {}
        self.cache_timeout = 300  # 5 минут
        
    def _get_encryption_key(self):
        """Получение ключа шифрования"""
        key = os.getenv('SITE_ENCRYPTION_KEY')
        if not key:
            raise ValueError("SITE_ENCRYPTION_KEY не установлен")
        return key.encode()
    
    def _create_data_hash(self, data):
        """Создание хеша данных"""
        if isinstance(data, str):
            data = data.encode()
        return hashlib.sha256(data).hexdigest()
    
    def load_products_from_sheets(self):
        """Загрузка данных из Google Sheets"""
        try:
            # Проверяем кэш
            cache_key = 'products'
            if cache_key in self.cache:
                cache_time, cache_data = self.cache[cache_key]
                if (datetime.now() - cache_time).seconds < self.cache_timeout:
                    return cache_data
            
            # Настройка Google Sheets API
            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            creds = ServiceAccountCredentials.from_json_keyfile_name('google_api_config.json', scope)
            client = gspread.authorize(creds)
            
            # Открываем таблицу
            sheet = client.open_by_key(self.sheets_id).sheet1
            data = sheet.get_all_records()
            
            products = []
            for row in data:
                # Проверяем целостность данных
                row_hash = row.get('Hash', '')
                row_data = {k: v for k, v in row.items() if k != 'Hash'}
                
                # Создаем хеш для проверки
                calculated_hash = self._create_data_hash(json.dumps(row_data, sort_keys=True))
                
                if row_hash and row_hash != calculated_hash:
                    print(f"⚠️ Нарушена целостность данных для товара ID: {row.get('ID', 'Unknown')}")
                    continue
                
                products.append(row_data)
            
            # Сохраняем в кэш
            self.cache[cache_key] = (datetime.now(), products)
            
            return products
            
        except Exception as e:
            print(f"❌ Ошибка загрузки из Google Sheets: {e}")
            return []

# Инициализируем API
api = SecureAPI()

@app.route('/')
def index():
    """Главная страница"""
    return send_from_directory('../web', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Обслуживание статических файлов"""
    return send_from_directory('../web', filename)

@app.route('/api/products')
def get_products():
    """API для получения товаров"""
    try:
        products = api.load_products_from_sheets()
        
        # Создаем хеш данных
        products_json = json.dumps(products, ensure_ascii=False, sort_keys=True)
        data_hash = api._create_data_hash(products_json)
        
        response = {
            'success': True,
            'products': products,
            'hash': data_hash,
            'timestamp': datetime.now().isoformat(),
            'count': len(products)
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/decrypt', methods=['POST'])
def decrypt_data():
    """API для расшифровки данных"""
    try:
        data = request.get_json()
        encrypted_data = data.get('data')
        
        if not encrypted_data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Расшифровываем данные
        decrypted_data = api.cipher_suite.decrypt(encrypted_data.encode()).decode()
        products = json.loads(decrypted_data)
        
        return jsonify({
            'success': True,
            'products': products,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/status')
def get_status():
    """API для проверки статуса"""
    try:
        products = api.load_products_from_sheets()
        
        return jsonify({
            'success': True,
            'status': 'online',
            'products_count': len(products),
            'last_update': datetime.now().isoformat(),
            'cache_status': 'active' if 'products' in api.cache else 'empty'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/health')
def health_check():
    """Проверка здоровья сервера"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

if __name__ == '__main__':
    print("🚀 Запуск защищенного API сервера...")
    print("🔒 API доступен на http://localhost:5001")
    print("📊 Endpoints:")
    print("   - GET  /api/products - получение товаров")
    print("   - POST /api/decrypt  - расшифровка данных")
    print("   - GET  /api/status   - статус сервера")
    print("   - GET  /api/health   - проверка здоровья")
    
    app.run(host='0.0.0.0', port=5001, debug=False)
