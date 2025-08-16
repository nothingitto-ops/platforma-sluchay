#!/bin/bash

echo "🚀 Полный перезапуск сайта Platforma"
echo "======================================"

# Останавливаем все процессы на порту 8000
echo "🛑 Останавливаем процессы на порту 8000..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Обновляем данные
echo "🔄 Обновляем данные..."
cd /Users/ww/Downloads/platforma/platforma_site_current
python update_js_from_json.py

# Переходим в папку web
cd web

# Добавляем все изменения
echo "📝 Добавляем изменения в Git..."
git add .

# Коммитим
echo "💾 Создаем коммит..."
timestamp=$(date '+%Y-%m-%d %H:%M:%S')
git commit -m "🔄 Автоматическое обновление - $timestamp"

# Пушим на GitHub
echo "🚀 Отправляем на GitHub..."
git push origin main

# Запускаем локальный сервер
echo "🌐 Запускаем локальный сервер..."
cd ..
python -m http.server 8000 &

echo ""
echo "✅ Сайт перезапущен!"
echo "🌐 Локальный сервер: http://localhost:8000"
echo "🌍 GitHub Pages: https://nothingitto-ops.github.io/platformini/"
echo ""
echo "💡 Для остановки сервера нажмите Ctrl+C"
