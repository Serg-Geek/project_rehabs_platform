# facilities/models/facility.py

from django.db import models
from django.utils.text import slugify
from .region import City
from .services import Service
from decimal import Decimal
from datetime import timedelta
from .services import InstitutionService, DoctorService
from .specialization import Specialization

class BaseFacility(models.Model):
    """Базовая модель с общими полями"""
    name = models.CharField(max_length=255)
    slug = models.SlugField(("name"))
    description = models.TextField(blank=True)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Добавить общие поля для лицензий
    license_number = models.CharField(max_length=100, blank=True, null=True)
    license_issued = models.DateField(blank=True, null=True)
    license_expires = models.DateField(blank=True, null=True)

    
    class Meta:
        abstract = True

class MedicalInstitution(BaseFacility):
    """Медицинские учреждения"""
    TYPES = (
        ('clinic', 'Клиника'),
        ('rehab', 'Реабилитационный центр'),
        ('hospital', 'Больница'),
    )
    
    type = models.CharField(max_length=10, choices=TYPES)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    license_number = models.CharField(max_length=100)
    website = models.URLField(blank=True, null=True)
    def add_service(self, service: Service, price: Decimal, duration: timedelta) -> 'InstitutionService':
        """Учреждение добавляет себе услугу"""
        return InstitutionService.objects.create(
            institution=self,
            service=service,
            price=price,
            duration=duration
        )

    def __str__(self):
        return f"{self.get_type_display()}: {self.name}"

class PrivateDoctor(BaseFacility):
    """Частные врачи"""
    specialization = models.ForeignKey(Specialization, on_delete=models.SET_NULL, null=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    license_number = models.CharField(max_length=100)
    consultation_price = models.DecimalField(max_digits=10, decimal_places=2)
    experience_years = models.PositiveIntegerField(default=0)


    def set_primary_service(self, service: Service) -> None:
        """Назначить основную услугу (для частного врача)"""
        DoctorService.objects.filter(doctor=self).update(is_primary=False)
        DoctorService.objects.update_or_create(
            doctor=self,
            service=service,
            defaults={'is_primary': True, 'is_available': True}
        )

    def __str__(self):
        return f"Доктор {self.name} ({self.specialization})"