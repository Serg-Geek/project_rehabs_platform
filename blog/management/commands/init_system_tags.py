"""
Django management command для инициализации системных тегов.

Использование:
    python manage.py init_system_tags
    python manage.py init_system_tags --force
"""

from django.core.management.base import BaseCommand
from blog.models import Tag


class Command(BaseCommand):
    help = 'Создает системные теги из словаря SYSTEM_TAG_ICONS'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Принудительно обновить существующие системные теги',
        )

    def handle(self, *args, **options):
        force_update = options['force']
        
        self.stdout.write('Инициализация системных тегов...')
        
        # Используем метод из модели Tag
        created_count, updated_count = Tag.initialize_system_tags()
        
        # Выводим результаты
        if created_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'✓ Создано {created_count} системных тегов')
            )
        
        if updated_count > 0:
            self.stdout.write(
                self.style.WARNING(f'↻ Обновлено {updated_count} системных тегов')
            )
        
        if created_count == 0 and updated_count == 0:
            self.stdout.write(
                self.style.NOTICE('○ Все системные теги уже существуют')
            )
        
        # Выводим итоговую статистику
        total_system_tags = Tag.objects.filter(is_system=True).count()
        self.stdout.write(
            self.style.SUCCESS(f'Всего системных тегов в БД: {total_system_tags}')
        )
        
        # Показываем список системных тегов
        system_tags = Tag.objects.filter(is_system=True).order_by('name')
        if system_tags.exists():
            self.stdout.write('\nСписок системных тегов:')
            for tag in system_tags:
                status = '✓' if tag.is_active else '✗'
                self.stdout.write(f'  {status} {tag.name} ({tag.slug})')
        
        self.stdout.write(
            self.style.SUCCESS('\n✓ Инициализация системных тегов завершена')
        ) 