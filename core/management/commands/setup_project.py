from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
import os
from pathlib import Path


class Command(BaseCommand):
    help = 'Автоматическая установка проекта с нуля'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-migrations',
            action='store_true',
            help='Пропустить применение миграций',
        )
        parser.add_argument(
            '--skip-data',
            action='store_true',
            help='Пропустить загрузку данных',
        )
        parser.add_argument(
            '--skip-superuser',
            action='store_true',
            help='Пропустить создание суперпользователя',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Начинаем установку проекта...'))
        
        # 1. Создаем необходимые папки
        self.create_required_folders()
        
        # 2. Проверяем и создаем папки migrations
        self.create_migrations_folders()
        
        # 3. Применяем миграции
        if not options['skip_migrations']:
            self.apply_migrations()
        
        # 4. Загружаем данные
        if not options['skip_data']:
            self.load_initial_data()
        
        # 5. Создаем суперпользователя
        if not options['skip_superuser']:
            self.create_superuser()
        
        self.stdout.write(self.style.SUCCESS('✅ Установка проекта завершена успешно!'))
        self.stdout.write(self.style.SUCCESS('🌐 Запустите сервер: python manage.py runserver'))

    def create_required_folders(self):
        """Создает необходимые папки для работы проекта"""
        self.stdout.write('📁 Создаем необходимые папки...')
        
        required_folders = [
            'logs',
            'media',
            'static',
        ]
        
        for folder in required_folders:
            folder_path = Path(settings.BASE_DIR) / folder
            folder_path.mkdir(exist_ok=True)
            self.stdout.write(f'  ✓ Папка {folder} создана/проверена')

    def create_migrations_folders(self):
        """Создает папки migrations и __init__.py файлы"""
        self.stdout.write('📁 Проверяем папки migrations...')
        
        apps = [
            'core', 'facilities', 'staff', 'users', 'blog', 'requests',
            'medical_services', 'reviews', 'recovery_stories', 'admin_logs', 'content'
        ]
        
        for app in apps:
            migrations_dir = Path(settings.BASE_DIR) / app / 'migrations'
            init_file = migrations_dir / '__init__.py'
            
            # Создаем папку migrations если её нет
            migrations_dir.mkdir(exist_ok=True)
            
            # Создаем __init__.py если его нет
            if not init_file.exists():
                init_file.touch()
                self.stdout.write(f'  ✓ Создан {init_file}')
            else:
                self.stdout.write(f'  ✓ {init_file} уже существует')

    def apply_migrations(self):
        """Применяет миграции"""
        self.stdout.write('🔄 Применяем миграции...')
        
        # Сначала создаем недостающие миграции
        self.create_missing_migrations()
        
        try:
            call_command('migrate', verbosity=0)
            self.stdout.write(self.style.SUCCESS('  ✓ Миграции применены успешно'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ✗ Ошибка при применении миграций: {e}'))
            raise

    def create_missing_migrations(self):
        """Создает недостающие миграции для всех приложений"""
        self.stdout.write('📝 Создаем недостающие миграции...')
        
        apps = [
            'core', 'facilities', 'staff', 'users', 'blog', 'requests',
            'medical_services', 'reviews', 'recovery_stories', 'admin_logs', 'content'
        ]
        
        for app in apps:
            try:
                # Проверяем, есть ли миграции в приложении
                migrations_dir = Path(settings.BASE_DIR) / app / 'migrations'
                migration_files = list(migrations_dir.glob('0*.py'))
                
                if not migration_files:
                    self.stdout.write(f'  📋 Создаем миграции для {app}...')
                    call_command('makemigrations', app, verbosity=0)
                    self.stdout.write(f'  ✓ Миграции для {app} созданы')
                else:
                    self.stdout.write(f'  ✓ Миграции для {app} уже существуют')
                    
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  ⚠ Ошибка при создании миграций для {app}: {e}'))
                # Продолжаем с другими приложениями
                continue

    def load_initial_data(self):
        """Загружает начальные данные"""
        self.stdout.write('📊 Загружаем начальные данные...')
        
        # Проверяем наличие резервной копии БД
        backup_file = Path(settings.BASE_DIR) / 'db_backup.json'
        
        if backup_file.exists():
            try:
                call_command('loaddata', 'db_backup.json', verbosity=0)
                self.stdout.write(self.style.SUCCESS('  ✓ Данные загружены из db_backup.json'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  ⚠ Ошибка при загрузке db_backup.json: {e}'))
                self.stdout.write('  📋 Пробуем загрузить данные из фикстур...')
                self.load_from_fixtures()
        else:
            self.stdout.write('  📋 Резервная копия не найдена, загружаем из фикстур...')
            self.load_from_fixtures()

    def load_from_fixtures(self):
        """Загружает данные из фикстур"""
        try:
            call_command('load_all_initial_data', verbosity=0)
            self.stdout.write(self.style.SUCCESS('  ✓ Данные загружены из фикстур'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  ⚠ Ошибка при загрузке фикстур: {e}'))

    def create_superuser(self):
        """Создает суперпользователя по умолчанию"""
        self.stdout.write('👤 Создаем суперпользователя...')
        
        try:
            from users.models import User
            
            # Проверяем, есть ли уже суперпользователь
            if User.objects.filter(is_superuser=True).exists():
                self.stdout.write('  ✓ Суперпользователь уже существует')
                return
            
            # Создаем суперпользователя по умолчанию
            user = User.objects.create_user(
                username='admin',
                email='admin@admin.com',
                password='123456'
            )
            user.is_superuser = True
            user.is_staff = True
            user.role = 'superuser'
            user.save()
            
            self.stdout.write(self.style.SUCCESS('  ✓ Суперпользователь создан'))
            self.stdout.write('    Email: admin@admin.com')
            self.stdout.write('    Пароль: 123456')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ✗ Ошибка при создании суперпользователя: {e}'))
            self.stdout.write('  💡 Создайте суперпользователя вручную: python manage.py createsuperuser') 