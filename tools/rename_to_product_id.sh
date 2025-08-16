#!/bin/bash

# Скрипт для переименования папок и файлов согласно новой системе ID
# Основан на данных из sheets_data.json

echo "🚀 Начинаем переименование папок и файлов согласно новой системе ID..."

# Переходим в корневую директорию проекта
cd "$(dirname "$0")/.."
cd web/img

# Создаем маппинг: ID -> текущая папка -> новое название
declare -A id_mapping=(
    ["12"]="belt-nessffo-1:product_12"
    ["11"]="belt-skirt-1:product_11" 
    ["10"]="belt-bag-p1:product_10"
    ["9"]="shirt-white:product_9"
    ["8"]="pants-with-belt-skirt-U2:product_8"
    ["7"]="shirt-olive:product_7"
    ["6"]="nessffo-bag:product_6"
    ["5"]="shirt-pants-white:product_5"
    ["4"]="shawl-1:product_4"
    ["3"]="belt-trousers:product_3"
    ["2"]="apron-1:product_2"
    ["1"]="shawl-2:product_1"
)

for id in "${!id_mapping[@]}"; do
    mapping="${id_mapping[$id]}"
    current_folder="${mapping%:*}"
    new_folder="${mapping#*:}"
    
    echo "📁 ID $id: $current_folder → $new_folder"
    
    if [ -d "$current_folder" ]; then
        # Создаем новую папку
        mkdir -p "$new_folder"
        
        # Переименовываем файлы
        file_count=1
        for file in "$current_folder"/*.jpg; do
            if [ -f "$file" ]; then
                new_filename="$new_folder/product_${id}_${file_count}.jpg"
                cp "$file" "$new_filename"
                echo "  📄 $(basename "$file") → product_${id}_${file_count}.jpg"
                ((file_count++))
            fi
        done
        
        # Удаляем старую папку
        rm -rf "$current_folder"
        echo "  🗑️  Удалена старая папка $current_folder"
    else
        echo "  ⚠️  Папка $current_folder не найдена"
    fi
done

echo "✅ Переименование завершено!"
