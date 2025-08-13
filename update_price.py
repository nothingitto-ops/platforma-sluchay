#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys

def update_price(product_title, new_price):
    """Обновляет цену конкретного товара"""
    
    print(f"🔄 Обновление цены для товара '{product_title}' на '{new_price}'")
    
    # Загружаем данные
    try:
        with open('web/products.json', 'r', encoding='utf-8') as f:
            products = json.load(f)
    except Exception as e:
        print(f"❌ Ошибка загрузки products.json: {e}")
        return False
    
    # Ищем товар
    found = False
    for product in products:
        if product.get('title') == product_title:
            old_price = product.get('price', 'не указана')
            product['price'] = new_price
            found = True
            print(f"✅ Цена обновлена: {old_price} → {new_price}")
            break
    
    if not found:
        print(f"❌ Товар '{product_title}' не найден")
        return False
    
    # Сохраняем изменения
    try:
        with open('web/products.json', 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        print("✅ products.json обновлен")
    except Exception as e:
        print(f"❌ Ошибка сохранения: {e}")
        return False
    
    # Обновляем JavaScript
    try:
        import subprocess
        result = subprocess.run(['python', 'update_js_from_json.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ JavaScript файл обновлен")
            return True
        else:
            print(f"❌ Ошибка обновления JavaScript: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Ошибка запуска скрипта обновления: {e}")
        return False

def main():
    if len(sys.argv) != 3:
        print("Использование: python update_price.py 'Название товара' 'Новая цена'")
        print("Пример: python update_price.py 'Пояс-юбка' '3000 р.'")
        return
    
    product_title = sys.argv[1]
    new_price = sys.argv[2]
    
    success = update_price(product_title, new_price)
    
    if success:
        print("\n🎉 Цена успешно обновлена!")
        print("🔄 Обновите страницу в браузере для применения изменений")
    else:
        print("\n❌ Обновление не удалось")

if __name__ == "__main__":
    main()
