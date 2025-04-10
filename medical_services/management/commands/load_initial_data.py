from django.core.management.base import BaseCommand
from django.core.management import call_command
from medical_services.models import ServiceCategory, Service

class Command(BaseCommand):
    help = 'Загружает начальные данные для категорий услуг и создает базовые услуги'

    def handle(self, *args, **options):
        self.stdout.write('Загрузка начальных данных...')
        
        # Загружаем фикстуры
        call_command('loaddata', 'medical_services/fixtures/initial_service_categories.json')
        
        # Создаем базовые услуги для каждой категории
        alcoholism_category = ServiceCategory.objects.get(slug='lechenie-alkogolizma')
        drug_addiction_category = ServiceCategory.objects.get(slug='lechenie-narkomanii')
        other_category = ServiceCategory.objects.get(slug='drugie-uslugi')
        
        # Услуги для лечения алкоголизма
        alcoholism_services = [
            'Реабилитация',
            'Детоксикация',
            'Вывод из запоя',
            'Кодирование',
            'Лечение в стационаре',
            'Амбулаторное лечение',
            'Программы лечения'
        ]
        
        # Услуги для лечения наркомании
        drug_addiction_services = [
            'Реабилитация',
            'Детоксикация',
            'Снятие ломки',
            'Кодирование',
            'УБОД',
            'Лечение в стационаре',
            'Амбулаторное лечение',
            'Программы лечения'
        ]
        
        # Другие услуги
        other_services = [
            'Интернет зависимость',
            'Игровая зависимость',
            'Ресоциализация',
            'Адвокатская помощь',
            'Лечение за границей',
            'Психологическая помощь',
            'Психиатрическая помощь'
        ]
        
        # Создаем услуги
        for service_name in alcoholism_services:
            Service.objects.get_or_create(
                name=service_name,
                defaults={
                    'description': f'Услуга по лечению алкоголизма: {service_name}',
                    'duration': 60,
                    'is_active': True
                }
            )[0].categories.add(alcoholism_category)
            
        for service_name in drug_addiction_services:
            Service.objects.get_or_create(
                name=service_name,
                defaults={
                    'description': f'Услуга по лечению наркомании: {service_name}',
                    'duration': 60,
                    'is_active': True
                }
            )[0].categories.add(drug_addiction_category)
            
        for service_name in other_services:
            Service.objects.get_or_create(
                name=service_name,
                defaults={
                    'description': f'Дополнительная услуга: {service_name}',
                    'duration': 60,
                    'is_active': True
                }
            )[0].categories.add(other_category)
        
        self.stdout.write(self.style.SUCCESS('Начальные данные успешно загружены!')) 