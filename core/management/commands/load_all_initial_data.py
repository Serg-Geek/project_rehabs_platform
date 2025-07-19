from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Загружает все начальные данные из фикстур'

    def handle(self, *args, **options):
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
            
            # Словарь системных тегов с описаниями
            system_tags_data = {
                'profilaktika-i-preduprezhdenie': {
                    'name': 'Профилактика и предупреждение',
                    'description': 'Материалы по профилактике зависимостей и предупреждению рецидивов',
                    'icon': 'deps/icons/articles_tags_icons/prevention-icon.svg'
                },
                'yuridicheskaya-konsultatsiya': {
                    'name': 'Юридическая консультация',
                    'description': 'Правовые вопросы, связанные с зависимостями и реабилитацией',
                    'icon': 'deps/icons/articles_tags_icons/justice-hammer-icon.svg'
                },
                'psihiatriya': {
                    'name': 'Психиатрия',
                    'description': 'Психиатрические аспекты лечения зависимостей',
                    'icon': 'deps/icons/articles_tags_icons/psychiatrist-icon.svg'
                },
                'psihologiya': {
                    'name': 'Психология',
                    'description': 'Психологические методы лечения и поддержки',
                    'icon': 'deps/icons/articles_tags_icons/psychologist-icon.svg'
                },
                'rodstvennikam': {
                    'name': 'Родственникам',
                    'description': 'Информация для родственников зависимых людей',
                    'icon': 'deps/icons/articles_tags_icons/clients-icon.svg'
                },
                'narkomaniya': {
                    'name': 'Наркомания',
                    'description': 'Материалы по лечению наркотической зависимости',
                    'icon': 'deps/icons/articles_tags_icons/medicine-icon.svg'
                },
                'alkogolizm': {
                    'name': 'Алкоголизм',
                    'description': 'Материалы по лечению алкогольной зависимости',
                    'icon': 'deps/icons/articles_tags_icons/alcohol-icon.svg'
                },
            }
            
            created_count = 0
            updated_count = 0
            
            for slug, data in system_tags_data.items():
                tag, created = Tag.objects.get_or_create(
                    slug=slug,
                    defaults={
                        'name': data['name'],
                        'description': data['description'],
                        'icon': data['icon'],
                        'is_system': True,
                        'is_active': True
                    }
                )
                
                if created:
                    created_count += 1
                else:
                    # Обновляем существующий тег, если данные изменились
                    if (tag.name != data['name'] or 
                        tag.description != data['description'] or 
                        tag.icon != data['icon'] or 
                        not tag.is_system or 
                        not tag.is_active):
                        
                        tag.name = data['name']
                        tag.description = data['description']
                        tag.icon = data['icon']
                        tag.is_system = True
                        tag.is_active = True
                        tag.save()
                        updated_count += 1
            
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