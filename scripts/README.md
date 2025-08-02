# Скрипты для работы с дампами

Эта папка содержит скрипты для автоматизации работы с дампами базы данных.

## Быстрое использование

### Linux/Mac

```bash
# Создание дампа
./scripts/create_dump.sh

# Восстановление из дампа
./scripts/restore_dump.sh

# Дамп конкретного приложения
./scripts/dump_app.sh medical_services
```

### Windows

```cmd
# Создание дампа
scripts\create_dump.bat

# Восстановление из дампа
scripts\restore_dump.bat

# Дамп конкретного приложения
scripts\dump_app.bat medical_services
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

### 🖥️ Кроссплатформенность

- **Linux/Mac**: `.sh` скрипты (bash)
- **Windows**: `.bat` скрипты (cmd)

## Подробная документация

См. [project_docs/scripts/README.md](../project_docs/scripts/README.md) для полного описания всех возможностей.

## Структура

```
scripts/
├── create_dump.sh      # Создание полного дампа (Linux/Mac)
├── create_dump.bat     # Создание полного дампа (Windows)
├── restore_dump.sh     # Восстановление из дампа (Linux/Mac)
├── restore_dump.bat    # Восстановление из дампа (Windows)
├── dump_app.sh         # Дамп конкретного приложения (Linux/Mac)
├── dump_app.bat        # Дамп конкретного приложения (Windows)
└── README.md           # Этот файл
```

## Примеры

### Linux/Mac

```bash
# Создать дамп перед изменениями
./scripts/create_dump.sh backup_before_changes.json

# Восстановить после ошибок
./scripts/restore_dump.sh fixtures/backup_before_changes.json

# Дамп только медицинских услуг
./scripts/dump_app.sh medical_services
```

### Windows

```cmd
# Создать дамп перед изменениями
scripts\create_dump.bat backup_before_changes.json

# Восстановить после ошибок
scripts\restore_dump.bat fixtures\backup_before_changes.json

# Дамп только медицинских услуг
scripts\dump_app.bat medical_services
```

## Требования

### Linux/Mac

- **Django проект** - скрипты должны запускаться из корня проекта
- **Python** - для выполнения команд Django
- **jq** - для анализа JSON файлов (опционально)
- **bash** - для выполнения скриптов

### Windows

- **Django проект** - скрипты должны запускаться из корня проекта
- **Python** - для выполнения команд Django
- **cmd** - для выполнения скриптов

## Установка зависимостей

### Ubuntu/Debian:

```bash
sudo apt install jq
```

### CentOS/RHEL:

```bash
sudo yum install jq
```

### macOS:

```bash
brew install jq
```

### Windows:

jq не требуется, используется встроенный Python для анализа JSON.

## Безопасность

⚠️ **Внимание:** Скрипты `restore_dump` удаляют текущую базу данных!

- Всегда создавайте резервные копии перед восстановлением
- Проверяйте содержимое дампа перед загрузкой
- Используйте тестовую среду для проверки
