# Руководство по тестированию проекта Rehabs Platform

## Подготовка окружения

Перед запуском тестов убедитесь, что у вас:

1. Активировано виртуальное окружение:

   ```bash
   cd /home/svg/devSV/django/dev_env/
   source venv/bin/activate
   cd project_rehabs_platform
   ```

2. Установлены все необходимые зависимости:
   ```bash
   pip install -r requirements.txt
   ```

## Способы запуска тестов

### 1. Запуск через Django test runner

Django предоставляет встроенную утилиту для запуска тестов. Это самый простой способ:

```bash
python manage.py test
```

#### Запуск тестов для конкретного приложения:

```bash
python manage.py test requests
```

#### Запуск конкретного теста:

```bash
python manage.py test requests.tests.test_models.AnonymousRequestModelTest
```

### 2. Запуск через pytest

Pytest предоставляет расширенные возможности для запуска и отладки тестов:

```bash
pytest
```

#### Запуск тестов для конкретного приложения:

```bash
pytest requests/
```

#### Запуск с подробным выводом:

```bash
pytest -v
```

#### Запуск конкретного файла с тестами:

```bash
pytest requests/tests/test_models.py
```

#### Запуск тестов с покрытием кода:

```bash
pytest --cov=requests
```

## Структура тестов

Тесты хранятся в подпакетах `tests` каждого приложения:

```
requests/
  └── tests/
      ├── __init__.py
      ├── conftest.py        # Общие фикстуры для тестов
      ├── test_admin.py      # Тесты административного интерфейса
      ├── test_models.py     # Тесты моделей
      ├── test_urls.py       # Тесты URL-маршрутов
      └── test_views.py      # Тесты представлений
```

## Написание тестов

### Тесты моделей

Тесты моделей проверяют корректность создания объектов и их методов:

```python
from django.test import TestCase
from requests.models import AnonymousRequest

class AnonymousRequestModelTest(TestCase):
    def setUp(self):
        self.request = AnonymousRequest.objects.create(
            name="Тестовый клиент",
            phone="79991234567"
            # ...
        )

    def test_request_creation(self):
        self.assertEqual(self.request.name, "Тестовый клиент")
```

### Тесты представлений

Тесты представлений проверяют корректность обработки HTTP-запросов:

```python
from django.test import TestCase, Client
from django.urls import reverse

class ConsultationRequestViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('requests:consultation_request')

    def test_get_consultation_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
```

## Использование фикстур

Для повторного использования данных в разных тестах используйте фикстуры pytest в файле `conftest.py`:

```python
import pytest
from requests.models import AnonymousRequest

@pytest.fixture
def anonymous_request():
    return AnonymousRequest.objects.create(
        name="Тестовый клиент",
        phone="79991234567"
        # ...
    )
```

## Рекомендации

1. Всегда запускайте тесты перед созданием pull request
2. Старайтесь писать тесты при создании новых функций
3. Поддерживайте высокое покрытие кода тестами
4. Используйте описательные имена для тестов
5. Следуйте принципу AAA (Arrange-Act-Assert) при написании тестов
