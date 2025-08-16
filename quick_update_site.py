#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Быстрое обновление сайта
"""

import subprocess
import sys
import os

def main():
    """Быстрое обновление сайта"""
    print("🚀 Быстрое обновление сайта...")
    
    try:
        # Запускаем обновление данных
        result = subprocess.run([sys.executable, 'update_website_data.py'], 
                              capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            print("✅ Сайт обновлен успешно!")
            print("🌐 Обновите страницу в браузере: http://localhost:8000")
        else:
            print("❌ Ошибка обновления сайта:")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()
