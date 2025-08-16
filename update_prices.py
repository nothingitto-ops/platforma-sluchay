#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
from datetime import datetime

def update_price(product_title, new_price):
    """Обновляет цену товара в products.json и синхронизирует с app.min.js"""
    
    print(f"💰 Обновление цены для '{product_title}' на '{new_price}'")
    
    # 1. Обновляем products.json
    try:
        with open('products.json', 'r', encoding='utf-8') as f:
            products = json.load(f)
        
        # Ищем товар по названию
        found = False
        for product in products:
            if product.get('title') == product_title:
                old_price = product.get('price', '')
                product['price'] = new_price
                product['updated'] = datetime.now().isoformat()
                found = True
                print(f"✅ Обновлено в products.json: {old_price} → {new_price}")
                break
        
        if not found:
            print(f"❌ Товар '{product_title}' не найден в products.json")
            return False
        
        # Сохраняем обновленный products.json
        with open('products.json', 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        
        print("✅ products.json обновлен")
        
    except Exception as e:
        print(f"❌ Ошибка обновления products.json: {e}")
        return False
    
    # 2. Синхронизируем с app.min.js
    try:
        with open('app.min.js', 'r', encoding='utf-8') as f:
            app_js_content = f.read()
        
        # Ищем и заменяем цену в app.min.js
        # Ищем строку с названием товара и ценой
        pattern = rf'("title": "{re.escape(product_title)}",\s*"price": ")[^"]*(")'
        match = re.search(pattern, app_js_content)
        
        if match:
            old_price_js = match.group(0)
            new_price_js = f'"title": "{product_title}",\n    "price": "{new_price}"'
            
            app_js_content = app_js_content.replace(old_price_js, new_price_js)
            
            # Сохраняем обновленный app.min.js
            with open('app.min.js', 'w', encoding='utf-8') as f:
                f.write(app_js_content)
            
            print("✅ app.min.js синхронизирован")
            return True
        else:
            print("⚠️ Цена в app.min.js не найдена, но products.json обновлен")
            return True
            
    except Exception as e:
        print(f"❌ Ошибка синхронизации app.min.js: {e}")
        return False

if __name__ == "__main__":
    # Пример использования
    update_price("Пояс-юбка", "3000 р.")
