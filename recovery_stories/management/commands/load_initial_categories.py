from django.core.management.base import BaseCommand
from recovery_stories.models import RecoveryCategory
from django.utils.translation import gettext_lazy as _
from django.db import transaction

class Command(BaseCommand):
    help = 'Загружает начальные категории историй выздоровления'

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
                category = RecoveryCategory.objects.create(
                    name=category_data['name'],
                    description=category_data['description'],
                    order=category_data['order']
                )
                created_count += 1

                # Создаем дочерние категории
                for child_data in children:
                    child = RecoveryCategory.objects.create(
                        name=child_data['name'],
                        description=child_data['description'],
                        order=child_data['order'],
                        parent=category
                    )
                    created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Успешно загружены категории: создано {created_count}'
            )
        ) 