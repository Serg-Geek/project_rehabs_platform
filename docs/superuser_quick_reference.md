# Краткая справка суперпользователя

## Быстрый доступ

### Вход в систему

- **URL:** `http://localhost:8000/admin/`
- **Email:** `admin@admin.com`
- **Пароль:** `123456`

## Основные разделы

### 👥 Пользователи

- **Все пользователи:** `/admin/users/user/`
- **Только персонал:** `/admin/users/user/staff-users/`
- **Логи действий:** `/admin/users/useractionlog/`

### 🔐 Система доступа

- **Уровни доступа:** `/admin/admin_logs/accesslevel/`
- **Разрешения:** `/admin/admin_logs/apppermission/`
- **Доступы пользователей:** `/admin/admin_logs/useraccess/`
- **Логи администраторов:** `/admin/admin_logs/adminactionlog/`

### 📋 Заявки

- **Все заявки:** `/admin/requests/request/`
- **История статусов:** `/admin/requests/requeststatushistory/`
- **Логи действий:** `/admin/requests/requestactionlog/`
- **Шаблоны:** `/admin/requests/requesttemplate/`

### 🏥 Медицинские учреждения

- **Учреждения:** `/admin/facilities/facility/`
- **Специалисты:** `/admin/staff/staffmember/`
- **Специализации:** `/admin/staff/specialization/`

### 📝 Контент

- **Блог:** `/admin/blog/post/`
- **Истории выздоровления:** `/admin/recovery_stories/recoverystory/`
- **Отзывы:** `/admin/reviews/review/`
- **Баннеры:** `/admin/content/banner/`

## Статусы заявок

| Статус                | Описание               |
| --------------------- | ---------------------- |
| `new`                 | Новая заявка           |
| `processing`          | В обработке            |
| `assigned`            | Назначен ответственный |
| `completed`           | Завершена              |
| `closed`              | Закрыта                |
| `treatment_completed` | Лечение завершено      |

## Роли пользователей

| Роль             | Права                |
| ---------------- | -------------------- |
| `superuser`      | Полный доступ        |
| `content_admin`  | Управление контентом |
| `requests_admin` | Обработка заявок     |
| `user`           | Базовый доступ       |

## Команды управления

### Создание суперпользователя

```bash
python manage.py shell -c "from users.models import User; user = User.objects.create_user(username='admin', email='admin@example.com', password='123456'); user.is_superuser = True; user.is_staff = True; user.role = 'superuser'; user.save(); print(f'Создан суперпользователь: {user.email}')"
```

### Резервное копирование

```bash
# Создание резервной копии
python manage.py dumpdata > backup.json

# Восстановление
python manage.py loaddata backup.json
```

### Проверка системы

```bash
python manage.py check
python manage.py check --deploy
```

### Создание тестовых данных

```bash
python manage.py shell -c "from facilities.management.commands.create_fake_data import Command; Command().handle()"
```

## Горячие клавиши

### В админ-панели

- `Ctrl + F` - поиск на странице
- `Ctrl + S` - сохранение формы
- `Tab` - переход между полями
- `Enter` - отправка формы

### В браузере

- `F5` - обновление страницы
- `Ctrl + R` - обновление страницы
- `Ctrl + Shift + R` - принудительное обновление
- `Ctrl + T` - новая вкладка

## Мониторинг

### Ежедневные проверки

1. ✅ Новые заявки
2. ✅ Новые отзывы
3. ✅ Логи действий
4. ✅ Активность пользователей

### Еженедельные задачи

1. 📊 Анализ статистики
2. 📝 Обновление контента
3. 🔒 Проверка безопасности
4. ⚙️ Обновление настроек

## Безопасность

### Рекомендации

- 🔐 Регулярно меняйте пароль
- 📱 Используйте двухфакторную аутентификацию
- 🖥️ Выходите из системы после работы
- 📋 Проверяйте логи на подозрительную активность

### Подозрительная активность

- Множественные неудачные попытки входа
- Действия с необычных IP-адресов
- Массовые изменения данных
- Попытки доступа к запрещенным разделам

## Поддержка

### Контакты

- **Email:** support@rehabs-platform.com
- **Документация:** `/docs/`
- **GitHub:** https://github.com/Serg-Geek/project_rehabs_platform

### При проблемах

1. 🔍 Проверьте логи в "Admin Action Log"
2. ⚙️ Убедитесь в корректности настроек
3. 📚 Обратитесь к документации
4. 💾 Создайте резервную копию

---

**Последнее обновление:** $(date)
**Версия системы:** Django 5.1.8
