#!/bin/bash

# Скрипт для создания репозитория на GitHub и деплоя сайта platforma.sluchay

echo "🚀 Создание репозитория и деплой сайта platforma.sluchay"
echo "=================================================="

# Проверяем, что мы в правильной директории
if [ ! -f "index.html" ]; then
    echo "❌ Ошибка: index.html не найден. Убедитесь, что вы находитесь в папке web/"
    exit 1
fi

# Проверяем статус git
if [ ! -d ".git" ]; then
    echo "❌ Ошибка: Git репозиторий не инициализирован"
    exit 1
fi

echo "✅ Git репозиторий найден"

# Проверяем, есть ли коммиты
if ! git rev-parse HEAD >/dev/null 2>&1; then
    echo "❌ Ошибка: Нет коммитов в репозитории"
    exit 1
fi

echo "✅ Коммиты найдены"

echo ""
echo "📋 Инструкции для создания репозитория на GitHub:"
echo "=================================================="
echo "1. Перейдите на https://github.com/new"
echo "2. Введите имя репозитория: platforma-sluchay"
echo "3. Выберите 'Public' (публичный)"
echo "4. НЕ ставьте галочки на 'Add a README file', 'Add .gitignore', 'Choose a license'"
echo "5. Нажмите 'Create repository'"
echo ""
echo "После создания репозитория, GitHub покажет команды для подключения."
echo "Скопируйте URL репозитория (он будет выглядеть как: https://github.com/YOUR_USERNAME/platforma-sluchay.git)"
echo ""

read -p "Введите URL вашего нового репозитория: " REPO_URL

if [ -z "$REPO_URL" ]; then
    echo "❌ URL репозитория не введен"
    exit 1
fi

echo ""
echo "🔗 Подключаем локальный репозиторий к GitHub..."

# Добавляем remote origin
git remote add origin "$REPO_URL"

# Проверяем, что remote добавлен
if ! git remote get-url origin >/dev/null 2>&1; then
    echo "❌ Ошибка при добавлении remote origin"
    exit 1
fi

echo "✅ Remote origin добавлен: $REPO_URL"

# Пушим код в репозиторий
echo ""
echo "📤 Отправляем код в GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo "✅ Код успешно отправлен в GitHub!"
else
    echo "❌ Ошибка при отправке кода"
    exit 1
fi

echo ""
echo "🌐 Настройка GitHub Pages:"
echo "=========================="
echo "1. Перейдите в настройки репозитория: $REPO_URL/settings"
echo "2. В левом меню найдите 'Pages'"
echo "3. В разделе 'Source' выберите 'Deploy from a branch'"
echo "4. В выпадающем списке выберите 'main'"
echo "5. В папке выберите '/' (root)"
echo "6. Нажмите 'Save'"
echo ""
echo "После этого ваш сайт будет доступен по адресу:"
echo "https://YOUR_USERNAME.github.io/platforma-sluchay/"
echo ""

# Проверяем наличие CNAME файла
if [ -f "CNAME" ]; then
    echo "📝 CNAME файл найден:"
    cat CNAME
    echo ""
    echo "Если у вас есть домен, он будет автоматически настроен."
fi

echo "🎉 Готово! Ваш сайт platforma.sluchay готов к деплою!"
echo ""
echo "Следующие шаги:"
echo "1. Настройте GitHub Pages (см. инструкции выше)"
echo "2. Подождите несколько минут для деплоя"
echo "3. Проверьте работу сайта"
echo ""
echo "Для обновления сайта в будущем используйте:"
echo "git add . && git commit -m 'Update' && git push"
