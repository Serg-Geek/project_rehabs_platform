from django.core.management.base import BaseCommand
from medical_services.models import ServiceCategory, Service

class Command(BaseCommand):
    help = 'Загружает начальные данные: категории услуг и базовые услуги'

    def handle(self, *args, **options):
        # Создаем категории услуг
        categories_data = [
            {
                'name': 'Лечение алкоголизма',
                'slug': 'lechenie-alkogolizma',
                'description': 'Услуги по лечению алкогольной зависимости'
            },
            {
                'name': 'Лечение наркомании',
                'slug': 'lechenie-narkomanii',
                'description': 'Услуги по лечению наркотической зависимости'
            },
            {
                'name': 'Другие услуги',
                'slug': 'drugie-uslugi',
                'description': 'Прочие медицинские услуги'
            }
        ]

        for category_data in categories_data:
            category, created = ServiceCategory.objects.get_or_create(
                slug=category_data['slug'],
                defaults=category_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Создана категория: {category.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Категория уже существует: {category.name}')
                )

        # Создаем базовые услуги для каждой категории
        services_data = [
            {
                'name': 'Консультация нарколога',
                'slug': 'konsultaciya-narkologa',
                'description': 'Первичная консультация врача-нарколога',
                'duration': 60,
                'categories': ['lechenie-alkogolizma', 'lechenie-narkomanii']
            },
            {
                'name': 'Детоксикация',
                'slug': 'detoksikaciya',
                'description': 'Медикаментозная детоксикация организма',
                'duration': 120,
                'categories': ['lechenie-alkogolizma', 'lechenie-narkomanii']
            },
            {
                'name': 'Психотерапия',
                'slug': 'psihoterapiya',
                'description': 'Индивидуальные сессии с психотерапевтом',
                'duration': 60,
                'categories': ['lechenie-alkogolizma', 'lechenie-narkomanii', 'drugie-uslugi']
            },
            {
                'name': 'Групповая терапия',
                'slug': 'gruppovaya-terapiya',
                'description': 'Групповые занятия с психологом',
                'duration': 90,
                'categories': ['lechenie-alkogolizma', 'lechenie-narkomanii', 'drugie-uslugi']
            }
        ]

        for service_data in services_data:
            categories = service_data.pop('categories')
            service, created = Service.objects.get_or_create(
                slug=service_data['slug'],
                defaults=service_data
            )
            
            if created:
                # Добавляем категории к услуге
                service.categories.add(*ServiceCategory.objects.filter(slug__in=categories))
                self.stdout.write(
                    self.style.SUCCESS(f'Создана услуга: {service.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Услуга уже существует: {service.name}')
                )

        self.stdout.write(
            self.style.SUCCESS('Начальные данные успешно загружены')
        ) 