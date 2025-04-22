from django.core.management.base import BaseCommand
from django.core.management import call_command
from facilities.models import OrganizationType

class Command(BaseCommand):
    help = 'Загружает все начальные данные: регионы, категории услуг, специализации и типы организаций'

    def handle(self, *args, **options):
        # Загружаем регионы и города
        self.stdout.write('Загрузка регионов и городов...')
        call_command('load_regions')
        
        # Загружаем категории услуг и базовые услуги
        self.stdout.write('Загрузка категорий услуг и базовых услуг...')
        call_command('load_initial_data')
        
        # Загружаем специализации
        self.stdout.write('Загрузка специализаций...')
        call_command('load_specializations')
        
        # Создаем типы организаций
        self.stdout.write('Создание типов организаций...')
        org_types = [
            {
                'name': 'Клиника',
                'slug': 'clinic',
                'description': 'Медицинская клиника',
                'competencies': 'Лечение пациентов'
            },
            {
                'name': 'Реабилитационный центр',
                'slug': 'rehab',
                'description': 'Реабилитационный центр',
                'competencies': 'Реабилитация пациентов'
            }
        ]
        
        for org_type_data in org_types:
            org_type, created = OrganizationType.objects.get_or_create(
                slug=org_type_data['slug'],
                defaults=org_type_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Создан тип организации: {org_type.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Тип организации уже существует: {org_type.name}'))
        
        self.stdout.write(self.style.SUCCESS('Все начальные данные успешно загружены')) 