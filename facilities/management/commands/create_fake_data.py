from django.core.management.base import BaseCommand
from django.utils.text import slugify
from facilities.models import OrganizationType, MedicalFacility, Clinic, RehabCenter
from core.models import City, Region
import uuid

class Command(BaseCommand):
    help = 'Creates fake data for medical facilities'

    def handle(self, *args, **kwargs):
        # Создаем регион
        region, _ = Region.objects.get_or_create(
            name='Краснодарский край',
            slug='krasnodarskij-kraj',
            defaults={
                'is_active': True
            }
        )

        # Создаем город
        city, _ = City.objects.get_or_create(
            name='Анапа',
            region=region,
            defaults={
                'slug': 'anapa',
                'is_active': True
            }
        )

        # Создаем типы организаций
        clinic_type, _ = OrganizationType.objects.get_or_create(
            name='Клиника',
            slug='clinic',
            defaults={
                'description': 'Медицинское учреждение, оказывающее амбулаторную помощь',
                'competencies': 'Диагностика, лечение, профилактика заболеваний'
            }
        )

        rehab_type, _ = OrganizationType.objects.get_or_create(
            name='Реабилитационный центр',
            slug='rehabilitation',
            defaults={
                'description': 'Специализированное учреждение для реабилитации пациентов',
                'competencies': 'Реабилитация, психологическая помощь, социальная адаптация'
            }
        )

        # Создаем клиники
        clinics_data = [
            {
                'name': 'Медицинский центр "Здоровье"',
                'description': 'Современный медицинский центр с широким спектром услуг',
                'address': 'ул. Ленина, 123, Анапа',
                'phone': '+7 (86133) 123-45',
                'email': 'info@zdorovie-anapa.ru',
                'website': 'https://zdorovie-anapa.ru',
                'license_number': 'ЛО-23-01-123456',
                'emergency_support': True,
                'has_hospital': True
            },
            {
                'name': 'Клиника "Доктор+"',
                'description': 'Специализированная клиника с современным оборудованием',
                'address': 'пр. Революции, 45, Анапа',
                'phone': '+7 (86133) 234-56',
                'email': 'info@doctor-plus.ru',
                'website': 'https://doctor-plus.ru',
                'license_number': 'ЛО-23-01-234567',
                'emergency_support': True,
                'has_hospital': False
            }
        ]

        for clinic_data in clinics_data:
            # Создаем уникальный slug
            base_slug = slugify(clinic_data['name'])
            unique_slug = f"{base_slug}-{str(uuid.uuid4())[:8]}"
            
            clinic, created = Clinic.objects.get_or_create(
                name=clinic_data['name'],
                defaults={
                    'slug': unique_slug,
                    'organization_type': clinic_type,
                    'description': clinic_data['description'],
                    'address': clinic_data['address'],
                    'phone': clinic_data['phone'],
                    'email': clinic_data['email'],
                    'website': clinic_data['website'],
                    'license_number': clinic_data['license_number'],
                    'city': city,
                    'emergency_support': clinic_data['emergency_support'],
                    'has_hospital': clinic_data['has_hospital']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created clinic: {clinic.name}'))

        # Создаем реабилитационные центры
        rehab_centers_data = [
            {
                'name': 'Реабилитационный центр "Новая жизнь"',
                'description': 'Современный центр реабилитации с комплексным подходом',
                'address': 'ул. Пушкина, 67, Анапа',
                'phone': '+7 (86133) 345-67',
                'email': 'info@novaya-zhizn.ru',
                'website': 'https://novaya-zhizn.ru',
                'license_number': 'ЛО-23-01-345678',
                'capacity': 50,
                'program_duration': 30,
                'accommodation_conditions': '2-3 местные номера с удобствами'
            },
            {
                'name': 'Центр восстановления "Вершина"',
                'description': 'Специализированный центр для комплексной реабилитации',
                'address': 'ул. Гоголя, 89, Анапа',
                'phone': '+7 (86133) 456-78',
                'email': 'info@vershina-anapa.ru',
                'website': 'https://vershina-anapa.ru',
                'license_number': 'ЛО-23-01-456789',
                'capacity': 30,
                'program_duration': 45,
                'accommodation_conditions': '1-2 местные номера с удобствами'
            }
        ]

        for rehab_data in rehab_centers_data:
            # Создаем уникальный slug
            base_slug = slugify(rehab_data['name'])
            unique_slug = f"{base_slug}-{str(uuid.uuid4())[:8]}"
            
            rehab, created = RehabCenter.objects.get_or_create(
                name=rehab_data['name'],
                defaults={
                    'slug': unique_slug,
                    'organization_type': rehab_type,
                    'description': rehab_data['description'],
                    'address': rehab_data['address'],
                    'phone': rehab_data['phone'],
                    'email': rehab_data['email'],
                    'website': rehab_data['website'],
                    'license_number': rehab_data['license_number'],
                    'city': city,
                    'capacity': rehab_data['capacity'],
                    'program_duration': rehab_data['program_duration'],
                    'accommodation_conditions': rehab_data['accommodation_conditions']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created rehab center: {rehab.name}'))

        self.stdout.write(self.style.SUCCESS('Successfully created fake data')) 