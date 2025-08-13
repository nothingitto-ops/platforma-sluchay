#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PIL import Image, ImageDraw, ImageFont
import os

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
    img.save('favicon.png')
    print("✅ Favicon PNG создан: favicon.png")
    
    # Создаем также 16x16 версию
    img_small = img.resize((16, 16), Image.Resampling.LANCZOS)
    img_small.save('favicon-16x16.png')
    print("✅ Favicon 16x16 создан: favicon-16x16.png")
    
    # Создаем также 48x48 версию
    img_large = img.resize((48, 48), Image.Resampling.LANCZOS)
    img_large.save('favicon-48x48.png')
    print("✅ Favicon 48x48 создан: favicon-48x48.png")
    
    print("🎉 Favicon файлы созданы!")
    print("📝 Добавьте в index.html:")
    print('<link rel="icon" type="image/png" sizes="32x32" href="favicon.png">')
    print('<link rel="icon" type="image/png" sizes="16x16" href="favicon-16x16.png">')
    
    return True

if __name__ == "__main__":
    create_favicon()
