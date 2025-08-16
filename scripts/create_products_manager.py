#!/usr/bin/env python3
"""
Менеджер товаров для платформы
Создание, редактирование и управление товарами без Google Sheets
"""

import os
import json
import shutil
import zipfile
import re
from datetime import datetime
import sys

class ProductsManager:
    def __init__(self):
        self.products_file = "products_data.json"
        self.web_dir = "../web_combined_working"
        self.images_dir = "../img"
        self.products = self.load_products()
        
    def load_products(self):
        """Загрузка товаров из JSON файла"""
        if os.path.exists(self.products_file):
            try:
                with open(self.products_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"✅ Загружено {len(data)} товаров из {self.products_file}")
                    return data
            except Exception as e:
                print(f"❌ Ошибка загрузки товаров: {e}")
                return []
        else:
            print("📝 Файл товаров не найден, создаем новый")
            return []
    
    def save_products(self):
        """Сохранение товаров в JSON файл"""
        try:
            with open(self.products_file, 'w', encoding='utf-8') as f:
                json.dump(self.products, f, ensure_ascii=False, indent=2)
            print(f"✅ Товары сохранены в {self.products_file}")
        except Exception as e:
            print(f"❌ Ошибка сохранения товаров: {e}")
    
    def add_product(self):
        """Добавление нового товара"""
        print("\n🆕 ДОБАВЛЕНИЕ НОВОГО ТОВАРА")
        print("=" * 40)
        
        # Генерация ID
        existing_ids = [p.get('id', '') for p in self.products]
        product_id = f"product_{len(self.products) + 1}"
        while product_id in existing_ids:
            product_id = f"product_{len(self.products) + 2}"
        
        # Ввод данных
        title = input("Название товара: ").strip()
        if not title:
            print("❌ Название обязательно!")
            return
        
        price = input("Цена (например: 3 500 ₽): ").strip()
        if not price:
            print("❌ Цена обязательна!")
            return
        
        desc = input("Описание: ").strip()
        meta = input("Состав и уход: ").strip()
        
        # Статус
        print("\nСтатус товара:")
        print("1. В наличии (stock)")
        print("2. Под заказ (preorder)")
        status_choice = input("Выберите статус (1 или 2): ").strip()
        status = "stock" if status_choice == "1" else "preorder"
        
        # Ссылка
        link = input("Ссылка на Telegram (Enter для стандартной): ").strip()
        if not link:
            link = "https://t.me/stub123"
        
        # Изображения
        print(f"\n📁 Папка с изображениями: {self.images_dir}/{product_id}/")
        print("Убедитесь, что изображения находятся в этой папке")
        print("Формат имен: product_id_1.jpg, product_id_2.jpg, и т.д.")
        
        # Проверяем существующие изображения
        images_path = os.path.join(self.images_dir, product_id)
        images = []
        if os.path.exists(images_path):
            for file in sorted(os.listdir(images_path)):
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    images.append(f"{product_id}/{file}")
        
        if not images:
            print("⚠️ Изображения не найдены! Создайте папку и добавьте изображения.")
            create_images = input("Создать папку для изображений? (y/n): ").strip().lower()
            if create_images == 'y':
                os.makedirs(images_path, exist_ok=True)
                print(f"✅ Создана папка: {images_path}")
        
        # Создание товара
        product = {
            "id": product_id,
            "title": title,
            "price": price,
            "desc": desc,
            "meta": meta,
            "status": status,
            "link": link,
            "section": "home",
            "images": images
        }
        
        self.products.append(product)
        self.save_products()
        print(f"✅ Товар '{title}' добавлен!")
    
    def edit_product(self):
        """Редактирование товара"""
        if not self.products:
            print("❌ Нет товаров для редактирования")
            return
        
        print("\n✏️ РЕДАКТИРОВАНИЕ ТОВАРА")
        print("=" * 40)
        
        # Показываем список товаров
        for i, product in enumerate(self.products, 1):
            print(f"{i}. {product['title']} - {product['price']}")
        
        try:
            choice = int(input(f"\nВыберите товар (1-{len(self.products)}): ")) - 1
            if choice < 0 or choice >= len(self.products):
                print("❌ Неверный номер!")
                return
        except ValueError:
            print("❌ Введите число!")
            return
        
        product = self.products[choice]
        print(f"\nРедактируем: {product['title']}")
        
        # Редактирование полей
        title = input(f"Название ({product['title']}): ").strip()
        if title:
            product['title'] = title
        
        price = input(f"Цена ({product['price']}): ").strip()
        if price:
            product['price'] = price
        
        desc = input(f"Описание ({product['desc']}): ").strip()
        if desc:
            product['desc'] = desc
        
        meta = input(f"Состав ({product['meta']}): ").strip()
        if meta:
            product['meta'] = meta
        
        link = input(f"Ссылка ({product['link']}): ").strip()
        if link:
            product['link'] = link
        
        # Статус
        print(f"\nТекущий статус: {product['status']}")
        print("1. В наличии (stock)")
        print("2. Под заказ (preorder)")
        status_choice = input("Новый статус (Enter для пропуска): ").strip()
        if status_choice == "1":
            product['status'] = "stock"
        elif status_choice == "2":
            product['status'] = "preorder"
        
        self.save_products()
        print("✅ Товар обновлен!")
    
    def delete_product(self):
        """Удаление товара"""
        if not self.products:
            print("❌ Нет товаров для удаления")
            return
        
        print("\n🗑️ УДАЛЕНИЕ ТОВАРА")
        print("=" * 40)
        
        # Показываем список товаров
        for i, product in enumerate(self.products, 1):
            print(f"{i}. {product['title']} - {product['price']}")
        
        try:
            choice = int(input(f"\nВыберите товар для удаления (1-{len(self.products)}): ")) - 1
            if choice < 0 or choice >= len(self.products):
                print("❌ Неверный номер!")
                return
        except ValueError:
            print("❌ Введите число!")
            return
        
        product = self.products[choice]
        confirm = input(f"Удалить товар '{product['title']}'? (y/n): ").strip().lower()
        
        if confirm == 'y':
            # Удаляем папку с изображениями
            images_path = os.path.join(self.images_dir, product['id'])
            if os.path.exists(images_path):
                shutil.rmtree(images_path)
                print(f"🗑️ Удалена папка изображений: {images_path}")
            
            # Удаляем товар из списка
            del self.products[choice]
            self.save_products()
            print("✅ Товар удален!")
        else:
            print("❌ Удаление отменено")
    
    def list_products(self):
        """Показ списка товаров"""
        if not self.products:
            print("📝 Нет товаров")
            return
        
        print("\n📋 СПИСОК ТОВАРОВ")
        print("=" * 60)
        
        for i, product in enumerate(self.products, 1):
            status_icon = "✅" if product['status'] == 'stock' else "⏳"
            print(f"{i}. {status_icon} {product['title']}")
            print(f"   💰 {product['price']}")
            print(f"   📝 {product['desc']}")
            print(f"   🖼️ {len(product['images'])} изображений")
            print(f"   🔗 {product['link']}")
            print("-" * 40)
    
    def update_app_js(self):
        """Обновление app.min.js с новыми данными"""
        print("\n🔄 ОБНОВЛЕНИЕ APP.MIN.JS")
        print("=" * 40)
        
        if not os.path.exists(self.web_dir):
            print(f"❌ Папка {self.web_dir} не найдена!")
            return
        
        app_js_path = os.path.join(self.web_dir, "app.min.js")
        if not os.path.exists(app_js_path):
            print(f"❌ Файл {app_js_path} не найден!")
            return
        
        try:
            # Читаем текущий файл
            with open(app_js_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Создаем новый массив товаров
            products_json = json.dumps(self.products, ensure_ascii=False, indent=2)
            
            # Заменяем массив товаров
            pattern = r'const products = \[.*?\];'
            replacement = f'const products = {products_json};'
            
            if re.search(pattern, content, re.DOTALL):
                new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
                
                # Создаем бэкап
                backup_path = f"{app_js_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copy2(app_js_path, backup_path)
                print(f"💾 Создан бэкап: {backup_path}")
                
                # Записываем новый файл
                with open(app_js_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"✅ app.min.js обновлен с {len(self.products)} товарами")
            else:
                print("❌ Не удалось найти массив товаров в app.min.js")
                
        except Exception as e:
            print(f"❌ Ошибка обновления app.min.js: {e}")
    
    def create_deploy(self):
        """Создание деплоя"""
        print("\n🚀 СОЗДАНИЕ ДЕПЛОЯ")
        print("=" * 40)
        
        if not os.path.exists(self.web_dir):
            print(f"❌ Папка {self.web_dir} не найдена!")
            return
        
        # Создаем папку для деплоя
        deploy_dir = f"deploy_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(deploy_dir, exist_ok=True)
        
        try:
            # Копируем файлы
            for item in os.listdir(self.web_dir):
                src = os.path.join(self.web_dir, item)
                dst = os.path.join(deploy_dir, item)
                
                if os.path.isdir(src):
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
            
            # Копируем изображения
            if os.path.exists(self.images_dir):
                img_dst = os.path.join(deploy_dir, "img")
                shutil.copytree(self.images_dir, img_dst)
            
            # Создаем ZIP архив
            zip_name = f"{deploy_dir}.zip"
            with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(deploy_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, deploy_dir)
                        zipf.write(file_path, arcname)
            
            print(f"✅ Деплой создан: {zip_name}")
            print(f"📁 Папка деплоя: {deploy_dir}")
            
        except Exception as e:
            print(f"❌ Ошибка создания деплоя: {e}")
    
    def run(self):
        """Основной цикл программы"""
        while True:
            print("\n" + "=" * 50)
            print("🛍️ МЕНЕДЖЕР ТОВАРОВ ПЛАТФОРМЫ")
            print("=" * 50)
            print("1. 📋 Показать все товары")
            print("2. 🆕 Добавить товар")
            print("3. ✏️ Редактировать товар")
            print("4. 🗑️ Удалить товар")
            print("5. 🔄 Обновить app.min.js")
            print("6. 🚀 Создать деплой")
            print("7. 💾 Сохранить товары")
            print("0. 🚪 Выход")
            
            choice = input("\nВыберите действие: ").strip()
            
            if choice == "1":
                self.list_products()
            elif choice == "2":
                self.add_product()
            elif choice == "3":
                self.edit_product()
            elif choice == "4":
                self.delete_product()
            elif choice == "5":
                self.update_app_js()
            elif choice == "6":
                self.create_deploy()
            elif choice == "7":
                self.save_products()
            elif choice == "0":
                print("👋 До свидания!")
                break
            else:
                print("❌ Неверный выбор!")

if __name__ == "__main__":
    manager = ProductsManager()
    manager.run()
