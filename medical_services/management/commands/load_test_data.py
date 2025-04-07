from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Загружает тестовые данные для медицинских услуг'

    def handle(self, *args, **options):
        self.stdout.write('Загрузка тестовых данных...')
        
        # Загружаем основные данные
        call_command('loaddata', 'test_data.json')
        self.stdout.write(self.style.SUCCESS('Основные данные загружены'))
        
        # Загружаем данные по услугам учреждений
        call_command('loaddata', 'facility_services.json')
        self.stdout.write(self.style.SUCCESS('Данные по услугам учреждений загружены'))
        
        self.stdout.write(self.style.SUCCESS('Все тестовые данные успешно загружены')) 