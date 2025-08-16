#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import zipfile
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

def create_favicon():
    """Создаем favicon с буквами PS"""
    
    print("🎨 Создаем favicon с буквами PS...")
    
    # Создаем изображение 32x32
    size = 32
    img = Image.new('RGBA', (size, size), (44, 62, 80, 255))  # #2c3e50
    draw = ImageDraw.Draw(img)
    
    # Пытаемся использовать системный шрифт
    try:
        # Для macOS
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 16)
    except:
        try:
            # Для Linux
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        except:
            # Fallback на стандартный шрифт
            font = ImageFont.load_default()
    
    # Рисуем текст "PS"
    text = "PS"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    
    draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
    
    # Сохраняем как PNG
    img.save('web/favicon.png')
    print("✅ Favicon PNG создан: web/favicon.png")
    
    # Создаем также 16x16 версию
    img_small = img.resize((16, 16), Image.Resampling.LANCZOS)
    img_small.save('web/favicon-16x16.png')
    print("✅ Favicon 16x16 создан: web/favicon-16x16.png")
    
    # Создаем также 48x48 версию
    img_large = img.resize((48, 48), Image.Resampling.LANCZOS)
    img_large.save('web/favicon-48x48.png')
    print("✅ Favicon 48x48 создан: web/favicon-48x48.png")
    
    return True

def update_index_html():
    """Обновляем index.html с favicon"""
    
    print("📝 Обновляем index.html с favicon...")
    
    index_path = 'web/index.html'
    
    # Читаем текущий index.html
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Ошибка чтения {index_path}: {e}")
        return False
    
    # Проверяем, есть ли уже favicon
    if 'favicon.png' in content:
        print("✅ Favicon уже добавлен в index.html")
        return True
    
    # Заменяем старый favicon на новый
    old_favicon = '<!-- Favicon - пустой для избежания 404 ошибок -->\n<link rel="icon" href="data:,">'
    new_favicon = '''<!-- Favicon -->
<link rel="icon" type="image/png" sizes="32x32" href="favicon.png">
<link rel="icon" type="image/png" sizes="16x16" href="favicon-16x16.png">
<link rel="icon" type="image/png" sizes="48x48" href="favicon-48x48.png">'''
    
    if old_favicon in content:
        content = content.replace(old_favicon, new_favicon)
    else:
        # Если нет старого favicon, добавляем новый после title
        title_pos = content.find('<title>')
        if title_pos != -1:
            title_end = content.find('</title>', title_pos) + 8
            content = content[:title_end] + '\n\n' + new_favicon + '\n' + content[title_end:]
    
    # Сохраняем обновленный файл
    try:
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ index.html обновлен с favicon")
        return True
    except Exception as e:
        print(f"❌ Ошибка сохранения {index_path}: {e}")
        return False

def create_deploy_archive():
    """Создаем архив для деплоя"""
    
    print("📦 Создаем архив для деплоя...")
    
    # Генерируем имя архива с текущей датой и временем
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = f"platforma_deploy_{timestamp}.zip"
    archive_path = f"../{archive_name}"
    
    # Переходим в папку web
    os.chdir('web')
    
    try:
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Функция для добавления файлов в архив
            def add_to_zip(path, arcname=None):
                if os.path.isfile(path):
                    zipf.write(path, arcname or path)
                    print(f"  ✅ Добавлен: {path}")
                elif os.path.isdir(path):
                    for root, dirs, files in os.walk(path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arc_path = os.path.relpath(file_path, '.')
                            zipf.write(file_path, arc_path)
                            print(f"  ✅ Добавлен: {arc_path}")
            
            # Добавляем основные файлы
            main_files = [
                'index.html',
                'app.min.js',
                'styles.min.css',
                'card-titles.css',
                'mobile.overrides.css',
                'favicon.png',
                'favicon-16x16.png',
                'favicon-48x48.png'
            ]
            
            for file in main_files:
                if os.path.exists(file):
                    add_to_zip(file)
                else:
                    print(f"  ⚠️  Файл не найден: {file}")
            
            # Добавляем папку img
            if os.path.exists('img'):
                add_to_zip('img')
            else:
                print("  ⚠️  Папка img не найдена")
            
            # Добавляем дополнительные файлы, если есть
            additional_files = [
                'data_hash.json',
                'site_info.json'
            ]
            
            for file in additional_files:
                if os.path.exists(file):
                    add_to_zip(file)
        
        print(f"✅ Архив создан: {archive_path}")
        
        # Показываем размер архива
        size_mb = os.path.getsize(archive_path) / (1024 * 1024)
        print(f"📊 Размер архива: {size_mb:.1f} MB")
        
        return archive_path
        
    except Exception as e:
        print(f"❌ Ошибка создания архива: {e}")
        return None

def main():
    """Основная функция"""
    
    print("🚀 Создание деплоя с favicon...")
    print("=" * 50)
    
    # Проверяем, что мы в правильной папке
    if not os.path.exists('web'):
        print("❌ Папка 'web' не найдена. Запустите скрипт из корневой папки проекта.")
        return False
    
    # Создаем favicon
    if not create_favicon():
        print("❌ Ошибка создания favicon")
        return False
    
    # Обновляем index.html
    if not update_index_html():
        print("❌ Ошибка обновления index.html")
        return False
    
    # Создаем архив
    archive_path = create_deploy_archive()
    if not archive_path:
        print("❌ Ошибка создания архива")
        return False
    
    print("=" * 50)
    print("🎉 Деплой с favicon готов!")
    print(f"📦 Архив: {archive_path}")
    print("✅ Favicon с буквами 'PS' добавлен")
    print("✅ index.html обновлен")
    print("✅ Все файлы включены в архив")
    print("\n🚀 Готово к выкладке на сайт!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
