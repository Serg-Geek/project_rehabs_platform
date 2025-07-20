# Центр помощи зависимым

Веб-платформа для поиска и выбора реабилитационных центров, клиник и частных врачей для лечения зависимостей.

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

**Быстрая установка (рекомендуется):**

```bash
python manage.py setup_project
```

Эта команда автоматически:

- Создаст необходимые папки (logs, media, static)
- Создаст необходимые папки migrations
- Применит все миграции
- Загрузит начальные данные
- Создаст суперпользователя (admin@admin.com / 123456)

**Если возникает ошибка с логированием (FileNotFoundError: logs/business.log), выполните:**

```bash
# Создайте папку logs вручную
mkdir logs

# Или используйте автоматическую установку
python manage.py setup_project
```

**Если при запуске миграций возникает ошибка "Dependency on app with no migrations: users", выполните:**

```bash
python manage.py makemigrations users
```

**Если возникает ошибка с зависимостями миграций (например, "NodeNotFoundError"), выполните:**

```bash
python manage.py makemigrations
```

Это создаст необходимые миграции и позволит корректно применить все миграции проекта.

## Решение проблем с миграциями

### Проблема: NodeNotFoundError при выполнении миграций

**Симптомы:**

```
django.db.migrations.exceptions.NodeNotFoundError: Migration requests.0007_alter_dependentrequest_status_and_more dependencies reference nonexistent parent node ('requests', '0006_remove_dependentrequest_notes_and_more')
```

**Причина:**
В репозитории отсутствуют миграции 0001-0006 для приложения `requests`, но есть миграция 0007, которая от них зависит.

**Решение:**

1. Обновите репозиторий до последней версии:

   ```bash
   git pull origin main
   ```

2. Убедитесь, что в папке `requests/migrations/` есть все файлы:

   - `0001_initial.py`
   - `0002_initial.py`
   - `0003_dependentrequest_content_type_and_more.py`
   - `0004_remove_dependentrequest_content_type_and_more.py`
   - `0005_anonymousrequest_assigned_organization_and_more.py`
   - `0006_remove_dependentrequest_notes_and_more.py`
   - `0007_alter_dependentrequest_status_and_more.py`
   - `__init__.py`

3. Если файлы отсутствуют, используйте команду автоматической установки:
   ```bash
   python manage.py setup_project
   ```

### Проблема: Dependency on app with no migrations

**Симптомы:**

```
ValueError: Dependency on app with no migrations: users
```

**Причина:**
В приложении отсутствует папка `migrations` или файл `__init__.py` в ней.

**Решение:**

1. Создайте папку migrations для проблемного приложения:

   ```bash
   mkdir users/migrations
   echo. > users/migrations/__init__.py  # Windows
   # или
   touch users/migrations/__init__.py    # Linux/Mac
   ```

2. Создайте начальную миграцию:

   ```bash
   python manage.py makemigrations users
   ```

3. Или используйте автоматическую установку:
   ```bash
   python manage.py setup_project
   ```

### Проблема: Ошибка логирования при запуске

**Симптомы:**

```
FileNotFoundError: [Errno 2] No such file or directory: 'logs/business.log'
ValueError: Unable to configure handler 'file_business'
```

**Причина:**
Папка `logs/` не существует при клонировании проекта, но система логирования пытается создать файлы логов.

**Решение:**

1. **Автоматическое решение (рекомендуется):**

   ```bash
   python manage.py setup_project
   ```

2. **Ручное решение:**

   ```bash
   # Создайте папку logs
   mkdir logs

   # Затем запустите миграции
   python manage.py migrate
   ```

### Автоматическое решение проблем

Команда `setup_project` автоматически решает большинство проблем с миграциями:

```bash
python manage.py setup_project
```

**Что делает команда:**

- ✅ Создает папки `migrations/` для всех приложений
- ✅ Создает файлы `__init__.py` в папках migrations
- ✅ Применяет все миграции
- ✅ Загружает начальные данные
- ✅ Создает суперпользователя

**Опции команды:**

```bash
python manage.py setup_project --skip-migrations  # без миграций
python manage.py setup_project --skip-data        # без загрузки данных
python manage.py setup_project --skip-superuser   # без создания админа
```

6. Загрузите начальные данные:

