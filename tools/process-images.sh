#!/bin/bash

# Скрипт для обработки изображений каталога
# Требует установленного ImageMagick (mogrify)

echo "🖼️  Обработка изображений каталога..."
echo "📊 Настройки качества:"
echo "   - Максимальный размер: 2000x2000px"
echo "   - Качество JPEG: 85%"
echo "   - Улучшение резкости: включено"
echo "   - Оптимизация: включена"
echo ""

# Проверяем наличие ImageMagick
if ! command -v mogrify &> /dev/null; then
    echo "❌ ImageMagick не установлен. Установите его:"
    echo "   macOS: brew install imagemagick"
    echo "   Ubuntu: sudo apt-get install imagemagick"
    exit 1
fi

# Создаем папку для обработанных изображений
mkdir -p img_processed

# Находим все изображения (кроме баннеров и плейсхолдера)
echo "📁 Поиск изображений..."
find ./img -type f \( -iname '*.jpg' -o -iname '*.jpeg' \) \
  ! -iname 'banner*.jpg' ! -iname 'item-placeholder.jpg' \
  -print | while read -r file; do
    echo "🔄 Обработка: $file"
    
    # Создаем папку для обработанного файла
    dir=$(dirname "$file")
    mkdir -p "img_processed/$dir"
    
    # Обрабатываем изображение с улучшенными настройками
    mogrify -verbose \
      -auto-orient \
      -resize '2000x2000>' \
      -strip \
      -interlace Plane \
      -quality 85 \
      -sharpen 0x1 \
      -unsharp 0x1+1+0.05 \
      -path "img_processed/$dir" "$file"
done

echo "✅ Обработка завершена!"
echo "📊 Статистика:"
echo "   Всего изображений: $(find ./img -type f \( -iname '*.jpg' -o -iname '*.jpeg' \) ! -iname 'banner*.jpg' ! -iname 'item-placeholder.jpg' -print | wc -l)"
echo "   Обработано: $(find ./img_processed -type f \( -iname '*.jpg' -o -iname '*.jpeg' \) -print | wc -l)"

# Показываем размеры до и после
echo ""
echo "📏 Размеры файлов:"
echo "   До обработки: $(du -sh img | cut -f1)"
echo "   После обработки: $(du -sh img_processed | cut -f1)"

echo ""
echo "💡 Для применения изменений выполните:"
echo "   mv img img_original && mv img_processed img"
