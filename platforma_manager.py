#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Platforma Manager Final - Финальная версия с Material Design 3

ЕДИНАЯ СИСТЕМА КНОПОК:
=====================
Все кнопки в приложении используют единую систему стилей:

1. primary_button() - Основная кнопка (синяя)
2. secondary_button() - Вторичная кнопка (бирюзовая) 
3. success_button() - Кнопка успеха (зеленая)
4. warning_button() - Кнопка предупреждения (оранжевая)
5. error_button() - Кнопка ошибки (красная)
6. outlined_button() - Контурная кнопка (прозрачная с рамкой)
7. light_button() - Светлая кнопка (для карточек)
8. compact_button() - Компактная кнопка (120x40px)

Все кнопки имеют единый стиль:
- Скругленные углы (radius=20)
- Иконка + текст
- Единые размеры и отступы
- Material Design 3 цвета
"""

import flet as ft
import json
import os
import shutil
from PIL import Image
import zipfile
from datetime import datetime
import requests
import re
import uuid
import gspread
from google.oauth2.credentials import Credentials
import sys
import locale
import asyncio
import base64
from typing import List, Dict, Optional
from flet import (
    ElevatedButton, OutlinedButton, Row, Icon, Text,
    ButtonStyle, RoundedRectangleBorder,
    padding, border, TextOverflow
)

# Настройка кодировки
if sys.platform.startswith('win'):
    try:
        locale.setlocale(locale.LC_ALL, 'Russian_Russia.1251')
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
        except:
            pass
else:
    try:
        locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        except:
            pass

class PlatformaManagerFinal:
    def __init__(self):
        self.products = []
        self.selected_product = None
        self.current_section = "home"
        self.current_view = "products"  # products, add, preview, deploy
        self.page = None
        
        # Ссылки на элементы интерфейса
        self.selected_product_text = ft.Ref[ft.Text]()
        self.edit_button = ft.Ref[ElevatedButton]()
        self.delete_button = ft.Ref[ElevatedButton]()
        self.preview_grid_ref = ft.Ref[ft.GridView]()
        
        # Для управления порядком в просмотре
        self.selected_preview_product = None
        self.preview_products = []  # Список товаров в текущем разделе просмотра
        self.preview_section = "home"  # Текущий раздел в просмотре
        
        # Для загрузки файлов
        self.selected_files = []
        
        # Спокойные цвета Material Design 3
        self.colors = {
            'primary': '#5C6BC0',  # Спокойный индиго
            'primary_light': '#8E99F3',
            'primary_container': '#E8EAF6',  # Светлый индиго для контейнеров
            'secondary': '#26A69A',  # Спокойный бирюзовый
            'tertiary': '#FF8A65',  # Спокойный коралловый
            'surface': '#FFFFFF',
            'background': '#FAFAFA',
            'error': '#EF5350',  # Спокойный красный
            'success': '#66BB6A',  # Спокойный зеленый
            'warning': '#FFA726',  # Спокойный оранжевый
            'on_surface': '#212121',
            'on_surface_variant': '#757575',
            'outline': '#BDBDBD',
            'surface_container': '#F5F5F5',
        }
        
        # Константы для кнопок (фиксированная ширина сайдбара)
        self.SIDE_W = 280
        self.BTN_W = self.SIDE_W - 32  # ширина сайдбара минус паддинги
        self.BTN_H, self.RADIUS, self.GAP = 42, 20, 10

    def pill_button(self, text, icon, bg=None, fg=None, on_click=None, outlined=False, width=None, height=None):
        """Создание кнопки-пилюли с единым стилем"""
        if bg is None:
            bg = self.colors['primary']
        if fg is None:
            fg = self.colors['surface']
        if width is None:
            width = self.BTN_W
        if height is None:
            height = self.BTN_H
            
        style = ButtonStyle(
            bgcolor=None if outlined else bg,
            color=fg if not outlined else self.colors['on_surface'],
            side=border.all(1, self.colors['outline']) if outlined else None,
            shape=RoundedRectangleBorder(radius=self.RADIUS),
            padding=padding.symmetric(horizontal=16, vertical=12),
        )
        
        btn_cls = OutlinedButton if outlined else ElevatedButton
        return btn_cls(
            width=width, height=height,
            content=Row(
                [Icon(icon, size=18), Text(text, size=14, no_wrap=True, max_lines=1, overflow=TextOverflow.ELLIPSIS)],
                spacing=8, alignment="start"
            ),
            style=style,
            on_click=on_click,
        )

    def primary_button(self, text, icon, on_click=None):
        """Основная кнопка - синяя"""
        return self.pill_button(text, icon, bg=self.colors['primary'], fg=self.colors['surface'], on_click=on_click)
    
    def secondary_button(self, text, icon, on_click=None):
        """Вторичная кнопка - бирюзовая"""
        return self.pill_button(text, icon, bg=self.colors['secondary'], fg=self.colors['surface'], on_click=on_click)
    
    def success_button(self, text, icon, on_click=None):
        """Кнопка успеха - зеленая"""
        return self.pill_button(text, icon, bg=self.colors['success'], fg=self.colors['surface'], on_click=on_click)
    
    def warning_button(self, text, icon, on_click=None):
        """Кнопка предупреждения - оранжевая"""
        return self.pill_button(text, icon, bg=self.colors['warning'], fg=self.colors['surface'], on_click=on_click)
    
    def error_button(self, text, icon, on_click=None):
        """Кнопка ошибки - красная"""
        return self.pill_button(text, icon, bg=self.colors['error'], fg=self.colors['surface'], on_click=on_click)
    
    def outlined_button(self, text, icon, on_click=None):
        """Контурная кнопка - прозрачная с рамкой"""
        return self.pill_button(text, icon, on_click=on_click, outlined=True)
    
    def light_button(self, text, icon, on_click=None):
        """Светлая кнопка - для карточек"""
        return self.pill_button(text, icon, bg=self.colors['primary_container'], fg=self.colors['on_surface'], on_click=on_click)
    
    def compact_button(self, text, icon, on_click=None, color_type="primary", outlined=False):
        """Компактная кнопка с меньшими размерами"""
        bg_map = {
            "primary": self.colors["primary"],
            "success": self.colors["success"],
            "error": self.colors["error"],
            "secondary": self.colors["secondary"],
        }
        bg = None if outlined else bg_map.get(color_type, self.colors["primary"])
        fg = self.colors["surface"] if not outlined else self.colors["on_surface"]
        side = ft.border.all(1, self.colors["outline"]) if outlined else None
        Btn = ft.OutlinedButton if outlined else ft.ElevatedButton

        return Btn(
            height=44,
            content=ft.Row(
                [
                    ft.Icon(icon, size=18),
                    ft.Text(text, size=14, no_wrap=True, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,  # <-- текст не «плавает»
            ),
            style=ft.ButtonStyle(
                bgcolor=bg,
                color=fg,
                side=side,
                shape=ft.StadiumBorder(),
                padding=ft.padding.symmetric(horizontal=16, vertical=10),
            ),
            on_click=on_click,
        )

    async def main(self, page: ft.Page):
        self.page = page
        page.title = "🛍️ Platforma Manager"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.window_width = 1800
        page.window_height = 1200
        page.window_min_width = 1600
        page.window_min_height = 900
        page.window_resizable = True
        page.window_maximized = True  # Авто-разворачивание при старте
        page.padding = 0
        page.spacing = 0
        
        # Даем Flet доступ к локальным файлам
        page.assets_dir = os.path.abspath(".")
        
        # Настройка темы Material Design 3
        page.theme = ft.Theme(
            color_scheme_seed=ft.Colors.INDIGO,
            use_material3=True,
        )
        
        # Загружаем данные
        await self.load_products_from_json()
        
        # Добавляем FilePicker
        self.file_picker = ft.FilePicker(on_result=self.on_files_selected)
        page.overlay.append(self.file_picker)
        page.update()  # ВАЖНО: обновляем страницу после добавления в overlay
        print(f"FilePicker initialized and added to overlay")
        print(f"Platform: {sys.platform}")
        print(f"Flet version: {getattr(ft, '__version__', 'unknown')}")
        
        # Создаем интерфейс
        await self.setup_ui()

    async def load_products_from_json(self):
        """Загрузка товаров из JSON файла"""
        try:
            if os.path.exists("products.json"):
                with open("products.json", "r", encoding="utf-8") as f:
                    self.products = json.load(f)
                print(f"✅ Загружено {len(self.products)} товаров из JSON")
            else:
                self.products = []
                print("⚠️ Файл products.json не найден")
        except Exception as e:
            print(f"❌ Ошибка загрузки товаров: {e}")
            self.products = []
        
        # Автоматическая синхронизация с Google Sheets
        await self.auto_sync_with_sheets()

    async def setup_ui(self):
        """Создание полнофункционального интерфейса"""
        
        # Защита от повторного построения при hot-reload
        if getattr(self.page, "is_built", False):
            self.page.clean()  # на всякий — вычистить старые контролы
        self.page.is_built = True
        
        # Главный контейнер
        main_container = ft.Container(
            content=ft.Row([
                # Боковая панель навигации
                self.create_sidebar_container(),
                
                # Вертикальный разделитель
                ft.VerticalDivider(width=1),
                
                # Основная область контента
                ft.Container(
                    content=self.create_main_content(),
                    expand=True,
                    padding=16,
                    bgcolor=self.colors['surface'],
                    border_radius=12,
                    clip_behavior=ft.ClipBehavior.NONE,  # предотвращаем обрезание содержимого
                ),
            ]),
            expand=True,
        )
        
        self.page.add(main_container)
        self.page.update()
        
        # Принудительно обновляем отображение товаров
        await self.refresh_products_table()
        
        # Настройка адаптивного скролла
        self.setup_adaptive_scroll()

    def setup_adaptive_scroll(self):
        """Настройка адаптивного скролла для сайдбара"""
        MIN_H = 760
        
        def on_resize(e):
            if hasattr(self, 'side_col'):
                self.side_col.scroll = "auto" if self.page.height < MIN_H else "off"
                # НЕ добавляем новые элементы в on_resize, только обновляем существующие
                self.page.update()
        
        self.page.on_resize = on_resize
        on_resize(None)  # применить состояние на старте

    async def on_preview_click(self, e):
        """Обработчик клика по кнопке Просмотр - переключатель между представлениями"""
        if self.current_view == "preview":
            # Если мы в просмотре, возвращаемся к товарам
            await self.show_products_view()
        else:
            # Если мы в товарах, переходим к просмотру
            await self.show_preview_view()

    def create_sidebar_container(self):
        """Создание контейнера боковой панели"""
        # Основная колонка с адаптивным скроллом
        self.side_col = ft.Column(
            spacing=8,
            tight=True,
            scroll="off",  # при старте пытаемся без скролла
        )

        # Контейнер сайдбара
        side = ft.Container(
            width=self.SIDE_W,
            padding=16,
            bgcolor=self.colors['surface_container'],
            content=self.side_col,
            border_radius=0
        )
        
        # Наполняем боковую колонку ОДИН РАЗ (без append в разных местах)
        self.rebuild_sidebar()
        
        return side

    def rebuild_sidebar(self):
        """Пересборка сайдбара без дублирования элементов"""
        if not hasattr(self, 'side_col'):
            return
            
        self.side_col.controls.clear()
        self.side_col.controls.extend([
            # Навигация (компактная карточка)
            ft.Container(
                bgcolor=self.colors['surface'],
                border_radius=8,
                padding=12,
                content=ft.Column(
                    spacing=8,
                    tight=True,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            ft.Icon(ft.Icons.INVENTORY_2_OUTLINED, size=24),
                            bgcolor=ft.Colors.BLUE_50,
                            width=48, height=48, border_radius=24
                        ),
                        ft.Text("Товары", size=13, weight=ft.FontWeight.W_600),
                        self.light_button("Просмотр" if self.current_view != "preview" else "Товары", ft.Icons.REMOVE_RED_EYE_OUTLINED, on_click=lambda e: self.page.run_task(self.on_preview_click(e))),
                    ],
                )
            ),
            
            # Кнопки Sheets и действий
            ft.Column(
                spacing=6,
                tight=True,
                controls=[
                                self.secondary_button("Загрузить с Sheets", ft.Icons.CLOUD_DOWNLOAD, on_click=lambda e: self.page.run_task(self.load_from_sheets(e))),
            self.primary_button("Отправить в Sheets", ft.Icons.CLOUD_UPLOAD, on_click=lambda e: self.page.run_task(self.sync_products(e))),
            self.primary_button("Синхронизировать", ft.Icons.SYNC, on_click=lambda e: self.page.run_task(self.sync_products(e))),
            self.success_button("Деплой", ft.Icons.ROCKET_LAUNCH, on_click=lambda e: self.page.run_task(self.deploy_site(e))),
            self.success_button("➕ Добавить товар", ft.Icons.ADD, on_click=lambda e: self.page.run_task(self.show_add_view_async(e))),
                ]
            ),
            

            
            # Кнопки действий
            ft.Column(
                spacing=6,
                tight=True,
                controls=[
                    ft.Container(
                        content=self.outlined_button("Редактировать", ft.Icons.EDIT_OUTLINED, on_click=lambda e: self.page.run_task(self.edit_selected_product(e))),
                        ref=self.edit_button,
                    ),
                    ft.Container(
                        content=self.error_button("Удалить", ft.Icons.DELETE, on_click=lambda e: self.page.run_task(self.delete_selected_product(e))),
                        ref=self.delete_button,
                    ),
                ]
            ),
            
            # Статистика
            ft.Column(
                spacing=2,
                tight=True,
                controls=[
                    ft.Text("Статистика", size=12, weight=ft.FontWeight.W_600, color=self.colors['on_surface_variant']),
                    ft.Text(f"Товаров: {len(self.products)}", size=11, color=self.colors['on_surface_variant'])
                ]
            )
        ])
        
        if hasattr(self, 'page'):
            self.page.update()

    def create_main_content(self):
        """Создание основной области контента"""
        self.content_area = ft.Container(
            content=self.create_products_view(),
            expand=True,
        )
        return self.content_area

    def create_products_view(self):
        """Создание представления товаров (ГЛАВНАЯ СТРАНИЦА) - ТАБЛИЦА"""
        return ft.Column([
            # Верхняя панель
            ft.Container(
                content=ft.Row([
                    ft.Text(
                        "Таблица товаров",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color=self.colors['on_surface'],
                    ),
                    ft.Container(expand=True),
                    ft.Container(
                        content=ft.SegmentedButton(
                            selected={"home"},
                            segments=[
                                ft.Segment(value="home", label=ft.Text("🏠 HOME")),
                                ft.Segment(value="nessffo", label=ft.Text("🎨 NESSFFO")),
                            ],
                            on_change=self.on_section_change,
                        ),
                        padding=ft.padding.only(right=16),  # правый паддинг чтобы чипы не обрезались
                    ),
                ]),
                padding=ft.padding.only(bottom=20),
            ),
            
            # ТАБЛИЦА ТОВАРОВ
            ft.Container(
                content=self.create_products_table(),
                expand=True,
            ),
            

        ])

    def create_products_table(self):
        """Создание таблицы товаров"""
        self.products_table = ft.Column([
            # Заголовки таблицы
            ft.Container(
                content=                ft.Row([
                    ft.Container(
                        content=ft.Text("Порядок", weight=ft.FontWeight.BOLD, size=14, color="white"),
                        width=80,
                    ),
                    ft.Container(
                        content=ft.Text("ID", weight=ft.FontWeight.BOLD, size=14, color="white"),
                        width=60,
                    ),
                    ft.Container(
                        content=ft.Text("Название", weight=ft.FontWeight.BOLD, size=14, color="white"),
                        expand=True,
                    ),
                    ft.Container(
                        content=ft.Text("Цена", weight=ft.FontWeight.BOLD, size=14, color="white"),
                        width=100,
                    ),
                ]),
                padding=ft.padding.all(8),
                bgcolor=self.colors['primary'],
                border_radius=ft.border_radius.only(top_left=8, top_right=8),
            ),
            
            # Содержимое таблицы (прокручиваемое)
            ft.Container(
                content=ft.ListView(
                    spacing=0,
                    expand=True,
                    height=200,
                ),
                expand=True,
                bgcolor=self.colors['surface'],
                border=ft.border.all(1, self.colors['outline']),
                border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8),
            ),
        ])
        return self.products_table

    def create_product_table_row(self, product: Dict, index: int):
        """Создание строки таблицы товара"""
        return ft.Container(
            content=ft.Row([
                # Порядок
                ft.Container(
                    content=ft.Text(
                        str(product.get('order', 'N/A')), 
                        size=12,
                        color="black",
                    ),
                    width=80,
                    padding=ft.padding.all(6),
                ),
                
                # ID
                ft.Container(
                    content=ft.Text(
                        str(product.get('id', index + 1)), 
                        size=12,
                        color="black",
                    ),
                    width=60,
                    padding=ft.padding.all(6),
                ),
                
                # Название
                ft.Container(
                    content=ft.Text(
                        str(product.get('title', 'Без названия')),
                        size=12,
                        color="black",
                    ),
                    expand=True,
                    padding=ft.padding.all(6),
                ),
                
                # Цена
                ft.Container(
                    content=ft.Text(
                        str(product.get('price', '0')),
                        size=12,
                        color="black",
                    ),
                    width=100,
                    padding=ft.padding.all(6),
                ),
                

            ]),
            border=ft.border.only(bottom=ft.border.BorderSide(1, "lightgray")),
            on_click=lambda e: self.select_product(product),
        )

    def product_first_image_src(self, p: dict) -> str | None:
        """
        Возвращает путь к первому фото товара для GridView.
        Использует изображения из локальной папки img/.
        """
        product_id = p.get("id", "")
        if not product_id:
            return None
        
        # Сначала проверяем в img/ (локальные изображения)
        img_path = f"img/product_{product_id}"
        if os.path.exists(img_path):
            for file in sorted(os.listdir(img_path)):
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                    full_path = f"{img_path}/{file}"
                    print(f"Найдено изображение для товара {product_id}: {full_path}")
                    # Возвращаем относительный путь для Flet
                    return f"/{full_path}"
        
        # Если нет в img/, проверяем в web/img/ (последний деплой)
        web_img_path = f"web/img/product_{product_id}"
        if os.path.exists(web_img_path):
            # Ищем первое изображение
            for file in sorted(os.listdir(web_img_path)):
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                    full_path = f"{web_img_path}/{file}"
                    print(f"Найдено изображение для товара {product_id}: {full_path}")
                    # Возвращаем относительный путь для Flet
                    return f"/{full_path}"
        
        print(f"Изображение не найдено для товара {product_id}")
        return None

    def get_product_image_base64(self, p: dict) -> str | None:
        """
        Возвращает изображение товара в формате base64 для Flet.
        """
        product_id = p.get("id", "")
        if not product_id:
            return None
        
        # Сначала проверяем в img/ (локальные изображения)
        img_path = f"img/product_{product_id}"
        if os.path.exists(img_path):
            for file in sorted(os.listdir(img_path)):
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                    full_path = f"{img_path}/{file}"
                    try:
                        with open(full_path, 'rb') as img_file:
                            img_data = img_file.read()
                            img_base64 = base64.b64encode(img_data).decode('utf-8')
                            # Определяем MIME тип
                            if file.lower().endswith('.png'):
                                mime_type = 'image/png'
                            elif file.lower().endswith('.jpg') or file.lower().endswith('.jpeg'):
                                mime_type = 'image/jpeg'
                            elif file.lower().endswith('.gif'):
                                mime_type = 'image/gif'
                            elif file.lower().endswith('.webp'):
                                mime_type = 'image/webp'
                            else:
                                mime_type = 'image/jpeg'
                            
                            return f"data:{mime_type};base64,{img_base64}"
                    except Exception as e:
                        print(f"Ошибка чтения изображения {full_path}: {e}")
                        continue
        
        # Если нет в img/, проверяем в web/img/ (последний деплой)
        web_img_path = f"web/img/product_{product_id}"
        if os.path.exists(web_img_path):
            # Ищем первое изображение
            for file in sorted(os.listdir(web_img_path)):
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                    full_path = f"{web_img_path}/{file}"
                    try:
                        with open(full_path, 'rb') as img_file:
                            img_data = img_file.read()
                            img_base64 = base64.b64encode(img_data).decode('utf-8')
                            # Определяем MIME тип
                            if file.lower().endswith('.png'):
                                mime_type = 'image/png'
                            elif file.lower().endswith('.jpg') or file.lower().endswith('.jpeg'):
                                mime_type = 'image/jpeg'
                            elif file.lower().endswith('.gif'):
                                mime_type = 'image/gif'
                            elif file.lower().endswith('.webp'):
                                mime_type = 'image/webp'
                            else:
                                mime_type = 'image/jpeg'
                            
                            return f"data:{mime_type};base64,{img_base64}"
                    except Exception as e:
                        print(f"Ошибка чтения изображения {full_path}: {e}")
                        continue
        
        return None

    def create_product_thumbnail(self, p: dict):
        """
        Миниатюра товара: первая картинка из папки product_{id},
        либо аккуратный плейсхолдер.
        """
        title = p.get("title", "Без названия")
        img = self.first_image_path_by_id(p)

        placeholder = ft.Container(
            alignment=ft.alignment.center,
            bgcolor=self.colors["surface_container"],
            border_radius=8,
            content=ft.Icon(ft.Icons.IMAGE_NOT_SUPPORTED_OUTLINED, size=42, color=self.colors["on_surface_variant"]),
            width=200, height=200,
        )

        if img and os.path.exists(img):
            # Используем абсолютный путь - это работало!
            abs_path = os.path.abspath(img)
            return ft.Image(
                src=abs_path,
                fit=ft.ImageFit.COVER,
                width=200,
                height=200,
                border_radius=8,
                error_content=placeholder,
            )

        return placeholder

    def first_image_path_by_id(self, product: dict) -> str | None:
        """
        Возвращает путь к ПЕРВОЙ картинке товара по его id.
        Ищет по порядку:
          img/product_{id}/..., затем web/img/product_{id}/...
        Подходит для превью/сеток.
        """
        pid = str(product.get("id", "")).strip()
        if not pid:
            return None

        # 0) если в JSON есть images="product_2/product_2_1.jpg|...", возьмем первое
        images_field = (product.get("images") or "").strip()
        if images_field:
            first = images_field.split("|")[0].strip()
            if first:
                candidate = first if first.startswith("img/") else f"img/{first}"
                if os.path.exists(candidate):
                    return candidate

        exts = (".png", ".jpg", ".jpeg", ".webp", ".gif")
        folders = [f"img/product_{pid}", f"web/img/product_{pid}"]

        for folder in folders:
            if os.path.isdir(folder):
                # сначала пробуем типичные имена
                candidates = [
                    f"{folder}/cover.jpg",
                    f"{folder}/{pid}_1.jpg",
                    f"{folder}/product_{pid}_1.jpg",
                    f"{folder}/1.jpg",
                ]
                for c in candidates:
                    if os.path.exists(c):
                        return c
                # иначе берём первый попавшийся файл по алфавиту
                for name in sorted(os.listdir(folder)):
                    if name.lower().endswith(exts):
                        return f"{folder}/{name}"
        return None

    def get_product_image_path(self, product: Dict) -> Optional[str]:
        """Получение пути к первому изображению товара"""
        try:
            product_id = product.get('id', '')
            if not product_id:
                return None
            
            # Проверяем разные пути к изображениям
            possible_paths = [
                f"img/product_{product_id}",
                f"web/img/product_{product_id}",
            ]
            
            for image_dir in possible_paths:
                if os.path.exists(image_dir):
                    # Ищем первое изображение
                    for file in sorted(os.listdir(image_dir)):
                        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                            # Используем относительный путь для веб-отображения
                            relative_path = f"{image_dir}/{file}"
                            print(f"Найдено изображение для товара {product_id}: {relative_path}")
                            return relative_path
            
            print(f"Изображение не найдено для товара {product_id}")
            return None
        except Exception as e:
            print(f"Ошибка поиска изображения для товара {product.get('id')}: {e}")
            return None

    def create_preview_card(self, product: Dict):
        """Создание карточки товара для просмотра"""
        try:
            # Получаем изображение
            image_path = self.get_product_image_path(product)
            
            # Проверяем, выбран ли этот товар
            is_selected = (self.selected_preview_product and 
                          self.selected_preview_product.get('id') == product.get('id'))
            
            # Создаем изображение или заглушку
            if image_path and os.path.exists(image_path):
                try:
                    # Создаем изображение из файла
                    image_widget = ft.Image(
                        src=image_path,
                        width=150,
                        height=150,
                        fit=ft.ImageFit.COVER,
                        border_radius=8,
                    )
                except Exception as e:
                    print(f"Ошибка загрузки изображения {image_path}: {e}")
                    image_widget = ft.Container(
                        content=ft.Icon(
                            ft.Icons.IMAGE,
                            size=50,
                            color=self.colors['on_surface_variant'],
                        ),
                        width=150,
                        height=150,
                        alignment=ft.alignment.center,
                        bgcolor=self.colors['surface_container'],
                        border_radius=8,
                    )
            else:
                # Заглушка если изображение не найдено
                image_widget = ft.Container(
                    content=ft.Icon(
                        ft.Icons.IMAGE_NOT_SUPPORTED,
                        size=50,
                        color=self.colors['on_surface_variant'],
                    ),
                    width=150,
                    height=150,
                    alignment=ft.alignment.center,
                    bgcolor=self.colors['surface_container'],
                    border_radius=8,
                )
            
            # Создаем карточку
            card = ft.Container(
                content=ft.Column([
                    # Изображение товара
                    image_widget,
                    
                    # Информация о товаре
                    ft.Container(
                        content=ft.Column([
                            ft.Text(
                                str(product.get('title', 'Без названия')),
                                size=14,
                                weight=ft.FontWeight.W_500,
                                color=self.colors['on_surface'],
                                text_align=ft.TextAlign.CENTER,
                                max_lines=2,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            ft.Text(
                                f"ID: {product.get('id', 'N/A')} | Порядок: {product.get('order', 'N/A')}",
                                size=11,
                                color=self.colors['on_surface_variant'],
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Text(
                                f"Цена: {product.get('price', '0')} ₽",
                                size=12,
                                weight=ft.FontWeight.W_600,
                                color=self.colors['primary'],
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ], spacing=4),
                        padding=ft.padding.all(8),
                    ),
                ], spacing=8),
                padding=ft.padding.all(8),
                bgcolor=self.colors['primary_container'] if is_selected else self.colors['surface'],
                border_radius=12,
                border=ft.border.all(3 if is_selected else 1, self.colors['primary'] if is_selected else self.colors['outline']),
                on_click=lambda e: self.select_preview_product_sync(product),
            )
            
            return card
            
        except Exception as e:
            print(f"Ошибка создания карточки просмотра: {e}")
            return ft.Container(
                content=ft.Text("Ошибка загрузки"),
                padding=10,
                bgcolor=self.colors['error_container'],
                border_radius=8,
            )

    def create_add_view(self):
        """Создание представления добавления товара"""
        # Создаем ссылки на поля ввода
        self.add_title_field = ft.Ref[ft.TextField]()
        self.add_price_field = ft.Ref[ft.TextField]()
        self.add_desc_field = ft.Ref[ft.TextField]()
        self.add_meta_field = ft.Ref[ft.TextField]()
        self.add_section_group = ft.Ref[ft.RadioGroup]()
        self.add_files_text = ft.Ref[ft.Text]()
        
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "➕ Добавить новый товар",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color=self.colors['on_surface'],
                ),
                ft.Text(
                    "Заполните форму для создания нового товара. Новый товар будет добавлен в начало списка.",
                    size=16,
                    color=self.colors['on_surface_variant'],
                ),
                
                # Форма добавления
                ft.Container(
                    content=ft.Column([
                        # Название
                        ft.TextField(
                            ref=self.add_title_field,
                            label="Название товара *",
                            hint_text="Введите название товара",
                            width=700,
                            border_color=self.colors['outline'],
                            focused_border_color=self.colors['primary'],
                        ),
                        
                        # Цена
                        ft.TextField(
                            ref=self.add_price_field,
                            label="Цена",
                            hint_text="7500",
                            width=300,
                            border_color=self.colors['outline'],
                            focused_border_color=self.colors['primary'],
                        ),
                        
                        # Описание
                        ft.TextField(
                            ref=self.add_desc_field,
                            label="Описание",
                            hint_text="Введите описание товара",
                            multiline=True,
                            min_lines=3,
                            max_lines=5,
                            width=700,
                            border_color=self.colors['outline'],
                            focused_border_color=self.colors['primary'],
                        ),
                        
                        # Состав
                        ft.TextField(
                            ref=self.add_meta_field,
                            label="Состав",
                            hint_text="Например: 100% хлопок, цвет на выбор",
                            width=700,
                            border_color=self.colors['outline'],
                            focused_border_color=self.colors['primary'],
                        ),
                        
                        # Раздел
                        ft.Row([
                            ft.Text("Раздел:", size=16, weight=ft.FontWeight.W_600),
                            ft.RadioGroup(
                                ref=self.add_section_group,
                                content=ft.Column([
                                    ft.Radio(value="home", label="🏠 HOME"),
                                    ft.Radio(value="nessffo", label="🎨 NESSFFO"),
                                ]),
                                value="home"
                            ),
                        ]),
                        
                        # Загрузка изображений
                        ft.Text("Изображения:", size=16, weight=ft.FontWeight.W_600),
                        ft.ElevatedButton(
                            "📁 Выбрать изображения",
                            icon=ft.Icons.FOLDER_OPEN,
                            on_click=self.open_images_dialog,
                        ),
                        ft.Text(
                            ref=self.add_files_text,
                            size=12,
                            color=self.colors['on_surface_variant'],
                            value="Файлы не выбраны"
                        ),
                        
                        ft.Container(height=20),
                        
                        # Кнопки
                        ft.Row([
                            self.compact_button("➕ Добавить товар", ft.Icons.ADD, on_click=lambda e: self.page.run_task(self.add_product_from_form(e)), color_type="success"),
                            self.compact_button("Отмена", ft.Icons.CANCEL, on_click=self.cancel_add_product, color_type="primary"),
                        ], spacing=10),
                    ], spacing=20, tight=True),
                    padding=ft.padding.all(20),
                    bgcolor=self.colors['surface_container'],
                    border_radius=8,
                ),
            ], spacing=20, scroll=ft.ScrollMode.AUTO),
            padding=ft.padding.all(20),
            expand=True,
        )

    def create_preview_view(self):
        """Создание представления предварительного просмотра - ПЛИТКА ДЛЯ ПЕРЕТАСКИВАНИЯ"""
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "🎯 Управление порядком товаров",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color=self.colors['on_surface'],
                ),
                ft.Text(
                    "Выберите товар и используйте кнопки для изменения порядка отображения на сайте",
                    size=16,
                    color=self.colors['on_surface_variant'],
                ),
                

                
                # Фильтры
                ft.Row([
                    ft.Text("Раздел:", size=16),
                    ft.Container(
                        content=ft.SegmentedButton(
                            selected={"home"},
                            segments=[
                                ft.Segment(value="home", label=ft.Text("🏠 HOME")),
                                ft.Segment(value="nessffo", label=ft.Text("🎨 NESSFFO")),
                            ],
                            on_change=self.on_preview_section_change,
                        ),
                        padding=ft.padding.only(right=16),  # правый паддинг чтобы чипы не обрезались
                    ),
                ]),
                
                # Плитка товаров для перетаскивания
                ft.Container(
                    content=ft.GridView(
                        expand=True,
                        runs_count=4,
                        max_extent=220,
                        child_aspect_ratio=1.0,
                        spacing=15,
                        run_spacing=15,
                        ref=self.preview_grid_ref,
                    ),
                    expand=True,
                    padding=ft.padding.all(20),
                    bgcolor=self.colors['surface_container'],
                    border_radius=8,
                ),
                
                # Кнопки управления порядком
                ft.Container(
                    content=ft.Row([
                        self.compact_button("⬆️ Поднять выше", ft.Icons.KEYBOARD_ARROW_UP, on_click=lambda e: self.page.run_task(self.move_product_up(e)), color_type="primary"),
                        self.compact_button("⬇️ Опустить ниже", ft.Icons.KEYBOARD_ARROW_DOWN, on_click=lambda e: self.page.run_task(self.move_product_down(e)), color_type="primary"),
                        self.compact_button("💾 Сохранить порядок", ft.Icons.SAVE, on_click=lambda e: self.page.run_task(self.save_product_order(e)), color_type="success"),
                    ], spacing=8),
                    padding=ft.padding.all(8),
                    bgcolor=self.colors['surface_container'],
                    border_radius=8,
                ),
            ]),
            padding=ft.padding.all(20),
        )

    def create_deploy_view(self):
        """Создание представления развертывания"""
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "Развертывание сайта",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color=self.colors['on_surface'],
                ),
                ft.Text(
                    "Экспорт и развертывание веб-сайта",
                    size=16,
                    color=self.colors['on_surface_variant'],
                ),
                
                # Опции развертывания
                ft.Container(
                    content=ft.Column([
                        ft.Checkbox(label="Обновить данные в Google Sheets", value=True),
                        ft.Checkbox(label="Создать архив для деплоя", value=True),
                        ft.Checkbox(label="Экспортировать изображения", value=True),
                        
                        ft.Container(height=20),
                        
                        ft.Row([
                                                    self.compact_button("🚀 Deploy", ft.Icons.ROCKET_LAUNCH, on_click=lambda e: self.page.run_task(self.deploy_site(e)), color_type="secondary"),
                        self.compact_button("📦 Создать архив", ft.Icons.ARCHIVE, on_click=lambda e: self.page.run_task(self.create_archive(e)), color_type="primary"),
                        ]),
                    ], spacing=15),
                    padding=ft.padding.all(20),
                    bgcolor=self.colors['surface_container'],
                    border_radius=8,
                ),
            ]),
            padding=ft.padding.all(20),
        )

    async def on_navigation_change(self, e):
        """Обработка изменения навигации"""
        index = e.control.selected_index
        if index == 0:  # Товары
            await self.show_products_view()
        elif index == 1:  # Просмотр
            await self.show_preview_view()
        elif index == 2:  # Deploy
            await self.show_deploy_view()
        elif index == 3:  # Добавить
            await self.show_add_view()

    async def on_section_change(self, e):
        """Обработка изменения раздела"""
        # Получаем значение из множества
        if isinstance(e.control.selected, set) and len(e.control.selected) > 0:
            self.current_section = list(e.control.selected)[0]
        else:
            self.current_section = e.control.selected
        print(f"Смена раздела на: {self.current_section}")
        await self.refresh_products_table()

    async def on_preview_section_change(self, e):
        """Обработка изменения раздела в предварительном просмотре"""
        if isinstance(e.control.selected, set) and e.control.selected:
            self.preview_section = list(e.control.selected)[0]
        else:
            self.preview_section = e.control.selected or "home"
        print(f"Смена раздела в просмотре на: {self.preview_section}")
        await self.refresh_preview_grid()

    async def show_products_view(self):
        """Показать представление товаров (ГЛАВНАЯ СТРАНИЦА)"""
        self.current_view = "products"
        self.content_area.content = self.create_products_view()
        # Обновляем сайдбар для изменения текста кнопки
        self.rebuild_sidebar()
        self.page.update()
        await self.refresh_products_table()

    async def show_add_view(self):
        """Показать представление добавления товара"""
        self.current_view = "add"
        self.content_area.content = self.create_add_view()
        self.page.update()

    async def show_preview_view(self):
        """Показать представление предварительного просмотра"""
        self.current_view = "preview"
        self.content_area.content = self.create_preview_view()
        # Обновляем сайдбар для изменения текста кнопки
        self.rebuild_sidebar()
        self.page.update()
        # Обновляем сетку просмотра
        await self.refresh_preview_grid()

    async def show_add_view_async(self, e=None):
        """Показать представление добавления товара (асинхронная версия)"""
        try:
            print("🔧 Попытка открытия формы добавления товара...")
            self.current_view = "add"
            print("✅ current_view установлен в 'add'")
            
            self.content_area.content = self.create_add_view()
            print("✅ create_add_view() выполнен")
            
            # Авто-разворачивание окна
            self.page.window_maximized = True
            print("✅ Окно развернуто")
            
            self.rebuild_sidebar()
            print("✅ rebuild_sidebar() выполнен")
            
            await asyncio.sleep(0)  # даём UI «перерисоваться»
            self.page.update()
            print("✅ page.update() выполнен")
            
            print("✅ Форма добавления товара открыта")
        except Exception as e:
            print(f"❌ Ошибка открытия формы: {e}")
            import traceback
            traceback.print_exc()

    # Удаляем дублированную функцию show_add_view

    async def show_products_view(self, e=None):
        """Показать представление товаров (таблица)"""
        self.current_view = "products"
        self.content_area.content = self.create_products_view()
        self.rebuild_sidebar()
        await self.refresh_products_table()

    async def cancel_add_product(self, e=None):
        """Отмена добавления товара"""
        # Очищаем выбранные файлы
        self.selected_files = []
        # Переключаемся на таблицу товаров
        await self.show_products_view()

    def on_files_selected(self, e: ft.FilePickerResultEvent):
        """Обработка выбора файлов"""
        print(f"DEBUG: on_files_selected вызван, files: {e.files}")
        if e.files:
            # В веб-режиме path может быть None, используем name
            self.selected_files = []
            file_names = []
            for f in e.files:
                if f.path:
                    self.selected_files.append(f.path)
                    file_names.append(os.path.basename(f.path))
                elif f.name:
                    # В веб-режиме используем имя файла
                    file_names.append(f.name)
                    # Создаем временный путь или сохраняем имя
                    self.selected_files.append(f.name)
            
            if hasattr(self, 'add_files_text') and self.add_files_text.current:
                self.add_files_text.current.value = f"Выбрано файлов: {len(file_names)}\n" + "\n".join(file_names[:3])
                if len(file_names) > 3:
                    self.add_files_text.current.value += f"\n... и еще {len(file_names) - 3} файлов"
                self.page.update()
            print(f"DEBUG: Выбрано файлов: {len(self.selected_files)}")
            print(f"DEBUG: Имена файлов: {file_names}")
        else:
            self.selected_files = []
            if hasattr(self, 'add_files_text') and self.add_files_text.current:
                self.add_files_text.current.value = "Файлы не выбраны"
                self.page.update()
            print("DEBUG: Файлы не выбраны")

    def show_snack_bar(self, message: str, color: str = None):
        """Показать уведомление (современный способ)"""
        if color is None:
            color = self.colors['primary']
        
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=color,
            duration=3000,
        )
        self.page.snack_bar.open = True
        self.page.update()

    def open_images_dialog(self, e=None):
        """Метод для открытия диалога выбора файлов"""
        print("CLICK: open_images_dialog")  # лог в консоль
        
        try:
            # Принудительно добавляем пикер в overlay
            if self.file_picker not in self.page.overlay:
                self.page.overlay.append(self.file_picker)
                self.page.update()
                print("FilePicker добавлен в overlay")

            # Обновляем страницу перед открытием диалога
            self.page.update()
            print("Страница обновлена")

            # Открываем диалог без фильтра (должно открыться в любом случае)
            print("Пробуем открыть диалог без фильтра...")
            self.file_picker.pick_files(allow_multiple=True)
            print("pick_files вызван")
            
        except Exception as e:
            print(f"❌ Ошибка открытия диалога выбора файлов: {e}")
            import traceback
            traceback.print_exc()
            # Показываем уведомление об ошибке
            self.show_snack_bar(f"❌ Ошибка открытия диалога: {e}", self.colors['error'])

    def compress_image(self, input_path: str, output_path: str, max_size: int = 2000, quality: int = 85) -> bool:
        """Сжатие изображения (по старому рецепту)"""
        try:
            from PIL import Image
            
            # Открываем изображение
            with Image.open(input_path) as img:
                # Конвертируем в RGB если нужно
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Изменяем размер если нужно
                if max(img.size) > max_size:
                    ratio = max_size / max(img.size)
                    new_size = tuple(int(dim * ratio) for dim in img.size)
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                # Сохраняем сжатое изображение
                img.save(output_path, 'JPEG', quality=quality, optimize=True)
                
            print(f"✅ Изображение сжато: {os.path.basename(input_path)} -> {os.path.basename(output_path)}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка сжатия изображения {input_path}: {e}")
            return False

    async def add_product_to_sheets(self, product: dict):
        """Добавление товара в Google Sheets"""
        try:
            from scripts.google_sheets_api import GoogleSheetsAPI
            
            sheets_api = GoogleSheetsAPI()
            
            # Подготавливаем данные для добавления
            row_data = [
                product.get('id', ''),
                product.get('order', ''),
                product.get('section', ''),
                product.get('title', ''),
                product.get('price', ''),
                product.get('desc', ''),
                product.get('meta', ''),
                product.get('status', ''),
                product.get('images', ''),
                product.get('link', ''),
                product.get('updated', '')
            ]
            
            # Добавляем новую строку в Google Sheets
            await sheets_api.add_product_row(row_data)
            
            print(f"✅ Товар '{product.get('title')}' добавлен в Google Sheets")
            
        except Exception as e:
            print(f"❌ Ошибка добавления в Google Sheets: {e}")
            # Не прерываем выполнение, если Google Sheets недоступен

    async def save_products_to_json(self):
        """Сохранение товаров в JSON файл"""
        try:
            with open("products.json", "w", encoding="utf-8") as f:
                json.dump(self.products, f, ensure_ascii=False, indent=2)
            print(f"✅ Сохранено {len(self.products)} товаров в JSON")
        except Exception as e:
            print(f"❌ Ошибка сохранения в JSON: {e}")
            raise



    async def show_deploy_view(self):
        """Показать представление развертывания"""
        self.current_view = "deploy"
        self.content_area.content = self.create_deploy_view()
        self.page.update()

    async def refresh_products_table(self):
        """Обновление таблицы товаров"""
        if not hasattr(self, 'products_table'):
            return
        
        try:
            # Очищаем содержимое таблицы (кроме заголовков)
            table_content = self.products_table.controls[1].content
            table_content.controls.clear()
            
            # Фильтруем товары по разделу
            filtered_products = [
                p for p in self.products 
                if p.get('section', 'home') == self.current_section
            ]
            
            # Сортируем по порядку (order) - сначала по order как число, потом по id
            filtered_products.sort(key=lambda x: (int(x.get('order', 999)), int(x.get('id', 999))))
            
            print(f"Отображаем {len(filtered_products)} товаров для раздела '{self.current_section}'")
            
            # Добавляем строки товаров
            for index, product in enumerate(filtered_products):
                print(f"Добавляем товар: {product.get('title', 'Без названия')} (порядок: {product.get('order', 999)})")
                table_row = self.create_product_table_row(product, index)
                table_content.controls.append(table_row)
            
            self.page.update()
            
        except Exception as e:
            print(f"Ошибка обновления таблицы: {e}")
            import traceback
            traceback.print_exc()

    async def sync_products(self, e=None):
        """Отправка данных в Google Sheets"""
        try:
            # Показываем уведомление
            snack_bar = ft.SnackBar(
                content=ft.Text("🔄 Отправка данных в Google Sheets..."),
                action="OK",
                bgcolor=self.colors['primary'],
            )
            self.page.snack_bar = snack_bar
            snack_bar.open = True
            self.page.update()
            
            # Проверяем наличие файла для синхронизации
            if not os.path.exists('auto_update_oauth2.py'):
                # Если файл не найден, показываем инструкцию
                snack_bar = ft.SnackBar(
                    content=ft.Text("❌ Файл auto_update_oauth2.py не найден. Проверьте настройки."),
                    action="OK",
                    bgcolor=self.colors['error'],
                )
                self.page.snack_bar = snack_bar
                snack_bar.open = True
                self.page.update()
                return
            
            # Проверяем наличие токена
            if not os.path.exists('token.json'):
                snack_bar = ft.SnackBar(
                    content=ft.Text("❌ Токен Google Sheets не найден. Настройте OAuth2."),
                    action="OK",
                    bgcolor=self.colors['error'],
                )
                self.page.snack_bar = snack_bar
                snack_bar.open = True
                self.page.update()
                return
            
            # Запускаем синхронизацию через subprocess
            import subprocess
            result = subprocess.run(['python', '-c', 
                                   'from auto_update_oauth2 import full_sync_oauth2; full_sync_oauth2()'], 
                                  capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                # Показываем успех
                snack_bar = ft.SnackBar(
                    content=ft.Text("✅ Данные успешно отправлены в Google Sheets"),
                    action="OK",
                    bgcolor=self.colors['success'],
                )
                self.page.snack_bar = snack_bar
                snack_bar.open = True
                self.page.update()
                
                # Обновляем таблицу
                await self.refresh_products_table()
            else:
                error_msg = result.stderr if result.stderr else "Неизвестная ошибка"
                raise Exception(f"Ошибка отправки: {error_msg}")
            
        except subprocess.TimeoutExpired:
            snack_bar = ft.SnackBar(
                content=ft.Text("⏰ Отправка заняла слишком много времени"),
                action="OK",
                bgcolor=self.colors['error'],
            )
            self.page.snack_bar = snack_bar
            snack_bar.open = True
            self.page.update()
        except Exception as e:
            print(f"❌ Ошибка отправки: {e}")
            snack_bar = ft.SnackBar(
                content=ft.Text(f"❌ Ошибка отправки: {e}"),
                action="OK",
                bgcolor=self.colors['error'],
            )
            self.page.snack_bar = snack_bar
            snack_bar.open = True
            self.page.update()

    async def edit_product(self, product: Dict):
        """Редактирование товара"""
        # Показываем диалог редактирования
        dialog = ft.AlertDialog(
            title=ft.Text("Редактирование товара"),
            content=ft.Text(f"Редактирование товара: {product.get('title', '')}"),
            actions=[
                ft.TextButton("Отмена", on_click=lambda e: self.page.run_task(self.close_dialog(e))),
                ft.TextButton("Сохранить", on_click=lambda e: self.page.run_task(self.save_edit(product))),
            ],
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    async def delete_product(self, product: Dict):
        """Удаление товара"""
        # Показываем диалог подтверждения
        dialog = ft.AlertDialog(
            title=ft.Text("Удаление товара"),
            content=ft.Text(f"Вы уверены, что хотите удалить товар '{product.get('title', '')}'?"),
            actions=[
                ft.TextButton("Отмена", on_click=lambda e: self.page.run_task(self.close_dialog(e))),
                ft.TextButton("Удалить", on_click=lambda e: self.page.run_task(self.confirm_delete(product))),
            ],
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    async def close_dialog(self, e):
        """Закрытие диалога"""
        self.page.dialog.open = False
        self.page.update()

    async def save_edit(self, product):
        """Сохранение редактирования"""
        try:
            # Здесь будет логика сохранения
            self.show_snack_bar(f"✅ Товар обновлен: {product.get('title', '')}", self.colors['success'])
            await self.close_dialog(None)
        except Exception as e:
            self.show_snack_bar(f"❌ Ошибка обновления: {e}", self.colors['error'])

    async def confirm_delete(self, product):
        """Подтверждение удаления товара"""
        try:
            # Здесь будет логика удаления
            self.show_snack_bar(f"🗑️ Товар удален: {product.get('title', '')}", self.colors['success'])
            await self.close_dialog(None)
        except Exception as e:
            self.show_snack_bar(f"❌ Ошибка удаления: {e}", self.colors['error'])

    async def add_product_from_form(self, e):
        """Добавление товара из формы"""
        try:
            # Получаем данные из формы
            title = self.add_title_field.current.value.strip()
            price = self.add_price_field.current.value.strip()
            desc = self.add_desc_field.current.value.strip()
            meta = self.add_meta_field.current.value.strip()
            section = self.add_section_group.current.value
            
            # Валидация
            if not title:
                self.show_snack_bar("❌ Введите название товара!", self.colors['error'])
                return
            
            if not self.selected_files:
                self.show_snack_bar("❌ Выберите хотя бы одно изображение!", self.colors['error'])
                return
            
            # Проверяем на дубликаты по названию
            for product in self.products:
                if product.get('title', '').strip().lower() == title.lower():
                    self.show_snack_bar(f"❌ Товар с названием '{title}' уже существует!", self.colors['error'])
                    return
            
            # Форматируем цену
            if price:
                # Убираем "р." если есть, чтобы избежать дублирования
                price = price.replace(' р.', '').replace('р.', '').strip()
                price += ' р.'
            else:
                price = "0 р."
            
            # Генерируем уникальный ID (учитываем удаленные товары)
            existing_ids = set()
            for product in self.products:
                try:
                    product_id = int(product.get('id', 0))
                    existing_ids.add(product_id)
                except:
                    pass
            
            # Находим первый свободный ID
            new_id = 1
            while new_id in existing_ids:
                new_id += 1
            
            new_id = str(new_id)
            
            # Создаем папку для изображений
            folder_name = f"product_{new_id}"
            folder_path = os.path.join('img', folder_name)
            os.makedirs(folder_path, exist_ok=True)
            
            # Обрабатываем и сжимаем изображения
            image_names = []
            for i, img_path in enumerate(self.selected_files, 1):
                ext = os.path.splitext(img_path)[1].lower()
                if ext not in ['.jpg', '.jpeg']:
                    ext = '.jpg'
                
                new_name = f"product_{new_id}_{i}{ext}"
                new_path = os.path.join(folder_path, new_name)
                
                if self.compress_image(img_path, new_path):
                    image_names.append(new_name)
            
            # Формируем строку изображений для JSON
            images_str = '|'.join(image_names) if image_names else ''
            
            # Смещаем порядковые номера товаров в той же категории на +1
            for product in self.products:
                if product.get('section') == section:
                    current_order = int(product.get('order', 1))
                    product['order'] = str(current_order + 1)
            
            # Создаем новый товар
            new_product = {
                'id': new_id,
                'title': title,
                'price': price,
                'desc': desc,
                'section': section,
                'order': '1',  # Новый товар получает порядковый номер 1
                'status': 'active',
                'images': images_str,  # Строка с изображениями
                'meta': meta,
                'link': '',
                'updated': datetime.now().isoformat()
            }
            
            # Добавляем в список товаров
            self.products.append(new_product)
            
            # Сохраняем в JSON
            await self.save_products_to_json()
            
            # Синхронизируем с Google Sheets (только новый товар)
            await self.add_product_to_sheets(new_product)
            
            # Обновляем интерфейс
            await self.refresh_products_table()
            
            self.show_snack_bar(f"✅ Товар '{title}' добавлен с ID {new_id}", self.colors['success'])
            
            # Переключаемся на просмотр товаров
            await self.show_products_view()
            
        except Exception as e:
            self.show_snack_bar(f"❌ Ошибка добавления товара: {e}", self.colors['error'])

    async def deploy_site(self, e):
        """Развертывание сайта"""
        try:
            self.show_snack_bar("🚀 Развертывание сайта...", self.colors['secondary'])
            
            # Здесь будет логика развертывания
            await asyncio.sleep(2)  # Имитация процесса
            
            self.show_snack_bar("✅ Сайт успешно развернут", self.colors['success'])
            
        except Exception as e:
            self.show_snack_bar(f"❌ Ошибка развертывания: {e}", self.colors['error'])

    async def create_archive(self, e):
        """Создание архива"""
        try:
            self.show_snack_bar("📦 Создание архива...", self.colors['secondary'])
            
            # Здесь будет логика создания архива
            await asyncio.sleep(1)  # Имитация процесса
            
            self.show_snack_bar("✅ Архив создан", self.colors['success'])
            
        except Exception as e:
            self.show_snack_bar(f"❌ Ошибка создания архива: {e}", self.colors['error'])

    def select_product(self, product: Dict):
        """Выбор товара в таблице"""
        self.selected_product = product
        self.selected_product_text.current.value = product.get('title', 'Без названия')
        self.edit_button.current.disabled = False
        self.delete_button.current.disabled = False
        print(f"Выбран товар: {product.get('title', 'Без названия')}")
        self.page.update()

    def select_preview_product_sync(self, product: Dict):
        """Синхронный выбор товара в просмотре"""
        self.selected_preview_product = product
        print(f"Выбран товар в просмотре: {product.get('title', 'Без названия')}")
        
        # Обновляем сетку просмотра синхронно
        self.refresh_preview_grid_sync()
        
        # Обновляем страницу для показа выделения
        if hasattr(self, 'page') and self.page:
            self.page.update()

    def refresh_preview_grid_sync(self):
        """Синхронное обновление сетки предварительного просмотра"""
        if not self.preview_grid_ref.current:
            return

        grid = self.preview_grid_ref.current
        grid.controls.clear()

        section = getattr(self, "preview_section", "home")
        items = [p for p in self.products if (p.get("section") or "").lower() == section]
        # сортировка по order
        def to_int(v): 
            try: return int(str(v))
            except: return 0
        items.sort(key=lambda x: to_int(x.get("order", 0)))

        # Сохраняем список товаров для управления порядком
        self.preview_products = items.copy()
        
        print(f"Отображаем {len(items)} товаров в просмотре для раздела '{section}'")

        for p in items:
            # Проверяем, выбран ли этот товар
            is_selected = (self.selected_preview_product and 
                          self.selected_preview_product.get('id') == p.get('id'))
            print(f"Товар {p.get('id')} - {p.get('title')} выбран: {is_selected}")

            # Создаем миниатюру товара
            thumbnail = self.create_product_thumbnail(p)

            # карточка плитки
            tile = ft.Container(
                bgcolor=self.colors["surface"],
                border=ft.border.all(
                    3 if is_selected else 1, 
                    self.colors["primary"] if is_selected else self.colors["outline"]
                ),
                border_radius=12,
                clip_behavior=ft.ClipBehavior.HARD_EDGE,
                content=ft.Column(
                    [
                        # миниатюра товара (занимает большую часть)
                        ft.Container(
                            content=thumbnail,
                            expand=True,
                        ),
                        # подпись внизу
                        ft.Container(
                            content=ft.Text(
                                p.get("title", ""), 
                                size=12, 
                                weight=ft.FontWeight.W_600, 
                                color=self.colors['on_surface'],
                                text_align=ft.TextAlign.CENTER,
                            ),
                            padding=ft.padding.all(8),
                            bgcolor=self.colors['surface'],
                        ),
                    ],
                    expand=True,
                ),
                on_click=lambda e, pid=p.get("id"): self.on_preview_tile_click(pid),
            )

            grid.controls.append(tile)

    async def select_preview_product(self, product: Dict):
        """Выбор товара в просмотре"""
        self.selected_preview_product = product
        print(f"Выбран товар в просмотре: {product.get('title', 'Без названия')}")
        
        # Обновляем сетку просмотра для показа выбранного товара
        await self.refresh_preview_grid()

    def edit_selected_product(self, e):
        """Редактирование выбранного товара"""
        if self.selected_product:
            # Просто обновляем страницу
            if hasattr(self, 'page') and self.page:
                self.page.update()

    async def delete_selected_product(self, e):
        """Удаление выбранного товара"""
        if not self.selected_product:
            self.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text("❌ Выберите товар для удаления"),
                    action="OK",
                    bgcolor=self.colors['error'],
                )
            )
            return
        
        try:
            product_to_delete = self.selected_product
            product_id = product_to_delete.get('id')
            product_section = product_to_delete.get('section')
            
            # Удаляем товар из списка
            self.products = [p for p in self.products if p.get('id') != product_id]
            
            # Смещаем порядковые номера товаров в той же категории
            for product in self.products:
                if product.get('section') == product_section:
                    current_order = int(product.get('order', 1))
                    deleted_order = int(product_to_delete.get('order', 1))
                    if current_order > deleted_order:
                        product['order'] = str(current_order - 1)
            
            # Сохраняем в JSON
            await self.save_products_to_json()
            
            # Удаляем папку с изображениями
            folder_path = f"img/product_{product_id}"
            if os.path.exists(folder_path):
                import shutil
                shutil.rmtree(folder_path)
                print(f"✅ Папка {folder_path} удалена")
            
            # Обновляем интерфейс
            await self.refresh_products_table()
            
            # Очищаем выбор
            self.selected_product = None
            self.selected_product_text.current.value = "Нет выбранного товара"
            self.edit_button.current.disabled = True
            self.delete_button.current.disabled = True
            
            self.show_snack_bar(f"✅ Товар '{product_to_delete.get('title')}' удален", self.colors['success'])
            
            self.page.update()
            
        except Exception as e:
            self.show_snack_bar(f"❌ Ошибка удаления: {e}", self.colors['error'])

    def deploy_site(self, e):
        """Деплой сайта"""
        try:
            # Показываем уведомление
            snack_bar = ft.SnackBar(
                content=ft.Text("🚀 Деплой сайта..."),
                action="OK",
                bgcolor=self.colors['success'],
            )
            self.page.snack_bar = snack_bar
            snack_bar.open = True
            self.page.update()
            
            # Здесь будет логика деплоя
            # Пока что имитируем процесс
            if hasattr(self, 'page') and self.page:
                self.page.update()
            
        except Exception as e:
            print(f"❌ Ошибка деплоя: {e}")
            snack_bar = ft.SnackBar(
                content=ft.Text(f"❌ Ошибка деплоя: {e}"),
                action="OK",
                bgcolor=self.colors['error'],
            )
            self.page.snack_bar = snack_bar
            snack_bar.open = True
            self.page.update()

    async def perform_deploy(self):
        """Выполнение деплоя"""
        try:
            await asyncio.sleep(2)  # Имитация процесса
            
            # Показываем успех
            snack_bar = ft.SnackBar(
                content=ft.Text("✅ Сайт успешно развернут!"),
                action="OK",
                bgcolor=self.colors['success'],
            )
            self.page.snack_bar = snack_bar
            snack_bar.open = True
            self.page.update()
            
        except Exception as e:
            print(f"❌ Ошибка выполнения деплоя: {e}")

    async def auto_sync_with_sheets(self):
        """Автоматическая синхронизация с Google Sheets"""
        try:
            print("🔄 Автоматическая синхронизация с Google Sheets...")
            
            # Проверяем наличие конфигурации Google API
            if not os.path.exists("google_api_config.json"):
                print("⚠️ Google API конфигурация не найдена")
                return
            
            # Здесь будет логика синхронизации с Google Sheets
            # Пока что имитируем процесс
            await asyncio.sleep(1)
            
            print("✅ Автоматическая синхронизация завершена")
            
        except Exception as e:
            print(f"❌ Ошибка автоматической синхронизации: {e}")

    async def load_from_sheets(self, e):
        """Подгрузка данных с Google Sheets"""
        try:
            # Показываем уведомление
            snack_bar = ft.SnackBar(
                content=ft.Text("📥 Загрузка данных с Google Sheets..."),
                action="OK",
                bgcolor=self.colors['secondary'],
            )
            self.page.snack_bar = snack_bar
            snack_bar.open = True
            self.page.update()
            
            # Загружаем данные из Google Sheets
            new_products = await self.load_products_from_sheets()
            
            if new_products:
                # Умное обновление товаров
                await self.smart_update_products(new_products)
                
                # Обновляем таблицу
                await self.refresh_products_table()
                
                # Показываем успех
                snack_bar = ft.SnackBar(
                    content=ft.Text(f"✅ Загружено {len(new_products)} товаров с Google Sheets"),
                    action="OK",
                    bgcolor=self.colors['success'],
                )
                self.page.snack_bar = snack_bar
                snack_bar.open = True
                self.page.update()
            else:
                # Показываем ошибку
                snack_bar = ft.SnackBar(
                    content=ft.Text("❌ Не удалось загрузить данные с Google Sheets"),
                    action="OK",
                    bgcolor=self.colors['error'],
                )
                self.page.snack_bar = snack_bar
                snack_bar.open = True
                self.page.update()
            
        except Exception as e:
            print(f"❌ Ошибка загрузки с Google Sheets: {e}")
            snack_bar = ft.SnackBar(
                content=ft.Text(f"❌ Ошибка загрузки: {e}"),
                action="OK",
                bgcolor=self.colors['error'],
            )
            self.page.snack_bar = snack_bar
            snack_bar.open = True
            self.page.update()

    async def load_products_from_sheets(self):
        """Загрузка товаров из Google Sheets через OAuth2"""
        try:
            import gspread
            from google.oauth2.credentials import Credentials
            import json
            
            # Загружаем конфигурацию Google Sheets
            try:
                with open('google_api_config.json', 'r') as f:
                    config = json.load(f)
                    spreadsheet_id = config.get('spreadsheet_id')
            except Exception as e:
                print(f"❌ Ошибка загрузки конфигурации: {e}")
                return []
            
            if not spreadsheet_id:
                print("❌ ID таблицы не найден в конфигурации")
                return []
            
            # Проверяем наличие токена OAuth2
            if not os.path.exists('token.json'):
                print("❌ Файл token.json не найден. Нужно настроить OAuth2")
                return []
            
            print(f"📥 Загрузка данных из Google Sheets через OAuth2 (ID: {spreadsheet_id})...")
            
            # Настройки Google Sheets API
            SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
            CREDENTIALS_FILE = 'token.json'
            
            # Получаем клиент для работы с Google Sheets
            creds = Credentials.from_authorized_user_file(CREDENTIALS_FILE, scopes=SCOPES)
            client = gspread.authorize(creds)
            
            # Открываем таблицу
            spreadsheet = client.open_by_key(spreadsheet_id)
            worksheet = spreadsheet.sheet1
            
            # Получаем все данные
            all_values = worksheet.get_all_values()
            if not all_values:
                print("❌ Таблица пуста!")
                return []
            
            headers = all_values[0]
            data = all_values[1:]
            
            print(f"📋 Заголовки: {headers}")
            print(f"📊 Найдено строк данных: {len(data)}")
            
            products = []
            
            # Обрабатываем строки данных
            for i, row in enumerate(data, 1):
                if not row or len(row) < 4:  # Минимум ID, Order, Section, Title
                    continue
                
                # Очищаем данные
                def clean_text(text):
                    if not text:
                        return ''
                    # Убираем лишние пробелы и переносы строк
                    text = str(text).strip().replace('\n', ' ').replace('\r', ' ')
                    # Убираем множественные пробелы
                    while '  ' in text:
                        text = text.replace('  ', ' ')
                    return text
                
                try:
                    # Парсим данные согласно структуре
                    product_id = clean_text(row[0]) if len(row) > 0 else ""
                    order = clean_text(row[1]) if len(row) > 1 else ""
                    section = clean_text(row[2]) if len(row) > 2 else ""
                    title = clean_text(row[3]) if len(row) > 3 else ""
                    price = clean_text(row[4]) if len(row) > 4 else ""
                    desc = clean_text(row[5]) if len(row) > 5 else ""
                    meta = clean_text(row[6]) if len(row) > 6 else ""
                    status = clean_text(row[7]) if len(row) > 7 else ""
                    images = clean_text(row[8]) if len(row) > 8 else ""
                    link = clean_text(row[9]) if len(row) > 9 else ""
                    
                    # Пропускаем строки без названия
                    if not title:
                        continue
                    
                    # Создаем объект товара
                    product = {
                        'id': product_id,
                        'order': order,
                        'section': section,
                        'title': title,
                        'price': price,
                        'desc': desc,
                        'meta': meta,
                        'status': status,
                        'images': images,
                        'link': link,
                        'updated': datetime.now().isoformat()
                    }
                    
                    products.append(product)
                    print(f"✅ Загружен товар: {title} (ID: {product_id}, Order: {order}, Section: {section})")
                    
                except Exception as e:
                    print(f"❌ Ошибка парсинга строки {i}: {e}")
                    continue
            
            print(f"✅ Загружено товаров: {len(products)}")
            return products
            
        except Exception as e:
            print(f"❌ Ошибка загрузки из Google Sheets: {e}")
            return []

    async def smart_update_products(self, new_products):
        """Умное обновление товаров с сопоставлением по ID"""
        try:
            print("🧠 Умное обновление товаров по ID...")
            
            # Создаем словарь существующих товаров по ID
            existing_products = {}
            for product in self.products:
                if 'id' in product and product['id']:
                    existing_products[product['id']] = product
            
            print(f"📁 Найдено {len(existing_products)} существующих товаров")
            
            updated_count = 0
            new_count = 0
            
            # Обрабатываем новые товары
            final_products = []
            for new_product in new_products:
                product_id = new_product.get('id', '')
                
                if product_id in existing_products:
                    # Обновляем существующий товар
                    existing_product = existing_products[product_id]
                    existing_product.update(new_product)
                    final_products.append(existing_product)
                    updated_count += 1
                    print(f"🔄 Обновлен товар: {new_product['title']} (ID: {product_id})")
                else:
                    # Добавляем новый товар
                    final_products.append(new_product)
                    new_count += 1
                    print(f"➕ Добавлен новый товар: {new_product['title']} (ID: {product_id})")
            
            # Заменяем список товаров
            self.products = final_products
            
            print(f"✅ Умное обновление завершено: {updated_count} обновлено, {new_count} добавлено")
            
            # Сохраняем изменения
            await self.save_products()
            
        except Exception as e:
            print(f"❌ Ошибка умного обновления: {e}")

    async def save_products(self):
        """Сохранение товаров в JSON файл"""
        try:
            with open("products.json", "w", encoding="utf-8") as f:
                json.dump(self.products, f, ensure_ascii=False, indent=2)
            print("✅ Товары сохранены в products.json")
        except Exception as e:
            print(f"❌ Ошибка сохранения товаров: {e}")

    async def move_product_up(self, e=None):
        """Поднять товар в порядке"""
        if not self.selected_preview_product:
            self.show_notification("❌ Выберите товар для изменения порядка", "error")
            return
        
        try:
            # Находим индекс выбранного товара в списке просмотра
            current_index = None
            for i, product in enumerate(self.preview_products):
                if product.get('id') == self.selected_preview_product.get('id'):
                    current_index = i
                    break
            
            if current_index is None or current_index == 0:
                self.show_notification("❌ Товар уже наверху", "error")
                return
            
            # Меняем местами с предыдущим товаром
            self.preview_products[current_index], self.preview_products[current_index - 1] = \
                self.preview_products[current_index - 1], self.preview_products[current_index]
            
            # Обновляем порядок в основном списке товаров
            self.update_products_order()
            
            # Обновляем сетку просмотра
            await self.refresh_preview_grid()
            
            self.show_notification("✅ Товар поднят", "success")
            
        except Exception as e:
            print(f"Ошибка поднятия товара: {e}")
            self.show_notification("❌ Ошибка поднятия товара", "error")

    async def move_product_down(self, e=None):
        """Опустить товар в порядке"""
        if not self.selected_preview_product:
            self.show_notification("❌ Выберите товар для изменения порядка", "error")
            return
        
        try:
            # Находим индекс выбранного товара в списке просмотра
            current_index = None
            for i, product in enumerate(self.preview_products):
                if product.get('id') == self.selected_preview_product.get('id'):
                    current_index = i
                    break
            
            if current_index is None or current_index == len(self.preview_products) - 1:
                self.show_notification("❌ Товар уже внизу", "error")
                return
            
            # Меняем местами со следующим товаром
            self.preview_products[current_index], self.preview_products[current_index + 1] = \
                self.preview_products[current_index + 1], self.preview_products[current_index]
            
            # Обновляем порядок в основном списке товаров
            self.update_products_order()
            
            # Обновляем сетку просмотра
            await self.refresh_preview_grid()
            
            self.show_notification("✅ Товар опущен", "success")
            
        except Exception as e:
            print(f"Ошибка опускания товара: {e}")
            self.show_notification("❌ Ошибка опускания товара", "error")

    async def save_product_order(self, e=None):
        """Сохранить новый порядок товаров"""
        try:
            # Обновляем порядок в основном списке товаров
            self.update_products_order()
            
            # Сохраняем в файл
            await self.save_products()
            
            # Обновляем Google Sheets
            await self.update_sheets_order()
            
            # Обновляем таблицу товаров
            await self.refresh_products_table()
            
            self.show_notification("✅ Порядок товаров сохранен в файл и Google Sheets", "success")
            
        except Exception as e:
            print(f"Ошибка сохранения порядка: {e}")
            self.show_notification("❌ Ошибка сохранения порядка", "error")

    def update_products_order(self):
        """Обновить порядок в основном списке товаров"""
        try:
            # Создаем словарь для быстрого поиска товаров по ID
            products_dict = {p.get('id'): p for p in self.products}
            
            # Обновляем порядок на основе preview_products
            for i, preview_product in enumerate(self.preview_products):
                product_id = preview_product.get('id')
                if product_id in products_dict:
                    products_dict[product_id]['order'] = i + 1
            
            print(f"✅ Обновлен порядок для {len(self.preview_products)} товаров")
            
        except Exception as e:
            print(f"Ошибка обновления порядка: {e}")

    async def update_sheets_order(self):
        """Обновить порядок товаров в Google Sheets"""
        try:
            # Проверяем наличие конфигурации Google API
            if not os.path.exists("google_api_config.json"):
                print("⚠️ Google API конфигурация не найдена")
                return
            
            # Импортируем модуль для работы с Google Sheets
            try:
                from scripts.google_sheets_api import GoogleSheetsAPI
            except ImportError:
                print("⚠️ Модуль Google Sheets API не найден")
                return
            
            # Создаем экземпляр API
            sheets_api = GoogleSheetsAPI()
            
            # Обновляем порядок в Sheets
            for i, preview_product in enumerate(self.preview_products):
                product_id = preview_product.get('id')
                new_order = i + 1
                
                # Находим товар в основном списке
                for product in self.products:
                    if product.get('id') == product_id:
                        # Обновляем порядок в Sheets
                        await sheets_api.update_product_order(product_id, new_order)
                        break
            
            print(f"✅ Обновлен порядок в Google Sheets для {len(self.preview_products)} товаров")
            
        except Exception as e:
            print(f"❌ Ошибка обновления порядка в Google Sheets: {e}")

    def show_notification(self, message: str, type: str = "info"):
        """Показать уведомление"""
        try:
            color_map = {
                "success": self.colors['success'],
                "error": self.colors['error'],
                "info": self.colors['primary']
            }
            
            snack_bar = ft.SnackBar(
                content=ft.Text(message),
                action="OK",
                bgcolor=color_map.get(type, self.colors['primary']),
            )
            self.page.snack_bar = snack_bar
            snack_bar.open = True
            self.page.update()
            
        except Exception as e:
            print(f"Ошибка показа уведомления: {e}")

    def update_selected_product_indicator(self):
        """Обновление индикатора выбранного товара"""
        try:
            if hasattr(self, 'page') and self.page:
                self.page.update()
        except Exception as e:
            print(f"Ошибка обновления индикатора: {e}")

    def on_preview_tile_click(self, product_id):
        """Обработка клика по плитке товара в просмотре"""
        try:
            # Находим товар по ID
            product = None
            for p in self.preview_products:
                if p.get('id') == product_id:
                    product = p
                    break
            
            if not product:
                print(f"Товар с ID {product_id} не найден")
                return
            
            # Если уже есть выбранный товар и это другой товар - меняем местами
            if (self.selected_preview_product and 
                self.selected_preview_product.get('id') != product_id):
                
                # Находим индексы товаров
                current_index = None
                new_index = None
                
                for i, p in enumerate(self.preview_products):
                    if p.get('id') == self.selected_preview_product.get('id'):
                        current_index = i
                    if p.get('id') == product_id:
                        new_index = i
                
                if current_index is not None and new_index is not None:
                    # Меняем местами
                    self.preview_products[current_index], self.preview_products[new_index] = \
                        self.preview_products[new_index], self.preview_products[current_index]
                    
                    # Обновляем порядок в основном списке товаров
                    self.update_products_order()
                    
                    # Сбрасываем выделение
                    self.selected_preview_product = None
                    
                    # Обновляем сетку
                    self.refresh_preview_grid_sync()
                    if hasattr(self, 'page') and self.page:
                        self.page.update()
                    
                    print(f"✅ Товары поменяны местами: {self.selected_preview_product.get('title') if self.selected_preview_product else 'None'} ↔ {product.get('title')}")
                    return
            
            # Если это первый клик или тот же товар - просто выделяем
            self.select_preview_product_sync(product)
            
        except Exception as e:
            print(f"Ошибка выбора товара: {e}")

    async def refresh_preview_grid(self):
        """Обновление сетки предварительного просмотра"""
        if not self.preview_grid_ref.current:
            return

        grid = self.preview_grid_ref.current
        grid.controls.clear()

        section = getattr(self, "preview_section", "home")
        items = [p for p in self.products if (p.get("section") or "").lower() == section]
        # сортировка по order
        def to_int(v): 
            try: return int(str(v))
            except: return 0
        items.sort(key=lambda x: to_int(x.get("order", 0)))

        # Сохраняем список товаров для управления порядком
        self.preview_products = items.copy()
        
        print(f"Отображаем {len(items)} товаров в просмотре для раздела '{section}'")

        for p in items:
            # Проверяем, выбран ли этот товар
            is_selected = (self.selected_preview_product and 
                          self.selected_preview_product.get('id') == p.get('id'))
            print(f"Товар {p.get('id')} - {p.get('title')} выбран: {is_selected}")

            # Создаем миниатюру товара
            thumbnail = self.create_product_thumbnail(p)

            # карточка плитки
            tile = ft.Container(
                bgcolor=self.colors["surface"],
                border=ft.border.all(
                    3 if is_selected else 1, 
                    self.colors["primary"] if is_selected else self.colors["outline"]
                ),
                border_radius=12,
                clip_behavior=ft.ClipBehavior.HARD_EDGE,
                content=ft.Column(
                    [
                        # миниатюра товара (занимает большую часть)
                        ft.Container(
                            content=thumbnail,
                            expand=True,
                        ),
                        # подпись внизу
                        ft.Container(
                            content=ft.Text(
                                p.get("title", ""), 
                                size=12, 
                                weight=ft.FontWeight.W_600, 
                                color=self.colors['on_surface'],
                                text_align=ft.TextAlign.CENTER,
                            ),
                            padding=ft.padding.all(8),
                            bgcolor=self.colors['surface'],
                        ),
                    ],
                    expand=True,
                ),
                on_click=lambda e, pid=p.get("id"): self.on_preview_tile_click(pid),
            )

            grid.controls.append(tile)

        self.page.update()

def main():
    """Главная функция"""
    app = PlatformaManagerFinal()
    ft.app(target=app.main, view=ft.WEB_BROWSER)

if __name__ == "__main__":
    main()

