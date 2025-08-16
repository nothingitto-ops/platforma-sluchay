#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
from PIL import Image
import glob

def optimize_image(image_path, max_size=(800, 800), quality=85):
    """Оптимизирует изображение для веба"""
    try:
        with Image.open(image_path) as img:
            # Конвертируем в RGB если нужно
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Изменяем размер если изображение слишком большое
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Сохраняем с оптимизацией
            img.save(image_path, 'JPEG', quality=quality, optimize=True)
            print(f"✅ Оптимизировано: {image_path}")
            
    except Exception as e:
        print(f"❌ Ошибка оптимизации {image_path}: {e}")

def main():
    """Основная функция оптимизации"""
    print("🖼️ Начинаем оптимизацию изображений...")
    
    # Находим все JPG файлы в папке img
    img_files = glob.glob("img/**/*.jpg", recursive=True)
    
    if not img_files:
        print("❌ Изображения не найдены")
        return
    
    print(f"📸 Найдено {len(img_files)} изображений")
    
    # Оптимизируем каждое изображение
    for img_file in img_files:
        optimize_image(img_file)
    
    print("🎉 Оптимизация завершена!")

if __name__ == "__main__":
    main()
