# Архитектура моделей медицинских учреждений

## Обзор

Система медицинских учреждений построена на принципе наследования от абстрактной базовой модели `AbstractMedicalFacility`. Это обеспечивает единообразие в работе с различными типами учреждений и переиспользование кода.

## Иерархия моделей

```
AbstractMedicalFacility (абстрактная базовая модель)
├── Clinic (клиники)
├── RehabCenter (реабилитационные центры)
└── PrivateDoctor (частные врачи)
```

## AbstractMedicalFacility

### Общие поля для всех учреждений

- `name` - название учреждения
- `slug` - URL-идентификатор
- `organization_type` - тип организации (FK к OrganizationType)
- `description` - описание
- `address` - адрес
- `phone` - телефон
- `email` - email
- `website` - веб-сайт
- `license_number` - номер лицензии
- `is_active` - активность
- `city` - город (FK к City)

### Общие возможности

- **Отзывы** - система рейтингов и отзывов
- **Документы** - лицензии, сертификаты, аккредитации
- **Изображения** - галереи и фотографии
- **Специалисты** - привязка к учреждению через GenericForeignKey

## OrganizationType

Типы организаций в системе:

- `clinic` - Клиника
- `rehabilitation-center` - Реабилитационный центр
- `private-doctor` - Частный врач

## Clinic

### Специфические поля

- `emergency_support` - экстренная помощь
- `has_hospital` - наличие стационара

### Использование

Клиники предназначены для стационарного и амбулаторного лечения с возможностью экстренной помощи.

## RehabCenter

### Специфические поля

- `capacity` - вместимость
- `program_duration` - длительность программы (дней)
- `min_price` - минимальная цена
- `accommodation_conditions` - условия проживания

### Использование

Реабилитационные центры специализируются на длительных программах восстановления с проживанием.

## PrivateDoctor

### Специфические поля

#### Персональная информация

- `first_name`, `last_name`, `middle_name` - ФИО
- `specializations` - специализации (M2M к Specialization)
- `experience_years` - стаж
- `education` - образование
- `biography` - биография
- `achievements` - достижения
- `photo` - фото

#### Место приема

- `office_description` - описание кабинета
- `parking_available` - наличие парковки
- `wheelchair_accessible` - доступность для инвалидных колясок

#### График работы

- `schedule` - график работы
- `home_visits` - выезд на дом
- `emergency_available` - экстренная помощь
- `weekend_work` - работа в выходные

#### Финансовые аспекты

- `consultation_price` - стоимость консультации
- `home_visit_price` - стоимость выезда на дом
- `insurance_accepted` - принимает страховку

#### Лицензирование

- `license_issue_date` - дата выдачи лицензии
- `license_expiry_date` - срок действия лицензии

#### Дополнительные возможности

- `online_consultations` - онлайн консультации
- `video_consultations` - видеоконсультации
- `special_equipment` - специальное оборудование

### Использование

Частные врачи - это индивидуальные специалисты, не привязанные к конкретным учреждениям.

## Преимущества архитектуры

### 1. Единообразие

- Все учреждения имеют одинаковую базовую структуру
- Единый подход к отзывам, документам, изображениям

### 2. Переиспользование кода

- Общие поля и методы в базовой модели
- Единая админка для всех типов учреждений

### 3. Расширяемость

- Легко добавить новые типы учреждений
- Изменения в базовой модели применяются ко всем наследникам

### 4. Консистентность

- Одинаковый API для всех учреждений
- Единые URL-паттерны и представления

## Миграции

При добавлении новых типов учреждений:

1. Создать новый тип в `OrganizationType`
2. Создать модель, наследующую от `AbstractMedicalFacility`
3. Добавить специфические поля
4. Создать миграцию
5. Обновить админку и представления

## Примеры использования

### Получение всех активных учреждений

```python
from facilities.models import Clinic, RehabCenter, PrivateDoctor

all_facilities = list(Clinic.objects.filter(is_active=True)) + \
                 list(RehabCenter.objects.filter(is_active=True)) + \
                 list(PrivateDoctor.objects.filter(is_active=True))
```

### Получение учреждений по типу

```python
from facilities.models import OrganizationType

clinic_type = OrganizationType.objects.get(slug='clinic')
clinics = Clinic.objects.filter(organization_type=clinic_type)
```

### Работа с отзывами

```python
# Все отзывы учреждения
facility.reviews.all()

# Средний рейтинг
facility.average_rating

# Количество отзывов
facility.reviews_count
```
