#!/bin/bash

# Скрипт для создания архива для деплоя на Netlify

echo "📦 Создание архива для деплоя..."

# Создаем временную папку для архива
ARCHIVE_DIR="platforma_site_deploy_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$ARCHIVE_DIR"

echo "📁 Копирование файлов..."

# Копируем основные файлы сайта из папки web
cp web/index.html "$ARCHIVE_DIR/"
cp web/app.min.js "$ARCHIVE_DIR/"
cp web/styles.min.css "$ARCHIVE_DIR/"
cp web/mobile.overrides.css "$ARCHIVE_DIR/"

# Копируем папку с изображениями
cp -r img "$ARCHIVE_DIR/"

# Создаем README для деплоя
cat > "$ARCHIVE_DIR/README.md" << EOF
# Platforma Site - Deploy Package

Дата создания: $(date)

## Файлы для деплоя на Netlify:

- \`index.html\` - главная страница
- \`app.min.js\` - JavaScript код
- \`styles.min.css\` - стили
- \`mobile.overrides.css\` - мобильные стили
- \`img/\` - папка с изображениями

## Инструкция по деплою:

1. Загрузите все файлы в Netlify
2. Укажите \`index.html\` как главную страницу
3. Сайт будет доступен по адресу: https://your-site-name.netlify.app

## Источник данных:

Google Sheets: https://docs.google.com/spreadsheets/d/e/2PACX-1vRGdW7QcHV6BgZHJnSMzXKkmsXDYZulMojN312tgvI6PK86H8dRjReYUOHI2l_aVYzLg2NIjAcir89g/pub?output=tsv

## Исправления в этой версии:

✅ Исправлены пути к изображениям в Google Sheets
✅ Все изображения теперь загружаются корректно
✅ Убраны ошибки 404 для изображений
EOF

# Создаем архив
ARCHIVE_NAME="platforma_site_deploy_$(date +%Y%m%d_%H%M%S).zip"
zip -r "$ARCHIVE_NAME" "$ARCHIVE_DIR"

# Удаляем временную папку
rm -rf "$ARCHIVE_DIR"

echo "✅ Архив создан: $ARCHIVE_NAME"
echo "📊 Размер архива: $(du -h "$ARCHIVE_NAME" | cut -f1)"
echo ""
echo "🚀 Готово для деплоя на Netlify!"
echo "   Просто перетащите файлы из архива в Netlify"
