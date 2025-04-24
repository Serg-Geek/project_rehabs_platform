from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Загружает все начальные данные из фикстур'

    def handle(self, *args, **options):
        # Список фикстур в порядке загрузки
        fixtures = [
            # Базовые справочники
            'facilities/fixtures/regions.json',
            'facilities/fixtures/cities.json',
            
            # Типы организаций
            'facilities/fixtures/organization_types.json',
            
            # Основные данные
            'facilities/fixtures/clinics.json',
            'facilities/fixtures/rehab_centers.json',
            
            # Отзывы (должны загружаться после организаций)
            'facilities/fixtures/reviews.json',
        ]

        for fixture in fixtures:
            try:
                self.stdout.write(f'Загрузка данных из {fixture}...')
                call_command('loaddata', fixture)
                self.stdout.write(self.style.SUCCESS(f'✓ Данные из {fixture} успешно загружены'))
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Ошибка при загрузке {fixture}: {str(e)}')
                )
                return

        self.stdout.write(self.style.SUCCESS('✓ Все начальные данные успешно загружены')) 