```bash
# Загрузка всех данных (регионы, города, учреждения, специализации, услуги, блог, истории)
python manage.py load_all_initial_data
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
├── requests/               # Заявки и обращения (новый модуль)
│   ├── models.py          # AnonymousRequest, DependentRequest, RequestNote, RequestStatusHistory
│   ├── views.py           # CBV для обработки заявок
│   └── admin.py           # Админка для управления заявками
├── medical_services/       # Медицинские услуги и категории
│   ├── models.py          # Service, ServiceCategory, FacilityService
│   ├── views.py           # CBV для списков и детальных страниц
│   └── urls.py            # Маршруты: services/, service/<slug>/, category/<slug>/
├── reviews/                # Отзывы
├── recovery_stories/       # Истории выздоровления
├── admin_logs/             # Логирование действий админов
├── content/                # Контент и настройки сайта
├── emails/                 # Шаблоны email
├── rehabs_platform/        # Основные настройки проекта
├── templates/              # HTML-шаблоны
│   ├── medical_services/   # Шаблоны услуг: service_list, service_detail, category_detail
│   └── includes/cards/     # Карточки: service_card.html
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
- Медицинские услуги через `FacilityService`

### Модуль медицинских услуг

Система управления медицинскими услугами включает:

- **Service** - услуги с описанием и категориями
- **ServiceCategory** - категории услуг с иерархией
- **FacilityService** - связь услуг с учреждениями и цены
- **ServicePrice** - история изменений цен

**Доступные страницы:**

- `/medical-services/services/` - список всех услуг с поиском и фильтрацией
- `/medical-services/service/<slug>/` - детальная страница услуги
- `/medical-services/category/<slug>/` - услуги в категории

**Навигация:** Через футер (основные категории) и хлебные крошки

### Модуль заявок (requests)

Система обработки заявок от клиентов и зависимых лиц с полным жизненным циклом:

#### Типы заявок

- **AnonymousRequest** - анонимные заявки через веб-формы, телефонные звонки
- **DependentRequest** - специализированные заявки от лиц с зависимостями

#### Возможности модуля

- Полный жизненный цикл заявок (создание → обработка → назначение → завершение)
- Система статусов и приоритетов
- Назначение учреждений и отслеживание комиссий
- Внутренние заметки и история изменений
- Детальное логирование всех действий
- Конфиденциальность для зависимых лиц

#### Статусы заявок

- Новая → В обработке → Ожидание комиссии → Комиссия получена → Лечение начато → Лечение завершено
- Дополнительные статусы: Отменена, Закрыта

## Основной функционал

### Для пациентов

- Поиск реабилитационных центров, клиник и частных врачей
- Просмотр информации об учреждениях и специалистах
- Поиск медицинских услуг по категориям
- Чтение отзывов и историй выздоровления
- Запись на консультацию
- Подача анонимных заявок

### Для реабилитационных центров и клиник

- Управление профилем учреждения
- Публикация информации о специалистах
- Управление услугами и ценами
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
- Управление медицинскими услугами и категориями
- Обработка заявок пользователей
- Назначение учреждений и отслеживание комиссий
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

### Быстрая установка проекта

```bash
# Полная автоматическая установка
python manage.py setup_project

# Установка с пропуском определенных шагов
python manage.py setup_project --skip-data  # без загрузки данных
python manage.py setup_project --skip-superuser  # без создания админа
```

### Загрузка данных

```bash
# Все данные (регионы, города, учреждения, специализации, услуги, блог, истории)
python manage.py load_all_initial_data
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

- **[Полная инструкция](docs/admin-guides/superuser_manual.md)** - подробное руководство по всем функциям системы
- **[Краткая справка](docs/admin-guides/superuser_quick_reference.md)** - быстрый доступ к основным функциям и командам
- **[Чек-листы](docs/admin-guides/superuser_checklists.md)** - ежедневные, еженедельные и ежемесячные задачи

### Для администраторов

- **[Руководство по медицинским услугам](docs/admin-guides/medical_services_guide.md)** - управление услугами и категориями
- **[Руководство по блогу](docs/admin-guides/blog_guide.md)** - управление статьями и тегами
- **[Руководство по заявкам](docs/admin-guides/admin_requests_guide.md)** - обработка заявок пользователей

### Для разработчиков

- **[Архитектура моделей](docs/architecture/architecture.md)** - описание архитектуры медицинских учреждений и модуля заявок
- **[Диаграммы проекта](docs/diagrams/README.md)** - ERD и UML диаграммы системы
- **[Руководство по тестированию](docs/testing/testing_guide.md)** - тестирование системы
- **[Анализ неиспользуемых полей](docs/development/unused_fields_analysis.md)** - оптимизация моделей

### Техническая документация

- **[Техническое задание](docs/Техническое_задание.txt)** - исходное ТЗ проекта
- **[Структура документации](docs/README.md)** - полный обзор всех документов

## Лицензия

MIT

## Авторы

- [Serg-Geek](https://github.com/Serg-Geek)

## Благодарности

- Django Software Foundation
- Bootstrap team
- Сообщество разработчиков
