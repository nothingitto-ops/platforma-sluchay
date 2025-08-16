#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📝 Update Data Only - Обновление данных для Platforma
Скрипт для обновления данных в web_combined_working
"""

import os
import json
import shutil
from datetime import datetime

def main():
    print("📝 Update Data Only")
    print("=" * 30)
    
    # Пути к файлам
    web_dir = "web_combined_working"
    products_file = "products.json"
    images_dir = "img"
    
    # Проверяем наличие папки web_combined_working
    if not os.path.exists(web_dir):
        print(f"❌ Папка {web_dir} не найдена!")
        return False
    
    try:
        # 1. Обновляем products.json
        print("📝 Обновляем products.json...")
        if os.path.exists(products_file):
            web_products_file = os.path.join(web_dir, 'products.json')
            shutil.copy2(products_file, web_products_file)
            print(f"✅ {products_file} скопирован в {web_dir}")
        else:
            print(f"⚠️ Файл {products_file} не найден")
        
        # 2. Обновляем изображения
        print("🖼️ Обновляем изображения...")
        if os.path.exists(images_dir):
            web_img_dir = os.path.join(web_dir, 'img')
            if os.path.exists(web_img_dir):
                shutil.rmtree(web_img_dir)
            shutil.copytree(images_dir, web_img_dir)
            print(f"✅ Изображения скопированы в {web_dir}")
        else:
            print(f"⚠️ Папка {images_dir} не найдена")
        
        # 3. Обновляем app.min.js если есть скрипт
        print("🔧 Обновляем app.min.js...")
        update_js_scripts = [
            'update_js_from_json.py',
            os.path.join(web_dir, 'update_js_from_json.py')
        ]
        
        js_updated = False
        for script in update_js_scripts:
            if os.path.exists(script):
                print(f"📝 Запуск скрипта: {script}")
                import subprocess
                result = subprocess.run(['python', script], 
                                      capture_output=True, text=True)
                
                if result.returncode == 0:
                    print("✅ app.min.js обновлен")
                    js_updated = True
                    break
                else:
                    print(f"❌ Ошибка обновления app.min.js: {result.stderr}")
        
        if not js_updated:
            print("⚠️ Скрипт обновления app.min.js не найден")
        
        # 4. Создаем хеш данных
        print("🔐 Создаем хеш данных...")
        if os.path.exists(products_file):
            with open(products_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                import hashlib
                data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
                data_hash = hashlib.md5(data_str.encode('utf-8')).hexdigest()[:8]
                
                hash_data = {
                    "hash": data_hash,
                    "timestamp": datetime.now().isoformat(),
                    "products_count": len(data)
                }
                
                hash_file = os.path.join(web_dir, 'data_hash.json')
                with open(hash_file, 'w', encoding='utf-8') as f:
                    json.dump(hash_data, f, ensure_ascii=False, indent=2)
                
                print(f"✅ Хеш данных создан: {data_hash}")
        
        print("")
        print("✅ Обновление данных завершено!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n💡 Рекомендации:")
        print("1. Убедитесь, что папка web_combined_working существует")
        print("2. Проверьте наличие файла products.json")
        print("3. Убедитесь, что у вас есть права на запись")
    
    input("\nНажмите Enter для выхода...")
