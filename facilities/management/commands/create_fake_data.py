from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify
from django.db.models import Q
import random
import uuid
from faker import Faker
from datetime import date, timedelta

from facilities.models import (
    OrganizationType, 
    Clinic, 
    RehabCenter, 
    FacilityImage, 
    FacilityDocument,
    PrivateDoctor
)
from staff.models import FacilitySpecialist, Specialization
from core.models import City, Region

class Command(BaseCommand):
    help = 'Creates fake data for medical facilities'

    def add_arguments(self, parser):
        parser.add_argument(
            '--num-clinics',
            type=int,
            default=5,
            help='Number of clinics to create'
        )
        parser.add_argument(
            '--num-rehabs',
            type=int,
            default=5,
            help='Number of rehabilitation centers to create'
        )
        parser.add_argument(
            '--num-reviews',
            type=int,
            default=3,
            help='Number of reviews per facility'
        )
        parser.add_argument(
            '--num-docs',
            type=int,
            default=1,
            help='Number of documents per facility'
        )

    def __init__(self):
        super().__init__()
        self.faker = Faker('ru_RU')

    def create_cities(self):
        """Создание городов и регионов"""
        regions_data = [
            {'name': 'Краснодарский край', 'slug': 'krasnodarskij-kraj'},
            {'name': 'Московская область', 'slug': 'moskovskaya-oblast'},
            {'name': 'Санкт-Петербург', 'slug': 'sankt-peterburg'},
        ]
        
        cities_data = [
            {'name': 'Анапа', 'region_slug': 'krasnodarskij-kraj'},
            {'name': 'Краснодар', 'region_slug': 'krasnodarskij-kraj'},
            {'name': 'Москва', 'region_slug': 'moskovskaya-oblast'},
            {'name': 'Санкт-Петербург', 'region_slug': 'sankt-peterburg'},
        ]
        
        regions = {}
        for region_data in regions_data:
            try:
                region = Region.objects.get(name=region_data['name'])
            except Region.DoesNotExist:
                region = Region.objects.create(
                    name=region_data['name'],
                    slug=region_data['slug'],
                    is_active=True
                )
            regions[region_data['slug']] = region
        
        cities = {}
        for city_data in cities_data:
            try:
                city = City.objects.get(
                    name=city_data['name'],
                    region=regions[city_data['region_slug']]
                )
            except City.DoesNotExist:
                city = City.objects.create(
                    name=city_data['name'],
                    region=regions[city_data['region_slug']],
                    slug=slugify(city_data['name']),
                    is_active=True
                )
            cities[city.name] = city
        
        return cities

    def create_review(self, facility, content_type):
        """Создание отзыва для учреждения"""
        review = Review.objects.create(
            content_type=content_type,
            object_id=facility.id,
            rating=random.randint(1, 5),
            content=self.faker.text(max_nb_chars=200)
        )
        return review

    def create_document(self, facility, content_type, doc_type):
        """Создание документа для учреждения"""
        issue_date = self.faker.date_between(start_date='-5y', end_date='today')
        expiry_date = issue_date + timedelta(days=random.randint(365, 1825))
        
        document = FacilityDocument.objects.create(
            content_type=content_type,
            object_id=facility.id,
            document_type=doc_type,
            title=self.faker.sentence(nb_words=3),
            number=self.faker.bothify(text='??-####-????'),
            issue_date=issue_date,
            expiry_date=expiry_date,
            is_active=True
        )
        return document

    def create_specialist(self, facility, content_type):
        """Создание специалиста для учреждения"""
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        middle_name = self.faker.middle_name()
        
        # Создаем базовый слаг из фамилии и имени
        base_slug = slugify(f"{last_name}-{first_name}")
        slug = base_slug
        
        # Проверяем, существует ли уже такой слаг
        counter = 1
        while FacilitySpecialist.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        specialist = FacilitySpecialist.objects.create(
            content_type=content_type,
            object_id=facility.id,
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            slug=slug,
            position=self.faker.job(),
            experience_years=random.randint(1, 30),
            education=self.faker.text(max_nb_chars=200),
            biography=self.faker.text(max_nb_chars=300),
            achievements=self.faker.text(max_nb_chars=200),
            is_active=True
        )
        return specialist

    def create_private_doctors(self):
        """Создание тестовых частных врачей"""
        self.stdout.write('Создание частных врачей...')
        
        # Получаем города и специализации
        cities = list(City.objects.all())
        specializations = list(Specialization.objects.all())
        private_doctor_type = OrganizationType.objects.get(slug='private-doctor')
        
        if not cities:
            self.stdout.write(self.style.WARNING('Нет городов для создания врачей'))
            return
            
        if not specializations:
            self.stdout.write(self.style.WARNING('Нет специализаций для создания врачей'))
            return
        
        # Создаем 20 частных врачей
        for i in range(20):
            first_name = self.faker.first_name()
            last_name = self.faker.last_name()
            middle_name = self.faker.middle_name()
            
            # Формируем название
            if middle_name:
                name = f"{last_name} {first_name} {middle_name}"
            else:
                name = f"{last_name} {first_name}"
            
            # Создаем базовый слаг
            base_slug = slugify(f"{last_name}-{first_name}")
            slug = base_slug
            
            # Проверяем уникальность slug
            counter = 1
            while PrivateDoctor.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            # Создаем врача
            doctor = PrivateDoctor.objects.create(
                name=name,
                slug=slug,
                organization_type=private_doctor_type,
                first_name=first_name,
                last_name=last_name,
                middle_name=middle_name,
                experience_years=random.randint(5, 35),
                education=self.faker.text(max_nb_chars=300),
                biography=self.faker.text(max_nb_chars=500),
                achievements=self.faker.text(max_nb_chars=200),
                phone=self.faker.phone_number(),
                email=self.faker.email(),
                website=self.faker.url() if random.choice([True, False]) else '',
                address=self.faker.address(),
                city=random.choice(cities),
                office_description=self.faker.text(max_nb_chars=200),
                parking_available=random.choice([True, False]),
                wheelchair_accessible=random.choice([True, False]),
                schedule=self.faker.text(max_nb_chars=150),
                home_visits=random.choice([True, False]),
                emergency_available=random.choice([True, False]),
                weekend_work=random.choice([True, False]),
                consultation_price=random.randint(1000, 5000) if random.choice([True, False]) else None,
                home_visit_price=random.randint(2000, 8000) if random.choice([True, False]) else None,
                insurance_accepted=random.choice([True, False]),
                license_number=f"ЛО-{random.randint(100000, 999999)}" if random.choice([True, False]) else '',
                license_issue_date=date.today() - timedelta(days=random.randint(100, 1000)),
                license_expiry_date=date.today() + timedelta(days=random.randint(100, 1000)),
                online_consultations=random.choice([True, False]),
                video_consultations=random.choice([True, False]),
                special_equipment=self.faker.text(max_nb_chars=150) if random.choice([True, False]) else '',
                is_active=True
            )
            
            # Добавляем специализации
            doctor_specializations = random.sample(specializations, random.randint(1, 3))
            doctor.specializations.set(doctor_specializations)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Создан врач: {doctor.get_full_name()} в {doctor.city.name}'
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Создано {PrivateDoctor.objects.count()} частных врачей'
            )
        )

    def handle(self, *args, **kwargs):
        num_clinics = kwargs['num_clinics']
        num_rehabs = kwargs['num_rehabs']
        num_reviews = kwargs['num_reviews']
        num_docs = kwargs['num_docs']

        # Создаем города
        cities = self.create_cities()

        # Получаем типы организаций
        clinic_type = OrganizationType.objects.get(slug='clinic')
        rehab_type = OrganizationType.objects.get(slug='rehabilitation-center')

        # Создаем клиники
        for i in range(num_clinics):
            city = random.choice(list(cities.values()))
            clinic_data = {
                'name': f'Клиника "{self.faker.company()}"',
                'description': self.faker.text(max_nb_chars=500),
                'address': f'{self.faker.street_address()}, {city.name}',
                'phone': self.faker.phone_number(),
                'email': self.faker.email(),
                'website': self.faker.url(),
                'license_number': self.faker.bothify(text='ЛО-??-??-######'),
                'emergency_support': random.choice([True, False]),
                'has_hospital': random.choice([True, False])
            }

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
                # Создаем отзывы
                content_type = ContentType.objects.get_for_model(clinic)
                for _ in range(num_reviews):
                    self.create_review(clinic, content_type)

                # Создаем документы
                doc_types = [FacilityDocument.DocumentType.LICENSE,
                           FacilityDocument.DocumentType.CERTIFICATE,
                           FacilityDocument.DocumentType.ACCREDITATION]
                for _ in range(num_docs):
                    self.create_document(clinic, content_type, random.choice(doc_types))

                # Создаем специалистов
                for _ in range(random.randint(1, 5)):
                    self.create_specialist(clinic, content_type)

                self.stdout.write(self.style.SUCCESS(f'Created clinic: {clinic.name}'))

        # Создаем реабилитационные центры
        for i in range(num_rehabs):
            city = random.choice(list(cities.values()))
            rehab_data = {
                'name': f'Реабилитационный центр "{self.faker.company()}"',
                'description': self.faker.text(max_nb_chars=500),
                'address': f'{self.faker.street_address()}, {city.name}',
                'phone': self.faker.phone_number(),
                'email': self.faker.email(),
                'website': self.faker.url(),
                'capacity': random.randint(20, 100),
                'program_duration': random.randint(14, 90),
                'accommodation_conditions': self.faker.text(max_nb_chars=200),
                'min_price': random.randint(10000, 50000)
            }

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
                    'city': city,
                    'capacity': rehab_data['capacity'],
                    'program_duration': rehab_data['program_duration'],
                    'accommodation_conditions': rehab_data['accommodation_conditions'],
                    'min_price': rehab_data['min_price']
                }
            )

            if created:
                # Создаем отзывы
                content_type = ContentType.objects.get_for_model(rehab)
                for _ in range(num_reviews):
                    self.create_review(rehab, content_type)

                # Создаем документы
                doc_types = [FacilityDocument.DocumentType.LICENSE,
                           FacilityDocument.DocumentType.CERTIFICATE,
                           FacilityDocument.DocumentType.ACCREDITATION]
                for _ in range(num_docs):
                    self.create_document(rehab, content_type, random.choice(doc_types))

                # Создаем специалистов
                for _ in range(random.randint(1, 5)):
                    self.create_specialist(rehab, content_type)

                self.stdout.write(self.style.SUCCESS(f'Created rehab center: {rehab.name}'))

        self.create_private_doctors()
        self.stdout.write(self.style.SUCCESS('Successfully created fake data')) 