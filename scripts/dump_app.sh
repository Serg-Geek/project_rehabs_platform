#!/bin/bash

# Скрипт создания дампа конкретного приложения
# Использование: ./dump_app.sh [приложение] [имя_файла]

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Проверка, что мы в корне проекта Django
if [ ! -f "manage.py" ]; then
    echo -e "${RED}Ошибка: manage.py не найден. Запустите скрипт из корня проекта Django.${NC}"
    exit 1
fi

# Проверка аргументов
if [ -z "$1" ]; then
    echo -e "${RED}Ошибка: не указано приложение${NC}"
    echo -e "${YELLOW}Использование: $0 [приложение] [имя_файла]${NC}"
    echo -e "${BLUE}Доступные приложения:${NC}"
    echo -e "  - core"
    echo -e "  - facilities"
    echo -e "  - staff"
    echo -e "  - users"
    echo -e "  - blog"
    echo -e "  - requests"
    echo -e "  - medical_services"
    echo -e "  - reviews"
    echo -e "  - recovery_stories"
    echo -e "  - content"
    exit 1
fi

APP_NAME="$1"

# Создание папки fixtures, если её нет
mkdir -p fixtures

# Определение имени файла
if [ -n "$2" ]; then
    DUMP_FILE="fixtures/$2"
else
    # Создание дампа с временной меткой
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    DUMP_FILE="fixtures/${APP_NAME}_dump_${TIMESTAMP}.json"
fi

echo -e "${YELLOW}Создание дампа приложения '$APP_NAME': $DUMP_FILE${NC}"

# Создание дампа с кодировкой UTF-8
PYTHONIOENCODING=utf-8 python manage.py dumpdata "$APP_NAME" --indent 2 > "$DUMP_FILE"

# Проверка успешности создания
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Дамп приложения '$APP_NAME' создан успешно${NC}"
    echo -e "${GREEN}Файл: $DUMP_FILE${NC}"
    echo -e "${GREEN}Размер: $(du -h "$DUMP_FILE" | cut -f1)${NC}"
    echo -e "${GREEN}Кодировка: UTF-8${NC}"
    
    # Показ статистики
    echo -e "${YELLOW}Статистика дампа:${NC}"
    echo -e "Количество объектов: $(jq length "$DUMP_FILE")"
    echo -e "Модели в дампе: $(jq -r '.[].model' "$DUMP_FILE" | sort | uniq | wc -l)"
    
    # Список моделей
    echo -e "${YELLOW}Модели в дампе:${NC}"
    jq -r '.[].model' "$DUMP_FILE" | sort | uniq | sed 's/^/  - /'
    
else
    echo -e "${RED}✗ Ошибка при создании дампа приложения '$APP_NAME'${NC}"
    echo -e "${YELLOW}Возможные причины:${NC}"
    echo -e "  - Приложение '$APP_NAME' не существует"
    echo -e "  - В приложении нет данных"
    echo -e "  - Ошибка в структуре приложения"
    exit 1
fi

echo -e "${GREEN}Готово!${NC}" 