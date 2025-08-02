#!/bin/bash

# Скрипт восстановления базы данных из дампа
# Использование: ./restore_dump.sh [путь_к_дампу]

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

# Определение файла дампа
if [ -n "$1" ]; then
    DUMP_FILE="$1"
else
    # Поиск последнего дампа
    LATEST_DUMP=$(ls -t fixtures/dump_*.json 2>/dev/null | head -1)
    if [ -z "$LATEST_DUMP" ]; then
        echo -e "${RED}Ошибка: дамп не найден. Укажите путь к файлу дампа.${NC}"
        echo -e "${YELLOW}Использование: $0 [путь_к_дампу]${NC}"
        exit 1
    fi
    DUMP_FILE="$LATEST_DUMP"
fi

# Проверка существования файла
if [ ! -f "$DUMP_FILE" ]; then
    echo -e "${RED}Ошибка: файл $DUMP_FILE не найден${NC}"
    exit 1
fi

echo -e "${YELLOW}Восстановление из дампа: $DUMP_FILE${NC}"
echo -e "${BLUE}Размер дампа: $(du -h "$DUMP_FILE" | cut -f1)${NC}"

# Подтверждение действия
echo -e "${YELLOW}ВНИМАНИЕ: Это действие удалит текущую базу данных!${NC}"
read -p "Продолжить? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Операция отменена${NC}"
    exit 0
fi

echo -e "${YELLOW}Начинаем восстановление...${NC}"

# Удалить старую БД
echo -e "${BLUE}Удаление старой базы данных...${NC}"
rm -f db.sqlite3

# Создать новую БД
echo -e "${BLUE}Создание новой базы данных...${NC}"
python manage.py migrate

# Проверка успешности миграций
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Ошибка при создании базы данных${NC}"
    exit 1
fi

# Загрузить дамп
echo -e "${BLUE}Загрузка данных из дампа...${NC}"
python manage.py loaddata "$DUMP_FILE"

# Проверка успешности загрузки
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Восстановление завершено успешно${NC}"
    
    # Показ статистики
    echo -e "${YELLOW}Статистика восстановления:${NC}"
    echo -e "Загружено объектов: $(jq length "$DUMP_FILE")"
    echo -e "Модели: $(jq -r '.[].model' "$DUMP_FILE" | sort | uniq | wc -l)"
    
    # Список загруженных моделей
    echo -e "${YELLOW}Загруженные модели:${NC}"
    jq -r '.[].model' "$DUMP_FILE" | sort | uniq | sed 's/^/  - /'
    
else
    echo -e "${RED}✗ Ошибка при загрузке дампа${NC}"
    echo -e "${YELLOW}Попробуйте очистить ContentType:${NC}"
    echo -e "${BLUE}python manage.py shell -c \"from django.contrib.contenttypes.models import ContentType; ContentType.objects.all().delete()\"${NC}"
    echo -e "${BLUE}python manage.py loaddata \"$DUMP_FILE\"${NC}"
    exit 1
fi

echo -e "${GREEN}Готово! База данных восстановлена.${NC}" 