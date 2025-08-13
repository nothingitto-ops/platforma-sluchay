# 🛍️ Platforma Development Guide

## 🚀 Быстрый старт

### Локальная разработка

1. **Запуск локального сервера:**
   ```bash
   ./start_local_server.sh
   ```
   или вручную:
   ```bash
   cd web
   python -m http.server 8000
   ```

2. **Открыть сайт в браузере:**
   ```
   http://localhost:8000
   ```

### Структура проекта

```
platforma_site_current/
├── web/                    # Основные файлы сайта
│   ├── index.html         # Главная страница
│   ├── app.min.js         # Основной JavaScript
│   ├── styles.min.css     # Стили
│   ├── products.json      # Данные товаров
│   └── img/               # Изображения товаров
├── img/                   # Исходные изображения
├── scripts/               # Скрипты для обновления
└── backups/               # Резервные копии
```

## 🔧 Разработка

### Внесение изменений

1. **Редактирование товаров:**
   - Измените файл `products.json`
   - Обновите изображения в папке `img/`

2. **Редактирование дизайна:**
   - `styles.min.css` - основные стили
   - `mobile.overrides.css` - мобильные стили
   - `card-titles.css` - стили заголовков карточек

3. **Редактирование функционала:**
   - `app.min.js` - основная логика
   - `app-test.js` - тестовая версия

### Тестирование

1. **Локальное тестирование:**
   - Откройте `http://localhost:8000`
   - Проверьте все функции сайта

2. **Тестовые страницы:**
   - `http://localhost:8000/test.html` - тестовая страница
   - `http://localhost:8000/test-simple.html` - упрощенная версия
   - `http://localhost:8000/debug_site.html` - отладочная версия

## 🚀 Деплой

### Автоматический деплой на GitHub

```bash
python github_deploy.py
```

### Ручной деплой

1. Откройте GitHub Desktop
2. Перейдите в папку `web/`
3. Сделайте коммит изменений
4. Отправьте на GitHub

### Проверка деплоя

- **Локально:** `http://localhost:8000`
- **Продакшн:** `https://platformasluchay.ru`

## 📊 Данные

### Структура товара

```json
{
  "id": "2",
  "order": "1",
  "section": "home",
  "title": "Название товара",
  "price": "3000 р.",
  "desc": "Описание товара",
  "meta": "Дополнительная информация",
  "status": "stock", // "stock" или "preorder"
  "images": "product_2/product_2_1.jpg,product_2/product_2_2.jpg",
  "link": "https://t.me/stub123",
  "updated": "2025-08-13T21:59:12.410841"
}
```

### Разделы сайта

- `home` - главная страница
- `nessffo` - коллекция nessffo

### Статусы товаров

- `stock` - в наличии
- `preorder` - под заказ

## 🔍 Отладка

### Полезные команды

```bash
# Проверка статуса Git
cd web && git status

# Просмотр логов сервера
tail -f /var/log/httpd/access_log

# Проверка доступности сайта
curl -I http://localhost:8000

# Проверка данных товаров
python -c "import json; print(len(json.load(open('web/products.json'))))"

# Обновление цены товара
python update_price.py 'Название товара' 'Новая цена'

# Обновление JavaScript из JSON
python update_js_from_json.py
```

### Частые проблемы

1. **Сайт не загружается:**
   - Проверьте, что сервер запущен в папке `web/`
   - Убедитесь, что порт 8000 свободен

2. **Изображения не отображаются:**
   - Проверьте пути в `products.json`
   - Убедитесь, что файлы существуют в `img/`

3. **Изменения не отображаются:**
   - Очистите кэш браузера (Ctrl+F5)
   - Проверьте, что файлы сохранены

## 📞 Поддержка

- **GitHub:** https://github.com/nothingitto-ops/platformini
- **Сайт:** https://platformasluchay.ru
- **Telegram:** https://t.me/stub123
