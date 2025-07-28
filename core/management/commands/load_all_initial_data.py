from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    """
    Command to load all initial data from fixtures.
    """
    help = 'Загружает все начальные данные из фикстур'

    def handle(self, *args, **options):
        """
        Handle command execution.
        
        Args:
            *args: Additional arguments
            **options: Command options
        """
        # Список фикстур в порядке загрузки (соблюдаем зависимости)
        fixtures = [
            # Базовые справочники (из core)
            'core/fixtures/regions.json',
            'core/fixtures/cities.json',
            
            # Типы организаций (из facilities)
            'facilities/fixtures/organization_types.json',
            
            # Специализации (из staff) - загружаем до учреждений
            'staff/fixtures/specializations.json',
            
            # Основные данные (из facilities)
            'facilities/fixtures/clinics.json',
            'facilities/fixtures/rehab_centers.json',
            
            # Медицинские услуги (из medical_services)
            'medical_services/fixtures/categories.json',
            'medical_services/fixtures/services.json',
            'medical_services/fixtures/facility_services.json',
            
            # Отзывы (из facilities)
            'facilities/fixtures/reviews.json',
            
            # Блог (из blog)
            'blog/fixtures/blog_data.json',
            
            # Истории выздоровления (из recovery_stories)
            'recovery_stories/fixtures/recovery_stories.json',
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

        # Создаем системные теги для блога
        try:
            self.stdout.write('Создание системных тегов для блога...')
            from blog.models import Tag
            
            # Используем метод из модели для инициализации системных тегов
            created_count, updated_count = Tag.initialize_system_tags()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Системные теги созданы: {created_count} новых, {updated_count} обновлено'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Ошибка при создании системных тегов: {str(e)}')
            )

        self.stdout.write(self.style.SUCCESS('✓ Все начальные данные успешно загружены')) 