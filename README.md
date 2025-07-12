# Платформа реабилитационных центров

Веб-платформа для поиска и выбора реабилитационных центров и клиник.

## Технологии

### Backend

- Python 3.11+
- Django 5.1.8
- SQLite (разработка) / PostgreSQL (продакшн)

### Frontend

- HTML5
- CSS3
- JavaScript
- Bootstrap 5

### Дополнительные библиотеки

- django-cleanup - автоматическая очистка файлов
- django-ckeditor-5 - WYSIWYG редактор
- Pillow - обработка изображений
- Faker - генерация тестовых данных
- transliterate - транслитерация

## Установка

1. Клонируйте репозиторий:

```bash
git clone https://github.com/Serg-Geek/project_rehabs_platform.git
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

4. Создайте файл с секретным ключом:

```bash
# Создайте файл rehabs_platform/secret.py
echo "MY_SECRET_KEY = 'ваш-секретный-ключ-здесь'" > rehabs_platform/secret.py
```

5. Примените миграции:

```bash
python manage.py migrate
```

6. Загрузите начальные данные:

```bash
# Загрузка всех данных
python manage.py load_all_initial_data

# Загрузка специализаций
python manage.py loaddata staff/fixtures/specializations.json

# Загрузка категорий историй выздоровления
python manage.py load_initial_categories
```

7. Создайте суперпользователя:

```bash
python manage.py createsuperuser
```

**Важно:** Вход в систему осуществляется по email, а не по username!

8. Запустите сервер разработки:

```bash
python manage.py runserver
```

## Структура проекта

```
project_rehabs_platform/
├── core/                   # Базовые модели (регионы, города)
├── facilities/             # Медицинские учреждения
│   ├── models.py          # Модели: AbstractMedicalFacility, Clinic, RehabCenter, PrivateDoctor
│   ├── admin.py           # Админка для всех типов учреждений
│   └── management/        # Команды управления данными
├── staff/                  # Специалисты и специализации
├── users/                  # Пользователи и аутентификация
├── blog/                   # Блог и статьи
├── requests/               # Заявки и обращения
├── medical_services/       # Медицинские услуги
├── reviews/                # Отзывы
├── recovery_stories/       # Истории выздоровления
├── admin_logs/             # Логирование действий админов
├── content/                # Контент и настройки сайта
├── emails/                 # Шаблоны email
├── rehabs_platform/        # Основные настройки проекта
├── templates/              # HTML-шаблоны
├── static/                 # Статические файлы
├── media/                  # Загружаемые файлы
└── docs/                   # Документация
```

### Архитектура моделей медицинских учреждений

Все медицинские учреждения наследуют от абстрактной модели `AbstractMedicalFacility`:

- **Clinic** - клиники с полями `emergency_support`, `has_hospital`
- **RehabCenter** - реабилитационные центры с полями `capacity`, `program_duration`, `min_price`
- **PrivateDoctor** - частнопрактикующие врачи с персональными данными и графиком работы

Общие возможности для всех учреждений:

- Отзывы и рейтинги
- Документы и лицензии
- Изображения и галереи
- Специалисты и их профили

## Основной функционал

### Для пациентов

- Поиск реабилитационных центров, клиник и частных врачей
- Просмотр информации об учреждениях и специалистах
- Чтение отзывов и историй выздоровления
- Запись на консультацию
- Подача анонимных заявок

### Для реабилитационных центров и клиник

- Управление профилем учреждения
- Публикация информации о специалистах
- Управление отзывами
- Статистика посещений

### Для частных врачей

- Создание персонального профиля
- Управление графиком работы и услугами
- Публикация информации о специализациях
- Получение отзывов от пациентов

### Для администраторов

- Управление пользователями и ролями
- Модерация контента
- Управление заявками
- Аналитика и отчеты
- Система логирования действий

## Система ролей

- **Суперпользователь** - полный доступ ко всем функциям
- **Администратор контента** - управление контентом сайта
- **Администратор заявок** - обработка заявок пользователей
- **Пользователь** - базовый доступ

## Вход в систему

**Важно:** Вход осуществляется по email, а не по username!

### Суперпользователь по умолчанию:

- **Email:** `admin@admin.com`
- **Пароль:** `123456`

### Создание нового суперпользователя:

```bash
# Через Django shell
python manage.py shell -c "from users.models import User; user = User.objects.create_user(username='admin', email='admin@example.com', password='123456'); user.is_superuser = True; user.is_staff = True; user.role = 'superuser'; user.save(); print(f'Создан суперпользователь: {user.email}')"
```

**Примечание:** Замените `admin@example.com` и `123456` на нужные email и пароль.

### Изменение роли существующего пользователя на суперпользователя:

```bash
# Через Django shell
python manage.py shell -c "from users.models import User; user = User.objects.get(email='user@example.com'); user.is_superuser = True; user.is_staff = True; user.role = 'superuser'; user.save(); print(f'Пользователь {user.email} теперь суперпользователь')"
```

**Примечание:** Замените `user@example.com` на email пользователя, которому нужно дать права суперпользователя.

## Команды управления

### Загрузка данных

```bash
# Все данные
python manage.py load_all_initial_data

# Специализации
python manage.py loaddata staff/fixtures/specializations.json

# Категории историй
python manage.py load_initial_categories
```

### Тестирование

```bash
# Запуск тестов
python manage.py test

# Создание тестовых данных
python manage.py shell -c "from facilities.management.commands.create_fake_data import Command; Command().handle()"
```

## Разработка

### Создание миграций

```bash
python manage.py makemigrations
python manage.py migrate
```

### Создание суперпользователя

```bash
python manage.py createsuperuser
```

### Проверка проекта

```bash
python manage.py check
python manage.py check --deploy
```

## Документация

### Для суперпользователей

- **[Полная инструкция](docs/superuser_manual.md)** - подробное руководство по всем функциям системы
- **[Краткая справка](docs/superuser_quick_reference.md)** - быстрый доступ к основным функциям и командам
- **[Чек-листы](docs/superuser_checklists.md)** - ежедневные, еженедельные и ежемесячные задачи

### Для разработчиков

- **[Архитектура моделей](docs/architecture.md)** - описание архитектуры медицинских учреждений
- **[API документация](docs/api.md)** - описание API endpoints
- **[Руководство по развертыванию](docs/deployment.md)** - инструкции по развертыванию

## Лицензия

MIT

## Авторы

- [Serg-Geek](https://github.com/Serg-Geek)

## Благодарности

- Django Software Foundation
- Bootstrap team
- Сообщество разработчиков
