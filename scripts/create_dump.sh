#!/bin/bash

# Скрипт создания дампа базы данных
# Использование: ./create_dump.sh [имя_файла]

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Проверка, что мы в корне проекта Django
if [ ! -f "manage.py" ]; then
    echo -e "${RED}Ошибка: manage.py не найден. Запустите скрипт из корня проекта Django.${NC}"
    exit 1
fi

# Создание папки fixtures, если её нет
mkdir -p fixtures

# Определение имени файла
if [ -n "$1" ]; then
    DUMP_FILE="fixtures/$1"
else
    # Создание дампа с временной меткой
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    DUMP_FILE="fixtures/dump_${TIMESTAMP}.json"
fi

echo -e "${YELLOW}Создание дампа: $DUMP_FILE${NC}"

# Создание дампа с кодировкой UTF-8
PYTHONIOENCODING=utf-8 python manage.py dumpdata \
  --exclude auth.permission \
  --exclude contenttypes.contenttype \
  --exclude admin.logentry \
  --exclude sessions.session \
  --indent 2 > "$DUMP_FILE"

# Проверка успешности создания
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Дамп создан успешно${NC}"
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
    echo -e "${RED}✗ Ошибка при создании дампа${NC}"
    exit 1
fi

echo -e "${GREEN}Готово!${NC}" 