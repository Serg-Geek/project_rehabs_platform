# Скрипты для работы с дампами

Эта папка содержит скрипты для автоматизации работы с дампами базы данных.

## Быстрое использование

### Создание дампа

```bash
./scripts/create_dump.sh
```

### Восстановление из дампа

```bash
./scripts/restore_dump.sh
```

### Дамп конкретного приложения

```bash
./scripts/dump_app.sh medical_services
```

## Особенности

### 🔤 Кодировка UTF-8

Все скрипты создают дампы в кодировке UTF-8 для корректного отображения русского текста.

### 📊 Статистика

Скрипты показывают:

- Размер созданного файла
- Количество объектов
- Список моделей в дампе
- Кодировку файла

## Подробная документация

См. [project_docs/scripts/README.md](../project_docs/scripts/README.md) для полного описания всех возможностей.

## Структура

```
scripts/
├── create_dump.sh      # Создание полного дампа
├── restore_dump.sh     # Восстановление из дампа
├── dump_app.sh         # Дамп конкретного приложения
└── README.md           # Этот файл
```

## Примеры

```bash
# Создать дамп перед изменениями
./scripts/create_dump.sh backup_before_changes.json

# Восстановить после ошибок
./scripts/restore_dump.sh fixtures/backup_before_changes.json

# Дамп только медицинских услуг
./scripts/dump_app.sh medical_services
```
