from django.core.management.base import BaseCommand
from recovery_stories.models import RecoveryCategory
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Загружает начальные категории историй выздоровления'

    def get_unique_slug(self, base_slug, parent_slug=None):
        """
        Генерирует уникальный slug для категории
        """
        if parent_slug:
            slug = f"{parent_slug}-{base_slug}"
        else:
            slug = base_slug

        # Проверяем уникальность slug
        counter = 1
        original_slug = slug
        while RecoveryCategory.objects.filter(slug=slug).exists():
            slug = f"{original_slug}-{counter}"
            counter += 1

        return slug

    def handle(self, *args, **options):
        # Сначала удаляем все существующие категории
        RecoveryCategory.objects.all().delete()
        
        categories_data = [
            {
                'name': 'Алкогольная зависимость',
                'description': 'Истории выздоровления от алкогольной зависимости',
                'order': 1,
                'children': [
                    {
                        'name': 'Мужчины',
                        'description': 'Истории выздоровления мужчин от алкогольной зависимости',
                        'order': 1
                    },
                    {
                        'name': 'Женщины',
                        'description': 'Истории выздоровления женщин от алкогольной зависимости',
                        'order': 2
                    }
                ]
            },
            {
                'name': 'Наркотическая зависимость',
                'description': 'Истории выздоровления от наркотической зависимости',
                'order': 2,
                'children': [
                    {
                        'name': 'Мужчины',
                        'description': 'Истории выздоровления мужчин от наркотической зависимости',
                        'order': 1
                    },
                    {
                        'name': 'Женщины',
                        'description': 'Истории выздоровления женщин от наркотической зависимости',
                        'order': 2
                    }
                ]
            },
            {
                'name': 'Игровая зависимость',
                'description': 'Истории выздоровления от игровой зависимости',
                'order': 3,
                'children': [
                    {
                        'name': 'Мужчины',
                        'description': 'Истории выздоровления мужчин от игровой зависимости',
                        'order': 1
                    },
                    {
                        'name': 'Женщины',
                        'description': 'Истории выздоровления женщин от игровой зависимости',
                        'order': 2
                    }
                ]
            },
            {
                'name': 'Семейные истории',
                'description': 'Истории выздоровления семей от зависимости',
                'order': 4
            },
            {
                'name': 'Истории специалистов',
                'description': 'Истории выздоровления от зависимости специалистов в области лечения зависимостей',
                'order': 5
            }
        ]

        created_count = 0

        with transaction.atomic():
            for category_data in categories_data:
                children = category_data.pop('children', [])
                
                # Создаем родительскую категорию
                parent_slug = slugify(category_data['name'])
                category = RecoveryCategory.objects.create(
                    name=category_data['name'],
                    description=category_data['description'],
                    order=category_data['order'],
                    slug=self.get_unique_slug(parent_slug)
                )
                created_count += 1

                # Создаем дочерние категории
                for child_data in children:
                    child_base_slug = slugify(child_data['name'])
                    child = RecoveryCategory.objects.create(
                        name=child_data['name'],
                        description=child_data['description'],
                        order=child_data['order'],
                        parent=category,
                        slug=self.get_unique_slug(child_base_slug, category.slug)
                    )
                    created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Успешно создано {created_count} категорий')
        ) 