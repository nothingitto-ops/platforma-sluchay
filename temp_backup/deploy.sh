#!/bin/bash

# Скрипт для быстрого деплоя обновлений сайта platforma.sluchay

echo "🚀 Деплой обновлений platforma.sluchay"
echo "====================================="

# Проверяем, что мы в правильной директории
if [ ! -f "index.html" ]; then
    echo "❌ Ошибка: index.html не найден. Убедитесь, что вы находитесь в папке web/"
    exit 1
fi

# Проверяем статус git
if [ ! -d ".git" ]; then
    echo "❌ Ошибка: Git репозиторий не найден"
    exit 1
fi

# Проверяем, есть ли изменения
if git diff-index --quiet HEAD --; then
    echo "✅ Нет изменений для коммита"
else
    echo "📝 Найдены изменения, добавляем в git..."
    
    # Добавляем все изменения
    git add .
    
    # Запрашиваем сообщение коммита
    echo ""
    read -p "Введите сообщение коммита (или нажмите Enter для 'Update'): " COMMIT_MESSAGE
    
    if [ -z "$COMMIT_MESSAGE" ]; then
        COMMIT_MESSAGE="Update"
    fi
    
    # Коммитим изменения
    git commit -m "$COMMIT_MESSAGE"
    
    if [ $? -eq 0 ]; then
        echo "✅ Изменения закоммичены"
    else
        echo "❌ Ошибка при коммите"
        exit 1
    fi
fi

# Отправляем изменения в GitHub
echo ""
echo "📤 Отправляем изменения в GitHub..."
git push

if [ $? -eq 0 ]; then
    echo "✅ Изменения отправлены в GitHub!"
    echo ""
    echo "🌐 GitHub Pages автоматически обновит сайт через 2-5 минут"
    echo "Сайт будет доступен по адресам:"
    echo "- https://nothingitto-ops.github.io/platforma-sluchay/"
    echo "- https://platformasluchay.ru"
    echo ""
    echo "🎉 Деплой завершен!"
else
    echo "❌ Ошибка при отправке изменений"
    exit 1
fi
