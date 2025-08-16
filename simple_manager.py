#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
import json
import os
import subprocess
import shutil
import re
from datetime import datetime

class PlatformaManagerModern:
    def __init__(self, root):
        self.root = root
        self.root.title("Platforma Manager - Современная версия")
        self.root.geometry("1400x900")
        
        # Настройка шрифтов
        self.font_base = ('Arial', 12)
        self.font_bold = ('Arial', 12, 'bold')
        self.font_header = ('Arial', 14, 'bold')
        
        # Переменные состояния
        self.current_section = 'home'
        self.web_server = None
        self.web_server_thread = None
        
        # Пути к файлам
        self.web_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web_combined_working")
        self.images_dir = "img"
        self.products_file = "products.json"
        
        # Загружаем данные
        self.load_products()
        
        # Создаем интерфейс
        self.create_ui()
        
    def load_products(self):
        """Загрузка товаров из файла"""
        try:
            # Сначала пробуем загрузить из products_data.json
            if os.path.exists(self.products_file):
                with open(self.products_file, 'r', encoding='utf-8') as f:
                    self.products = json.load(f)
                print(f"✅ Загружено {len(self.products)} товаров из {self.products_file}")
            # Если нет, пробуем из products.json
            elif os.path.exists('products.json'):
                with open('products.json', 'r', encoding='utf-8') as f:
                    self.products = json.load(f)
                    print(f"✅ Загружено {len(self.products)} товаров из products.json")
            else:
                print("📝 Файл товаров не найден, создаем новый")
                self.products = []
        except Exception as e:
            print(f"❌ Ошибка загрузки: {e}")
            self.products = []
    
    def save_products(self):
        """Сохранение товаров в файл с автоматическим обновлением"""
        try:
            with open(self.products_file, 'w', encoding='utf-8') as f:
                json.dump(self.products, f, ensure_ascii=False, indent=2)
            print(f"✅ Товары сохранены в {self.products_file}")
            
            # Автоматически запускаем локальное обновление данных
            self.root.after(100, self.update_data_local)
            
        except Exception as e:
            print(f"❌ Ошибка сохранения: {e}")
    
    def create_ui(self):
        """Создание интерфейса"""
        # Главный контейнер
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Навигационная панель
        self.create_navigation_bar(main_container)
        
        # Область контента
        self.create_content_area(main_container)
    
    def create_navigation_bar(self, parent):
        """Создание навигационной панели"""
        # Панель поиска и действий
        action_bar = ttk.Frame(parent)
        action_bar.pack(fill=tk.X, pady=(0, 20))
        
        # Поиск
        search_frame = ttk.Frame(action_bar)
        search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(search_frame, text="Поиск:", font=self.font_base).pack(side=tk.LEFT, padx=(0, 10))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT)
        search_entry.bind("<Return>", lambda e: self.apply_search())
        
        # Кнопки действий
        buttons_frame = ttk.Frame(action_bar)
        buttons_frame.pack(side=tk.RIGHT)
        
        ttk.Button(buttons_frame, text="➕ Добавить", command=self.show_add_section, 
                  style='Accent.TButton').pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="📝 Обновить данные", command=self.update_data_local).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="🚀 Обновить + Деплой", command=self.update_data, 
                  style='Accent.TButton').pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="🔄 Обновить app.min.js", command=self.update_app_js).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="👁 Просмотр", command=self.show_preview_window).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="🐙 GitHub", command=self.github_deploy).pack(side=tk.LEFT, padx=(0, 5))
    
    def create_content_area(self, parent):
        """Создание области контента"""
        self.content_frame = ttk.Frame(parent)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Создаем все секции
        self.create_products_section()
        self.create_add_section()
        self.create_deploy_section()
        
        # Показываем секцию товаров по умолчанию
        self.show_products_section()
    
    def create_products_section(self):
        """Создание секции товаров"""
        self.products_frame = ttk.Frame(self.content_frame)
        
        # Боковая панель с разделами
        sidebar = ttk.Frame(self.products_frame, width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        
        ttk.Label(sidebar, text="Разделы:", font=self.font_header).pack(anchor=tk.W, pady=(0, 10))
        
        # Кнопки разделов
        self.section_buttons = {}
        sections = [('home', '🏠 Главная'), ('nessffo', '📋 Nessffo')]
        
        for section_id, section_name in sections:
            btn = ttk.Button(sidebar, text=section_name, 
                           command=lambda s=section_id: self.filter_by_section(s))
            btn.pack(fill=tk.X, pady=2)
            self.section_buttons[section_id] = btn
        
        # Основная область с товарами
        main_area = ttk.Frame(self.products_frame)
        main_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Заголовок
        ttk.Label(main_area, text="Товары", font=self.font_header).pack(anchor=tk.W, pady=(0, 10))
        
        # Создаем Treeview для товаров
        columns = ('ID', 'Название', 'Цена', 'Статус', 'Изображения', 'Раздел', 'Порядок')
        self.products_tree = ttk.Treeview(main_area, columns=columns, show='headings', height=15)
        
        # Настройка колонок
        for col in columns:
            self.products_tree.heading(col, text=col)
            self.products_tree.column(col, width=100)
        
        # Настройка ширины колонок
        self.products_tree.column('ID', width=80)
        self.products_tree.column('Название', width=200)
        self.products_tree.column('Цена', width=100)
        self.products_tree.column('Статус', width=100)
        self.products_tree.column('Изображения', width=100)
        self.products_tree.column('Раздел', width=80)
        self.products_tree.column('Порядок', width=80)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(main_area, orient=tk.VERTICAL, command=self.products_tree.yview)
        self.products_tree.configure(yscrollcommand=scrollbar.set)
        
        self.products_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопки действий с товарами
        actions_frame = ttk.Frame(main_area)
        actions_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(actions_frame, text="✏️ Редактировать", command=self.edit_selected_product).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(actions_frame, text="🗑️ Удалить", command=self.delete_selected_product).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(actions_frame, text="🖼️ Управление изображениями", command=self.manage_images).pack(side=tk.LEFT, padx=(0, 5))
        
        # Привязываем события
        self.products_tree.bind('<Double-1>', lambda e: self.edit_selected_product())
        
        # Обновляем список товаров
        self.refresh_products_list()
    
    def create_add_section(self):
        """Создание секции добавления товара"""
        self.add_frame = ttk.Frame(self.content_frame)
        
        # Заголовок
        ttk.Label(self.add_frame, text="Добавление нового товара", font=self.font_header).pack(anchor=tk.W, pady=(0, 20))
        
        # Форма
        form_frame = ttk.Frame(self.add_frame)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Левая колонка
        left_col = ttk.Frame(form_frame)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))
        
        # Поля формы
        fields = [
            ('ID товара:', 'product_id_var'),
            ('Название:', 'title_var'),
            ('Цена:', 'price_var'),
            ('Описание:', 'desc_var'),
            ('Состав:', 'meta_var')
        ]
        
        self.form_vars = {}
        for i, (label, var_name) in enumerate(fields):
            frame = ttk.Frame(left_col)
            frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(frame, text=label, width=15).pack(side=tk.LEFT)
            var = tk.StringVar()
            
            # Для поля ID делаем его только для чтения и заполняем автоматически
            if var_name == 'product_id_var':
                # Генерируем следующий ID
                max_id = 0
                for p in self.products:
                    try:
                        p_id = int(p.get('id', '0'))
                        max_id = max(max_id, p_id)
                    except ValueError:
                        continue
                next_id = str(max_id + 1)
                var.set(next_id)
                
                entry = ttk.Entry(frame, textvariable=var, width=40, state='readonly')
            else:
                entry = ttk.Entry(frame, textvariable=var, width=40)
            
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.form_vars[var_name] = var
        
        # Статус
        status_frame = ttk.Frame(left_col)
        status_frame.pack(fill=tk.X, pady=5)
        ttk.Label(status_frame, text="Статус:", width=15).pack(side=tk.LEFT)
        self.status_var = tk.StringVar(value="preorder")
        ttk.Radiobutton(status_frame, text="Под заказ", variable=self.status_var, value="preorder").pack(side=tk.LEFT)
        ttk.Radiobutton(status_frame, text="В наличии", variable=self.status_var, value="stock").pack(side=tk.LEFT)
        
        # Раздел
        section_frame = ttk.Frame(left_col)
        section_frame.pack(fill=tk.X, pady=5)
        ttk.Label(section_frame, text="Раздел:", width=15).pack(side=tk.LEFT)
        self.section_var = tk.StringVar(value="home")
        ttk.Radiobutton(section_frame, text="Главная", variable=self.section_var, value="home").pack(side=tk.LEFT)
        ttk.Radiobutton(section_frame, text="Nessffo", variable=self.section_var, value="nessffo").pack(side=tk.LEFT)
        
        # Порядок (только для отображения)
        order_frame = ttk.Frame(left_col)
        order_frame.pack(fill=tk.X, pady=5)
        ttk.Label(order_frame, text="Порядок:", width=15).pack(side=tk.LEFT)
        self.order_display_var = tk.StringVar(value="13")
        order_entry = ttk.Entry(order_frame, textvariable=self.order_display_var, width=10, state='readonly')
        order_entry.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(order_frame, text="🔄 Обновить", command=self.update_order_display).pack(side=tk.LEFT)
        
        # Инициализируем отображение
        self.update_order_display()
        
        # Правая колонка
        right_col = ttk.Frame(form_frame)
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Изображения
        ttk.Label(right_col, text="Изображения:", font=self.font_bold).pack(anchor=tk.W, pady=(0, 10))
        
        self.images_listbox = tk.Listbox(right_col, height=10)
        self.images_listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        images_buttons = ttk.Frame(right_col)
        images_buttons.pack(fill=tk.X)
        
        ttk.Button(images_buttons, text="📁 Выбрать папку", command=self.select_images_folder).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(images_buttons, text="📄 Добавить файлы", command=self.add_single_image).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(images_buttons, text="🗑️ Очистить", command=self.clear_images).pack(side=tk.LEFT)
        
        # Кнопки действий
        actions_frame = ttk.Frame(self.add_frame)
        actions_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(actions_frame, text="💾 Сохранить товар", command=self.save_new_product, 
                  style='Accent.TButton').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(actions_frame, text="🔄 Очистить форму", command=self.clear_form).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(actions_frame, text="❌ Отмена", command=self.show_products_section).pack(side=tk.LEFT)
    
    def create_deploy_section(self):
        """Создание секции деплоя"""
        self.deploy_frame = ttk.Frame(self.content_frame)
        
        # Заголовок
        ttk.Label(self.deploy_frame, text="Деплой и публикация", font=self.font_header).pack(anchor=tk.W, pady=(0, 20))
        
        # Опции деплоя
        deploy_options = ttk.LabelFrame(self.deploy_frame, text="Опции деплоя")
        deploy_options.pack(fill=tk.X, pady=(0, 20))
        
        # Локальный сервер
        server_frame = ttk.Frame(deploy_options)
        server_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(server_frame, text="Локальный сервер:").pack(side=tk.LEFT)
        self.server_port_var = tk.StringVar(value="8005")
        ttk.Entry(server_frame, textvariable=self.server_port_var, width=10).pack(side=tk.LEFT, padx=(10, 10))
        
        self.server_button = ttk.Button(server_frame, text="🚀 Запустить сервер", command=self.toggle_server)
        self.server_button.pack(side=tk.LEFT)
        
        # Создание деплоя
        deploy_frame = ttk.Frame(deploy_options)
        deploy_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(deploy_frame, text="🐙 GitHub Pages", command=self.github_deploy).pack(side=tk.LEFT)
        
        # Статус
        self.status_label = ttk.Label(self.deploy_frame, text="Готов к работе", font=self.font_base)
        self.status_label.pack(anchor=tk.W, pady=(20, 0))
    
    def show_products_section(self):
        """Показать секцию товаров"""
        self.hide_all_sections()
        self.products_frame.pack(fill=tk.BOTH, expand=True)
        self.current_section = 'products'
        
        # По умолчанию показываем только товары раздела "Главная"
        self.filter_by_section('home')
    
    def show_add_section(self):
        """Показать секцию добавления"""
        self.hide_all_sections()
        self.add_frame.pack(fill=tk.BOTH, expand=True)
        self.current_section = 'add'
    
    def show_deploy_section(self):
        """Показать секцию деплоя"""
        self.hide_all_sections()
        self.deploy_frame.pack(fill=tk.BOTH, expand=True)
        self.current_section = 'deploy'
    
    def hide_all_sections(self):
        """Скрыть все секции"""
        self.products_frame.pack_forget()
        self.add_frame.pack_forget()
        self.deploy_frame.pack_forget()
    
    def refresh_products_list(self):
        """Обновить список товаров"""
        # Очищаем список
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        # Если есть текущий раздел, показываем только товары этого раздела
        if hasattr(self, 'current_section') and self.current_section in ['home', 'nessffo']:
            self.filter_by_section(self.current_section)
        else:
            # По умолчанию показываем товары раздела "Главная"
            self.filter_by_section('home')
    
    def filter_by_section(self, section):
        """Фильтрация по разделу"""
        self.current_section = section
        
        # Обновляем кнопки
        for section_id, btn in self.section_buttons.items():
            if section_id == section:
                btn.configure(style='Accent.TButton')
            else:
                btn.configure(style='TButton')
        
        # Очищаем список
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        # Фильтруем и добавляем товары по разделу
        filtered_products = [p for p in self.products if p.get('section', 'home') == section]
        # Сортируем по порядку
        sorted_filtered_products = sorted(filtered_products, key=lambda x: int(x.get('order', '0')))
        
        for product in sorted_filtered_products:
            status_icon = "✅" if product.get('status') == 'stock' else "⏳"
            images_str = product.get('images', '')
            images_count = len(images_str.split(',')) if images_str else 0
            
            self.products_tree.insert('', 'end', values=(
                product.get('id', ''),
                product.get('title', ''),
                product.get('price', ''),
                f"{status_icon} {product.get('status', '')}",
                f"{images_count} файлов",
                product.get('section', 'home'),
                product.get('order', '1')
            ))
    
    def apply_search(self):
        """Применить поиск"""
        search_term = self.search_var.get().lower()
        
        # Очищаем список
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        # Фильтруем и добавляем товары
        for product in self.products:
            if (search_term in product.get('title', '').lower() or 
                search_term in product.get('desc', '').lower() or
                search_term in product.get('id', '').lower()):
                
                status_icon = "✅" if product.get('status') == 'stock' else "⏳"
                images_str = product.get('images', '')
                images_count = len(images_str.split(',')) if images_str else 0
                
                self.products_tree.insert('', 'end', values=(
                    product.get('id', ''),
                    product.get('title', ''),
                    product.get('price', ''),
                    f"{status_icon} {product.get('status', '')}",
                    f"{images_count} файлов",
                    product.get('section', 'home'),
                    product.get('order', '1')
                ))
    
    def edit_selected_product(self):
        """Редактировать выбранный товар"""
        print("🔍 Функция edit_selected_product вызвана")
        
        selection = self.products_tree.selection()
        print(f"🔍 Выбранные элементы: {selection}")
        
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите товар для редактирования")
            return
        
        # Получаем ID товара
        item = self.products_tree.item(selection[0])
        product_id = item['values'][0]
        print(f"🔍 ID товара: {product_id}")
        print(f"🔍 Доступные ID в данных: {[p.get('id') for p in self.products]}")
        
        # Находим товар
        product = None
        for p in self.products:
            if str(p.get('id', '')) == str(product_id):
                product = p
                break
        
        print(f"🔍 Найден товар: {product}")
        
        if product:
            print("🔍 Открываем диалог редактирования")
            self.show_edit_dialog(product)
        else:
            print("❌ Товар не найден")
            messagebox.showerror("Ошибка", f"Товар с ID {product_id} не найден")
    
    def show_edit_dialog(self, product):
        """Показать диалог редактирования"""
        print("🔍 Функция show_edit_dialog вызвана")
        print(f"🔍 Товар для редактирования: {product}")
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Редактирование: {product['title']}")
        dialog.geometry("800x700")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Создаем скроллируемый фрейм
        canvas = tk.Canvas(dialog)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Форма редактирования
        form_frame = ttk.Frame(scrollable_frame, padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        ttk.Label(form_frame, text=f"Редактирование товара: {product['title']}", 
                 font=self.font_header).pack(anchor=tk.W, pady=(0, 20))
        
        # Основные поля
        # Очищаем цену от "р." для отображения
        price_value = product.get('price', '')
        if price_value and 'р.' in price_value:
            price_value = price_value.replace('р.', '').strip()
        
        fields = [
            ('ID:', 'id', product.get('id', '')),
            ('Название:', 'title', product.get('title', '')),
            ('Цена:', 'price', price_value),
            ('Описание:', 'desc', product.get('desc', '')),
            ('Состав:', 'meta', product.get('meta', '')),
            ('Ссылка:', 'link', product.get('link', ''))
        ]
        
        edit_vars = {}
        for label, field, value in fields:
            frame = ttk.Frame(form_frame)
            frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(frame, text=label, width=15).pack(side=tk.LEFT)
            var = tk.StringVar(value=value)
            entry = ttk.Entry(frame, textvariable=var, width=50)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            edit_vars[field] = var
        
        # Статус
        status_frame = ttk.Frame(form_frame)
        status_frame.pack(fill=tk.X, pady=10)
        ttk.Label(status_frame, text="Статус:", width=15).pack(side=tk.LEFT)
        status_var = tk.StringVar(value=product.get('status', 'preorder'))
        ttk.Radiobutton(status_frame, text="Под заказ", variable=status_var, value="preorder").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(status_frame, text="В наличии", variable=status_var, value="stock").pack(side=tk.LEFT)
        
        # Раздел
        section_frame = ttk.Frame(form_frame)
        section_frame.pack(fill=tk.X, pady=10)
        ttk.Label(section_frame, text="Раздел:", width=15).pack(side=tk.LEFT)
        section_var = tk.StringVar(value=product.get('section', 'home'))
        ttk.Radiobutton(section_frame, text="Главная", variable=section_var, value="home").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(section_frame, text="Nessffo", variable=section_var, value="nessffo").pack(side=tk.LEFT)
        
        # Порядок
        order_frame = ttk.Frame(form_frame)
        order_frame.pack(fill=tk.X, pady=10)
        ttk.Label(order_frame, text="Порядок:", width=15).pack(side=tk.LEFT)
        order_var = tk.StringVar(value=str(product.get('order', '1')))
        order_entry = ttk.Entry(order_frame, textvariable=order_var, width=10)
        order_entry.pack(side=tk.LEFT)
        
        # Изображения
        images_frame = ttk.LabelFrame(form_frame, text="Изображения", padding=10)
        images_frame.pack(fill=tk.X, pady=10)
        
        # Текущие изображения
        current_images = product.get('images', '')
        if isinstance(current_images, str):
            current_images = current_images.split(',') if current_images else []
        
        ttk.Label(images_frame, text="Текущие изображения:").pack(anchor=tk.W, pady=(0, 5))
        
        # Список изображений
        images_listbox = tk.Listbox(images_frame, height=6)
        images_listbox.pack(fill=tk.X, pady=(0, 10))
        
        for img in current_images:
            if img.strip():
                images_listbox.insert(tk.END, img.strip())
        
        # Кнопки для изображений
        images_buttons = ttk.Frame(images_frame)
        images_buttons.pack(fill=tk.X)
        
        def add_image():
            file_path = filedialog.askopenfilename(
                title="Выберите изображение",
                filetypes=[("Изображения", "*.jpg *.jpeg *.png")]
            )
            if file_path:
                # Обрабатываем изображение правильно
                product_id = product.get('id', '')
                if product_id:
                    try:
                        # Копируем изображение в правильную папку (основная папка)
                        product_folder = os.path.join(self.images_dir, f'product_{product_id}')
                        os.makedirs(product_folder, exist_ok=True)
                        
                        # Определяем следующий номер файла
                        existing_files = [f for f in os.listdir(product_folder) if f.startswith(f'product_{product_id}_') and f.endswith('.jpg')]
                        next_number = len(existing_files) + 1
                        
                        # Генерируем новое имя файла
                        new_filename = f'product_{product_id}_{next_number}.jpg'
                        new_path = os.path.join(product_folder, new_filename)
                        
                        # Копируем файл в основную папку
                        shutil.copy2(file_path, new_path)
                        
                        # Также копируем в web_combined_working
                        web_product_folder = os.path.join(self.web_dir, 'img', f'product_{product_id}')
                        os.makedirs(web_product_folder, exist_ok=True)
                        web_new_path = os.path.join(web_product_folder, new_filename)
                        shutil.copy2(file_path, web_new_path)
                        
                        # Добавляем правильный путь в список
                        correct_path = f'product_{product_id}/{new_filename}'
                        
                        # Добавляем новый файл в список (не заменяем существующие)
                        images_listbox.insert(tk.END, correct_path)
                        
                        print(f"📸 Добавлено изображение: {os.path.basename(file_path)} → {new_filename}")
                        
                        # Показываем сообщение об успехе
                        messagebox.showinfo("Успех", f"Изображение добавлено: {new_filename}")
                        
                    except Exception as e:
                        print(f"❌ Ошибка добавления изображения: {e}")
                        messagebox.showerror("Ошибка", f"Не удалось добавить изображение: {e}")
                else:
                    messagebox.showerror("Ошибка", "Не удалось определить ID товара")
        
        def remove_image():
            selection = images_listbox.curselection()
            if selection:
                # Получаем путь к файлу
                image_path = images_listbox.get(selection[0])
                
                # Удаляем файл физически из обеих папок
                web_full_path = os.path.join(self.web_dir, 'img', image_path)
                main_full_path = os.path.join(self.images_dir, image_path)
                
                if os.path.exists(web_full_path):
                    try:
                        os.remove(web_full_path)
                        print(f"🗑️ Удален файл из web: {image_path}")
                    except Exception as e:
                        print(f"⚠️ Ошибка удаления файла из web {image_path}: {e}")
                
                if os.path.exists(main_full_path):
                    try:
                        os.remove(main_full_path)
                        print(f"🗑️ Удален файл из main: {image_path}")
                    except Exception as e:
                        print(f"⚠️ Ошибка удаления файла из main {image_path}: {e}")
                
                # Удаляем из списка
                images_listbox.delete(selection)
                
                # Автоматически обновляем данные
                self.root.after(100, lambda: self.update_data_local())
        
        def move_up():
            selection = images_listbox.curselection()
            if selection and selection[0] > 0:
                text = images_listbox.get(selection[0])
                images_listbox.delete(selection[0])
                images_listbox.insert(selection[0] - 1, text)
                images_listbox.selection_set(selection[0] - 1)
        
        def move_down():
            selection = images_listbox.curselection()
            if selection and selection[0] < images_listbox.size() - 1:
                text = images_listbox.get(selection[0])
                images_listbox.delete(selection[0])
                images_listbox.insert(selection[0] + 1, text)
                images_listbox.selection_set(selection[0] + 1)
        
        ttk.Button(images_buttons, text="➕ Добавить", command=add_image).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(images_buttons, text="🗑️ Удалить", command=remove_image).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(images_buttons, text="⬆️ Вверх", command=move_up).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(images_buttons, text="⬇️ Вниз", command=move_down).pack(side=tk.LEFT)
        
        # Кнопки действий
        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.pack(fill=tk.X, pady=(20, 0))
        
        def save_changes():
            try:
                # Обновляем товар
                for field, var in edit_vars.items():
                    value = var.get()
                    # Добавляем "р." к цене если его нет
                    if field == 'price' and value and not value.endswith('р.'):
                        value = f"{value} р."
                    product[field] = value
                product['status'] = status_var.get()
                product['section'] = section_var.get()
                product['order'] = int(order_var.get()) if order_var.get().isdigit() else 1
                
                # Обновляем изображения
                images_list = []
                for i in range(images_listbox.size()):
                    images_list.append(images_listbox.get(i))
                product['images'] = ','.join(images_list)
                
                # Добавляем время обновления
                product['updated'] = datetime.now().isoformat()
                
                self.save_products()
                self.refresh_products_list()
                dialog.destroy()
                messagebox.showinfo("Успех", "Товар обновлен!")
            except Exception as e:
                print(f"❌ Ошибка сохранения изменений: {e}")
                messagebox.showerror("Ошибка", f"Не удалось сохранить изменения: {e}")
        
        ttk.Button(buttons_frame, text="💾 Сохранить", command=save_changes, 
                  style='Accent.TButton').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="❌ Отмена", command=dialog.destroy).pack(side=tk.LEFT)
        
        # Настройка скролла
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def delete_selected_product(self):
        """Удалить выбранный товар"""
        selection = self.products_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите товар для удаления")
            return
        
        # Получаем ID товара
        item = self.products_tree.item(selection[0])
        product_id = str(item['values'][0])  # Преобразуем в строку
        product_title = item['values'][1]
        
        # Находим товар для удаления
        product_to_delete = None
        for p in self.products:
            if str(p.get('id', '')) == product_id:  # Сравниваем как строки
                product_to_delete = p
                break
        
        if not product_to_delete:
            messagebox.showerror("Ошибка", "Товар не найден")
            return
        
        # Подтверждение
        if not messagebox.askyesno("Подтверждение", f"Удалить товар '{product_title}'?"):
            return
        
        # Получаем раздел и order удаляемого товара
        deleted_section = product_to_delete.get('section', 'home')
        deleted_order = int(product_to_delete.get('order', '1'))
        
        # Удаляем физические файлы изображений
        try:
            product_images = product_to_delete.get('images', '')
            if product_images:
                # Удаляем папку с изображениями товара
                product_folder = os.path.join(self.web_dir, 'img', f'product_{product_id}')
                if os.path.exists(product_folder):
                    shutil.rmtree(product_folder)
                    print(f"🗑️ Удалена папка изображений: {product_folder}")
        except Exception as e:
            print(f"⚠️ Ошибка удаления файлов изображений: {e}")
        
        # Удаляем товар
        self.products = [p for p in self.products if p.get('id') != product_id]
        
        # Сдвигаем order всех товаров в том же разделе с большим order на -1
        for p in self.products:
            if p.get('section') == deleted_section:
                current_order = int(p.get('order', '0'))
                if current_order > deleted_order:
                    p['order'] = str(current_order - 1)
        
        self.save_products()
        self.refresh_products_list()
        
        messagebox.showinfo("Успех", "Товар удален!")
    
    def select_images_folder(self):
        """Выбрать папку с изображениями"""
        folder = filedialog.askdirectory(title="Выберите папку с изображениями")
        if folder:
            # Очищаем список
            self.images_listbox.delete(0, tk.END)
            
            # Получаем ID товара для формирования пути
            product_id = self.form_vars['product_id_var'].get().strip()
            
            # Добавляем изображения с путями
            for file in sorted(os.listdir(folder)):
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    image_path = f"{product_id}/{file}"
                    self.images_listbox.insert(tk.END, image_path)
            
            # Сохраняем путь к папке
            self.selected_images_folder = folder
            
            # Показываем сообщение о количестве добавленных изображений
            count = len([f for f in os.listdir(folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
            messagebox.showinfo("Изображения", f"Добавлено {count} изображений")
    
    def add_single_image(self):
        """Добавить изображения (один или несколько файлов)"""
        file_paths = filedialog.askopenfilenames(
            title="Выберите изображения",
            filetypes=[("Изображения", "*.jpg *.jpeg *.png")]
        )
        if file_paths:
            # Получаем ID товара для формирования пути
            product_id = self.form_vars['product_id_var'].get().strip()
            
            # Сохраняем оригинальные пути для обработки
            if not hasattr(self, 'original_image_paths'):
                self.original_image_paths = {}
            
            # Добавляем все выбранные файлы
            for file_path in file_paths:
                # Получаем только имя файла
                filename = os.path.basename(file_path)
                image_path = f"{product_id}/{filename}"
                
                # Сохраняем оригинальный путь
                self.original_image_paths[image_path] = file_path
                
                # Добавляем в список
                self.images_listbox.insert(tk.END, image_path)
            
            # Показываем сообщение о количестве добавленных изображений
            messagebox.showinfo("Изображения", f"Добавлено {len(file_paths)} изображений")
    
    def process_product_images(self, product_id, images_list):
        """Обработать изображения товара и вернуть правильные пути (устаревшая функция)"""
        print(f"⚠️ Функция process_product_images устарела для товара {product_id}")
        return []
    
    def update_order_display(self, *args):
        """Обновить отображение order при изменении раздела"""
        if hasattr(self, 'section_var') and hasattr(self, 'order_display_var'):
            section = self.section_var.get()
            section_products = [p for p in self.products if p.get('section') == section]
            
            # Находим максимальный order в разделе
            max_order = 0
            for p in section_products:
                try:
                    current_order = int(p.get('order', '0'))
                    max_order = max(max_order, current_order)
                except ValueError:
                    continue
            
            # Новый товар получает следующий order
            next_order = max_order + 1
            
            self.order_display_var.set(str(next_order))
    
    def clear_images(self):
        """Очистить список изображений"""
        self.images_listbox.delete(0, tk.END)
        self.selected_images_folder = None
        # Очищаем сохраненные пути
        if hasattr(self, 'original_image_paths'):
            self.original_image_paths.clear()
    
    def save_new_product(self):
        """Сохранить новый товар"""
        # Проверяем обязательные поля
        if not self.form_vars['title_var'].get().strip():
            messagebox.showerror("Ошибка", "Название товара обязательно!")
            return
        
        if not self.form_vars['price_var'].get().strip():
            messagebox.showerror("Ошибка", "Цена товара обязательна!")
            return
        
        # Получаем ID (он уже автоматически заполнен)
        product_id = self.form_vars['product_id_var'].get().strip()
        
        # Используем фиксированную ссылку
        link = "https://t.me/stub123"
        
        # Добавляем "р." к цене если его нет
        price = self.form_vars['price_var'].get().strip()
        if price and not price.endswith('р.'):
            price = f"{price} р."
        
        # Определяем order для выбранного раздела
        section = self.section_var.get()
        section_products = [p for p in self.products if p.get('section') == section]
        
        # Находим максимальный order в разделе
        max_order = 0
        for p in section_products:
            try:
                current_order = int(p.get('order', '0'))
                max_order = max(max_order, current_order)
            except ValueError:
                continue
        
        # Новый товар получает следующий order
        next_order = max_order + 1
        
        # Создаем товар
        product = {
            'id': product_id,
            'title': self.form_vars['title_var'].get().strip(),
            'price': price,
            'desc': self.form_vars['desc_var'].get().strip(),
            'meta': self.form_vars['meta_var'].get().strip(),
            'link': link,
            'status': self.status_var.get(),
            'section': section,
            'order': str(next_order),
            'images': [],
            'updated': datetime.now().isoformat()
        }
        
        # Добавляем изображения из списка
        images_list = []
        for i in range(self.images_listbox.size()):
            image_path = self.images_listbox.get(i)
            if image_path.strip():
                # Если путь уже содержит product_id, используем его как есть
                if image_path.startswith(f"{product_id}/"):
                    images_list.append(image_path.strip())
                else:
                    # Иначе добавляем product_id к пути
                    images_list.append(f"{product_id}/{image_path.strip()}")
        
        # Добавляем товар
        self.products.append(product)
        
        # Обрабатываем изображения если они есть
        if images_list:
            try:
                # Создаем папку для товара
                product_folder = os.path.join(self.web_dir, 'img', f'product_{product_id}')
                os.makedirs(product_folder, exist_ok=True)
                
                processed_images = []
                
                # Копируем и переименовываем изображения
                for i, image_path in enumerate(images_list, 1):
                    # Получаем оригинальный путь к файлу
                    original_path = None
                    
                    if hasattr(self, 'selected_images_folder') and self.selected_images_folder:
                        # Если изображения из папки
                        original_filename = os.path.basename(image_path)
                        original_path = os.path.join(self.selected_images_folder, original_filename)
                    elif hasattr(self, 'original_image_paths') and image_path in self.original_image_paths:
                        # Если изображения добавлены по одному
                        original_path = self.original_image_paths[image_path]
                    elif hasattr(self, 'original_image_paths'):
                        # Ищем по базовому имени файла
                        base_name = os.path.basename(image_path)
                        for stored_path, original_path in self.original_image_paths.items():
                            if os.path.basename(stored_path) == base_name:
                                break
                        else:
                            original_path = None
                    elif os.path.exists(image_path):
                        # Если путь уже правильный
                        original_path = image_path
                    else:
                        original_path = None
                    
                    if original_path and os.path.exists(original_path):
                        # Новое имя файла
                        new_filename = f'product_{product_id}_{i}.jpg'
                        new_path = os.path.join(product_folder, new_filename)
                        
                        # Копируем файл
                        shutil.copy2(original_path, new_path)
                        print(f"📸 Скопировано: {os.path.basename(original_path)} → {new_filename}")
                        
                        # Добавляем правильный путь к списку
                        processed_images.append(f'product_{product_id}/{new_filename}')
                    else:
                        print(f"⚠️ Файл не найден: {image_path}")
                
                if processed_images:
                    # Обновляем пути к изображениям в товаре
                    product['images'] = ','.join(processed_images)
                    print(f"✅ Изображения обработаны для товара {product_id}")
                else:
                    product['images'] = ''
                    print(f"⚠️ Не удалось обработать изображения для товара {product_id}")
                
                # Очищаем сохраненные пути
                if hasattr(self, 'original_image_paths'):
                    self.original_image_paths.clear()
                    
            except Exception as e:
                print(f"❌ Ошибка обработки изображений: {e}")
                product['images'] = ''
        else:
            product['images'] = ''
        
        self.save_products()
        
        self.refresh_products_list()
        
        # Очищаем форму
        self.clear_form()
        
        messagebox.showinfo("Успех", f"Товар '{product['title']}' добавлен!")
    
    def clear_form(self):
        """Очистить форму"""
        for var_name, var in self.form_vars.items():
            if var_name == 'product_id_var':
                # Генерируем следующий ID
                max_id = 0
                for p in self.products:
                    try:
                        p_id = int(p.get('id', '0'))
                        max_id = max(max_id, p_id)
                    except ValueError:
                        continue
                next_id = str(max_id + 1)
                var.set(next_id)
            else:
                var.set('')
        self.status_var.set('preorder')
        self.section_var.set('home')
        self.clear_images()
    
    def update_app_js(self):
        """Обновить app.min.js с новыми данными"""
        if not os.path.exists(self.web_dir):
            messagebox.showerror("Ошибка", f"Папка {self.web_dir} не найдена!")
            return
        
        app_js_path = os.path.join(self.web_dir, "app.min.js")
        if not os.path.exists(app_js_path):
            messagebox.showerror("Ошибка", f"Файл {app_js_path} не найден!")
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
                
                # Записываем новый файл
                with open(app_js_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                messagebox.showinfo("Успех", f"app.min.js обновлен с {len(self.products)} товарами!")
            else:
                messagebox.showerror("Ошибка", "Не удалось найти массив товаров в app.min.js")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка обновления app.min.js: {e}")
    
    def update_data_local(self):
        """Обновление данных только локально (без деплоя)"""
        try:
            # Копируем products.json в web_combined_working
            if os.path.exists(self.products_file):
                web_products_file = os.path.join(self.web_dir, 'products.json')
                shutil.copy2(self.products_file, web_products_file)
                print(f"✅ {self.products_file} скопирован в {self.web_dir}")
            else:
                messagebox.showwarning("Предупреждение", f"Файл {self.products_file} не найден")
                return
            
            # Копируем изображения
            if os.path.exists(self.images_dir):
                web_img_dir = os.path.join(self.web_dir, 'img')
                if os.path.exists(web_img_dir):
                    shutil.rmtree(web_img_dir)
                shutil.copytree(self.images_dir, web_img_dir)
                print(f"✅ Изображения скопированы в {self.web_dir}")
            else:
                messagebox.showwarning("Предупреждение", f"Папка {self.images_dir} не найдена")
            
            # Обновляем app.min.js
            js_updated = False
            
            # Правильный путь к скрипту обновления
            update_script = os.path.join(self.web_dir, 'update_data_only.py')
            
            if os.path.exists(update_script):
                print(f"🔄 Запуск скрипта обновления: {update_script}")
                result = subprocess.run(['python3', update_script], 
                                      capture_output=True, text=True, cwd=self.web_dir)
                
                if result.returncode == 0:
                    print("✅ app.min.js обновлен")
                    js_updated = True
                else:
                    print(f"⚠️ Ошибка скрипта: {result.stderr}")
            else:
                print(f"⚠️ Скрипт не найден: {update_script}")
            
            if not js_updated:
                messagebox.showwarning("Предупреждение", "Не удалось обновить app.min.js")
                return
            
            messagebox.showinfo("Успех", 
                              "✅ Данные обновлены локально!\n\n"
                              "✅ products.json скопирован\n"
                              "✅ Изображения обновлены\n"
                              "✅ app.min.js обновлен\n\n"
                              "Для публикации на сайте используйте кнопку '🚀 Обновить + Деплой'")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка обновления данных: {e}")

    def update_data(self):
        """Обновление данных с автоматическим деплоем на GitHub"""
        try:
            # Сначала обновляем данные локально
            self.update_data_local()
            
            # Автоматический деплой на GitHub
            print("🚀 Запуск автоматического деплоя на GitHub...")
            
            # Проверяем наличие файла github_deploy.py
            if os.path.exists('github_deploy.py'):
                # Импортируем GitHub деплоер
                from github_deploy import GitHubDeployer
                
                # Создаем экземпляр деплоера
                deployer = GitHubDeployer()
                
                # Запускаем деплой
                success = deployer.deploy(auto_commit=True, open_desktop=False)
                
                if success:
                    messagebox.showinfo("Успех", 
                                      "🎉 Обновление и деплой завершены успешно!\n\n"
                                      "✅ Данные обновлены\n"
                                      "✅ app.min.js обновлен\n"
                                      "✅ Изменения отправлены на GitHub\n\n"
                                      "Сайт должен обновиться автоматически в ближайшее время.")
                else:
                    messagebox.showerror("Ошибка", 
                                       "❌ Деплой на GitHub не удался.\n\n"
                                       "Данные обновлены локально, но не отправлены на сервер.\n"
                                       "Проверьте отчет для деталей.")
            else:
                messagebox.showinfo("Информация", 
                                  "✅ Данные обновлены локально\n\n"
                                  "Файл github_deploy.py не найден.\n"
                                  "Деплой на GitHub не выполнен.")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка обновления данных: {e}")
    
    def show_preview_window(self):
        """Показать окно предварительного просмотра"""
        if not os.path.exists(self.web_dir):
            messagebox.showerror("Ошибка", f"Папка {self.web_dir} не найдена!")
            return
        
        # Запускаем локальный сервер
        try:
            # Останавливаем предыдущий сервер, если он запущен
            if self.web_server:
                self.web_server.terminate()
                self.web_server = None
            
            # Запускаем новый сервер
            self.web_server = subprocess.Popen(['python3', '-m', 'http.server', '8005'], 
                                             cwd=self.web_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Открываем браузер
            import webbrowser
            webbrowser.open('http://localhost:8005')
            
            messagebox.showinfo("Просмотр", 
                              "🌐 Локальный сервер запущен!\n\n"
                              "Сайт открыт в браузере по адресу:\n"
                              "http://localhost:8005\n\n"
                              "Для остановки сервера закройте это окно.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось запустить сервер: {e}")
    
    def toggle_server(self):
        """Переключить локальный сервер"""
        if self.web_server is None:
            # Запускаем сервер
            try:
                port = self.server_port_var.get()
                self.web_server = subprocess.Popen(['python3', '-m', 'http.server', port], 
                                                 cwd=self.web_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self.server_button.configure(text="🛑 Остановить сервер")
                self.status_label.configure(text=f"Сервер запущен на порту {port}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось запустить сервер: {e}")
        else:
            # Останавливаем сервер
            self.web_server.terminate()
            self.web_server = None
            self.server_button.configure(text="🚀 Запустить сервер")
            self.status_label.configure(text="Сервер остановлен")
    
    def create_deploy_package(self):
        """Создать пакет для деплоя (устаревшая функция)"""
        messagebox.showinfo("Информация", 
                          "📦 Создание ZIP пакета больше не требуется.\n\n"
                          "Используйте кнопку '🐙 GitHub Pages' для прямого деплоя на GitHub Pages.\n\n"
                          "Это быстрее и удобнее!")
    
    def github_deploy(self):
        """Деплой на GitHub Pages"""
        try:
            # Проверяем наличие файла github_deploy.py
            if os.path.exists('github_deploy.py'):
                # Импортируем GitHub деплоер
                from github_deploy import GitHubDeployer
                
                # Создаем экземпляр деплоера
                deployer = GitHubDeployer()
                
                # Запускаем деплой
                success = deployer.deploy(auto_commit=True, open_desktop=False)
                
                if success:
                    messagebox.showinfo("Успех", 
                                      "🎉 GitHub деплой завершен успешно!\n\n"
                                      "Сайт должен обновиться автоматически в ближайшее время.")
                else:
                    messagebox.showerror("Ошибка", 
                                       "❌ GitHub деплой не удался.\n\n"
                                       "Проверьте отчет для деталей.")
            else:
                messagebox.showerror("Ошибка", "Файл github_deploy.py не найден")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Неожиданная ошибка при GitHub деплое:\n{e}")
    
    def manage_images(self):
        """Управление изображениями"""
        messagebox.showinfo("Изображения", 
                          "🖼️ Управление изображениями\n\n"
                          "Для управления изображениями товара:\n"
                          "1. Выберите товар в списке\n"
                          "2. Нажмите '✏️ Редактировать'\n"
                          "3. В диалоге редактирования используйте кнопки:\n"
                          "   • ➕ Добавить - добавить новое изображение\n"
                          "   • 🗑️ Удалить - удалить выбранное изображение\n"
                          "   • ⬆️ Вверх / ⬇️ Вниз - изменить порядок")

def main():
    root = tk.Tk()
    
    # Настройка стилей
    style = ttk.Style()
    style.theme_use('clam')
    
    # Создаем стиль для акцентных кнопок
    style.configure('Accent.TButton', 
                   background='#007bff', 
                   foreground='white',
                   font=('Arial', 11))
    
    # Создаем приложение
    app = PlatformaManagerModern(root)
    
    # Запускаем главный цикл
    root.mainloop()

if __name__ == "__main__":
    main()
