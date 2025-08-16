#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🐙 Quick GitHub Deploy для Platforma
Простой скрипт для быстрого деплоя сайта через GitHub
"""

import os
import sys
import subprocess
from datetime import datetime

def main():
    print("🐙 Quick GitHub Deploy")
    print("=" * 30)
    
    # Проверяем наличие папки web_combined_working
    if not os.path.exists('web_combined_working'):
        print("❌ Папка 'web_combined_working' не найдена!")
        return False
    
    # Проверяем, что это Git репозиторий
    if not os.path.exists(os.path.join('web_combined_working', '.git')):
        print("❌ Папка 'web_combined_working' не является Git репозиторием!")
        print("💡 Убедитесь, что вы инициализировали Git в папке web_combined_working")
        return False
    
    try:
        # 1. Обновляем products.json
        print("📝 Обновляем products.json...")
        if os.path.exists('products.json'):
            import shutil
            shutil.copy2('products.json', 'web_combined_working/products.json')
            print("✅ products.json обновлен")
        
        # 2. Обновляем изображения
        print("🖼️ Обновляем изображения...")
        if os.path.exists('img'):
            web_img_dir = os.path.join('web_combined_working', 'img')
            if os.path.exists(web_img_dir):
                import shutil
                shutil.rmtree(web_img_dir)
            shutil.copytree('img', web_img_dir)
            print("✅ Изображения обновлены")
        
        # 3. Проверяем изменения
        print("🔍 Проверяем изменения...")
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, cwd='web_combined_working')
        
        if result.returncode == 0:
            changes = result.stdout.strip()
            if not changes:
                print("✅ Нет изменений для коммита")
                return True
        
        # 4. Добавляем изменения
        print("📦 Добавляем изменения...")
        result = subprocess.run(['git', 'add', '.'], 
                              capture_output=True, text=True, cwd='web_combined_working')
        if result.returncode != 0:
            print(f"❌ Ошибка добавления: {result.stderr}")
            return False
        
        # 5. Коммитим
        timestamp = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        commit_message = f"🚀 Автоматический деплой ({timestamp})"
        
        print(f"💾 Коммитим: {commit_message}")
        result = subprocess.run(['git', 'commit', '-m', commit_message], 
                              capture_output=True, text=True, cwd='web_combined_working')
        if result.returncode != 0:
            print(f"❌ Ошибка коммита: {result.stderr}")
            return False
        
        # 6. Пушим
        print("⬆️ Отправляем на GitHub...")
        result = subprocess.run(['git', 'push'], 
                              capture_output=True, text=True, cwd='web_combined_working')
        if result.returncode != 0:
            # Если нет upstream ветки, настраиваем её
            if "no upstream branch" in result.stderr:
                print("🔧 Настраиваем upstream ветку...")
                result = subprocess.run(['git', 'push', '--set-upstream', 'origin', 'main'], 
                                      capture_output=True, text=True, cwd='web_combined_working')
                if result.returncode != 0:
                    print(f"❌ Ошибка пуша: {result.stderr}")
                    return False
            else:
                print(f"❌ Ошибка пуша: {result.stderr}")
                return False
        
        print("✅ Деплой завершен успешно!")
        print("🌐 Сайт должен обновиться в ближайшее время")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n💡 Рекомендации:")
        print("1. Убедитесь, что папка 'web_combined_working' является Git репозиторием")
        print("2. Проверьте подключение к интернету")
        print("3. Убедитесь, что у вас есть права на пуш в репозиторий")
    
    input("\nНажмите Enter для выхода...")
