# facilities/models/specialist.py

from django.db import models
from django.utils.text import slugify
from .specialization import Specialization
from .facility import MedicalInstitution
from django.core.exceptions import ValidationError

class Specialist(models.Model):
    """Модель медицинского специалиста"""
    first_name = models.CharField(max_length=50, verbose_name="Имя")
    last_name = models.CharField(max_length=50, verbose_name="Фамилия")
    middle_name = models.CharField(
        max_length=50, 
        blank=True, 
        verbose_name="Отчество"
    )
    slug = models.SlugField(unique=True, blank=True, verbose_name="URL-идентификатор")
    specializations = models.ManyToManyField(
        Specialization,
        related_name='specialists',
        verbose_name="Специализации"
    )
    institution = models.ForeignKey(
    'MedicalInstitution',  # вместо from .facility import MedicalInstitution
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='specialists',
    verbose_name="Учреждение"
    )
    # Добавить связь с PrivateDoctor
    private_clinic = models.ForeignKey(
    'PrivateDoctor',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='assistants',
    verbose_name="Частная практика"
    )
    license_number = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Номер лицензии",
    )
    experience_years = models.PositiveIntegerField(
        default=0,
        verbose_name="Опыт работы (лет)"
    )
    is_accepting_new_patients = models.BooleanField(
        default=True,
        verbose_name="Принимает новых пациентов"
    )
    bio = models.TextField(blank=True, verbose_name="Биография")
    education = models.TextField(blank=True, verbose_name="Образование")

    class Meta:
        verbose_name = "Специалист"
        verbose_name_plural = "Специалисты"
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['last_name', 'first_name']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.last_name}-{self.first_name}")
            self.slug = base_slug
            counter = 1
            while Specialist.objects.filter(slug=self.slug).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1

        super().save(*args, **kwargs)

    def clean(self):
        if not self.institution and not self.private_clinic:
            raise ValidationError("Специалист должен быть привязан к учреждению или частной практике")
    @property
    def full_name(self):
        """Полное ФИО специалиста"""
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return " ".join(parts)

    @property
    def primary_specialization(self):
        """Первая (основная) специализация"""
        return self.specializations.first()

    def __str__(self):
        return f"{self.full_name} ({self.primary_specialization or 'специалист'})"