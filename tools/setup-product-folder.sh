#!/bin/bash

# Скрипт для создания папки товара и перемещения файлов
# Использование: ./setup-product-folder.sh "название товара"

if [ $# -eq 0 ]; then
    echo "❌ Укажите название товара!"
    echo "Использование: ./setup-product-folder.sh \"название товара\""
    exit 1
fi

PRODUCT_NAME="$1"
CLEAN_NAME=$(echo "$PRODUCT_NAME" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9а-я]/-/g' | sed 's/-\+/-/g' | sed 's/^-\|-$//g')
FOLDER_PATH="img/$CLEAN_NAME"
DOWNLOADS_DIR="$HOME/Downloads"

echo "🛍️  Настройка папки для товара: $PRODUCT_NAME"
echo "📁 Папка: $FOLDER_PATH"
echo ""

# Создаем папку
if [ ! -d "$FOLDER_PATH" ]; then
    echo "📂 Создаем папку: $FOLDER_PATH"
    mkdir -p "$FOLDER_PATH"
else
    echo "📂 Папка уже существует: $FOLDER_PATH"
fi

# Ищем файлы в папке загрузок
echo ""
echo "🔍 Ищем файлы в папке загрузок..."
FOUND_FILES=()

for file in "$DOWNLOADS_DIR"/"$CLEAN_NAME"-*.jpg; do
    if [ -f "$file" ]; then
        FOUND_FILES+=("$file")
        echo "📸 Найден файл: $(basename "$file")"
    fi
done

if [ ${#FOUND_FILES[@]} -eq 0 ]; then
    echo "⚠️  Файлы не найдены в папке загрузок"
    echo "   Искали: $CLEAN_NAME-*.jpg"
    echo ""
    echo "💡 Убедитесь что:"
    echo "   1. Файлы скачаны в папку 'Загрузки'"
    echo "   2. Имена файлов начинаются с '$CLEAN_NAME-'"
    echo "   3. Файлы имеют расширение .jpg"
    exit 1
fi

# Перемещаем файлы
echo ""
echo "📦 Перемещаем файлы в папку товара..."
for file in "${FOUND_FILES[@]}"; do
    filename=$(basename "$file")
    echo "   $filename → $FOLDER_PATH/"
    mv "$file" "$FOLDER_PATH/"
done

echo ""
echo "✅ Готово! Папка настроена:"
echo "   📁 $FOLDER_PATH"
echo "   📸 Файлов перемещено: ${#FOUND_FILES[@]}"
echo ""
echo "📋 Для Google Sheets используйте:"
echo "   $CLEAN_NAME-1.jpg|$CLEAN_NAME-2.jpg|..."
echo ""
echo "🚀 Для деплоя запустите: ./create-deploy-archive.sh"
