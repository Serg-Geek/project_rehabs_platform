# Платформа реабилитационных центров

Веб-платформа для поиска и выбора реабилитационных центров и клиник.

## Технологии

### Backend

- Python 3.11
- Django 5.1.8
- PostgreSQL 15

### Frontend

- HTML5
- CSS3
- JavaScript
- Bootstrap 5

## Установка

1. Клонируйте репозиторий:

```bash
git clone https://github.com/yourusername/project_rehabs_platform.git
cd project_rehabs_platform
```

2. Создайте и активируйте виртуальное окружение:

```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
# или
venv\Scripts\activate  # для Windows
```

3. Установите зависимости:

```bash
pip install -r requirements.txt
```

4. Создайте файл с переменными окружения:

```bash
cp .env.example .env
```

Отредактируйте файл .env, указав необходимые настройки.

5. Примените миграции:

```bash
python manage.py migrate
```

6. Загрузите начальные данные:

```bash
python manage.py load_all_initial_data
```

Для загрузки отдельных фикстур используйте команду:

```bash
# Загрузка специализаций
python manage.py loaddata staff/fixtures/specializations.json

# Загрузка других фикстур
python manage.py loaddata <path_to_fixture>
```

7. Создайте суперпользователя:

```bash
python manage.py createsuperuser
```

8. Запустите сервер разработки:

```bash
python manage.py runserver
```

## Структура проекта

```
project_rehabs_platform/
├── apps/                    # Django-приложения
│   ├── core/               # Базовые модели и функционал
│   ├── facilities/         # Медицинские учреждения
│   ├── staff/              # Специалисты
│   └── ...
├── config/                 # Конфигурация проекта
├── templates/              # HTML-шаблоны
├── static/                 # Статические файлы
└── ...
```

## Основной функционал

### Для пациентов

- Поиск реабилитационных центров и клиник
- Просмотр информации об учреждениях
- Чтение отзывов
- Запись на консультацию

### Для реабилитационных центров

- Управление профилем учреждения
- Публикация информации о специалистах
- Управление отзывами
- Статистика посещений

### Для администраторов

- Управление пользователями
- Модерация контента
- Аналитика и отчеты

## Лицензия

MIT

## Авторы

- [Ваше имя](https://github.com/yourusername)

## Благодарности

- Django Software Foundation
- Bootstrap team
- Сообщество разработчиков
