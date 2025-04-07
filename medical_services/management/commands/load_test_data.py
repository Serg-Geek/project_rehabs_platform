from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Загрузка тестовых данных в базу данных'

    def handle(self, *args, **options):
        # Загрузка регионов
        self.stdout.write('Загрузка регионов...')
        call_command('loaddata', 'core/fixtures/regions.json')
        
        # Загрузка городов
        self.stdout.write('Загрузка городов...')
        call_command('loaddata', 'core/fixtures/cities.json')
        
        # Загрузка типов организаций
        self.stdout.write('Загрузка типов организаций...')
        call_command('loaddata', 'facilities/fixtures/organization_types.json')
        
        # Загрузка специалистов
        self.stdout.write('Загрузка специалистов...')
        call_command('loaddata', 'staff/fixtures/test_data.json')
        
        # Загрузка реабилитационных центров
        self.stdout.write('Загрузка реабилитационных центров...')
        call_command('loaddata', 'facilities/fixtures/rehab_centers.json')
        
        # Загрузка клиник
        self.stdout.write('Загрузка клиник...')
        call_command('loaddata', 'facilities/fixtures/clinics.json')
        
        # Загрузка категорий услуг
        self.stdout.write('Загрузка категорий услуг...')
        call_command('loaddata', 'medical_services/fixtures/categories.json')
        
        # Загрузка медицинских услуг
        self.stdout.write('Загрузка медицинских услуг...')
        call_command('loaddata', 'medical_services/fixtures/services.json')
        
        # Загрузка услуг для учреждений
        self.stdout.write('Загрузка услуг для учреждений...')
        call_command('loaddata', 'medical_services/fixtures/facility_services.json')
        
        self.stdout.write(self.style.SUCCESS('Все тестовые данные успешно загружены')) 