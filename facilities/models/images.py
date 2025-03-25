# facilities/models/images.py
from pathlib import Path
from django.db import models
from django.core.files.storage import default_storage
from django.core.validators import FileExtensionValidator
from PIL import Image, ImageOps
from io import BytesIO
from django.core.files.base import ContentFile

class BaseImageModel(models.Model):
    """
    Базовая модель для изображений с обработкой через Pillow (с использованием pathlib)
    """
    image = models.ImageField(
        upload_to='facilities/images/%Y/%m/',
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])],
        verbose_name="Оригинальное изображение"
    )
    thumbnail = models.ImageField(
        upload_to='facilities/thumbnails/%Y/%m/',
        blank=True,
        null=True,
        verbose_name="Миниатюра"
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Описание"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата загрузки"
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        """Автоматическое создание миниатюры при сохранении"""
        super().save(*args, **kwargs)
        
        if not self.thumbnail and self.image:
            self.create_thumbnail()

    def create_thumbnail(self):
        """Генерация миниатюры 400x400px с обрезкой (с использованием pathlib)"""
        try:
            img = Image.open(self.image)
            
            # Автоповорот по EXIF-данным
            img = ImageOps.exif_transpose(img)
            
            # Обрезка до квадрата
            width, height = img.size
            size = min(width, height)
            left = (width - size) / 2
            top = (height - size) / 2
            right = (width + size) / 2
            bottom = (height + size) / 2
            img = img.crop((left, top, right, bottom))
            
            # Ресайз
            img.thumbnail((400, 400))
            
            # Сохранение в WEBP
            thumb_io = BytesIO()
            img.save(thumb_io, format='WEBP', quality=85)
            
            # Формирование имени файла с pathlib
            original_path = Path(self.image.name)
            thumb_name = f"thumb_{original_path.name}"
            thumb_path = original_path.with_name(thumb_name)
            
            # Сохранение
            self.thumbnail.save(
                str(thumb_path),  # Преобразуем Path в строку для save()
                ContentFile(thumb_io.getvalue()),
                save=False
            )
            super().save()
        except Exception as e:
            print(f"Ошибка создания миниатюры: {e}")

    def delete(self, *args, **kwargs):
        """Удаление файлов изображений при удалении модели"""
        storage = default_storage
        if self.image:
            storage.delete(self.image.name)
        if self.thumbnail:
            storage.delete(self.thumbnail.name)
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"Изображение {self.id}"

class FacilityImage(BaseImageModel):
    """Изображения медицинских учреждений"""
    IMAGE_TYPES = (
        ('main', 'Главное фото'),
        ('building', 'Здание'),
        ('interior', 'Интерьер'),
        ('equipment', 'Оборудование'),
        ('docs', 'Документы'),
    )

    facility = models.ForeignKey(
        'MedicalInstitution',
        on_delete=models.CASCADE,
        related_name='images'
    )
    image_type = models.CharField(
        max_length=10,
        choices=IMAGE_TYPES,
        default='main',
        verbose_name="Тип изображения"
    )

    class Meta(BaseImageModel.Meta):
        verbose_name = "Изображение учреждения"
        verbose_name_plural = "Изображения учреждений"
        constraints = [
            models.UniqueConstraint(
                fields=['facility', 'image_type'],
                condition=models.Q(image_type='main'),
                name='unique_main_image_per_facility'
            )
        ]

    def save(self, *args, **kwargs):
        """Автоматическая пометка главного изображения"""
        if self.image_type == 'main' and self.facility_id:
            FacilityImage.objects.filter(
                facility=self.facility,
                image_type='main'
            ).exclude(id=self.id).update(image_type='building')
        super().save(*args, **kwargs)

class DoctorImage(BaseImageModel):
    """Изображения врачей"""
    IMAGE_TYPES = (
        ('photo', 'Фото врача'),
        ('license', 'Лицензия'),
        ('diploma', 'Диплом'),
        ('docs', 'Документы'),
    )

    doctor = models.ForeignKey(
        'PrivateDoctor',
        on_delete=models.CASCADE,
        related_name='images'
    )
    image_type = models.CharField(
        max_length=10,
        choices=IMAGE_TYPES,
        verbose_name="Тип изображения"
    )

    class Meta(BaseImageModel.Meta):
        verbose_name = "Изображение врача"
        verbose_name_plural = "Изображения врачей"


class SpecialistImage(BaseImageModel):
    """Изображения специалистов"""
    IMAGE_TYPES = (
        ('photo', 'Фото специалиста'),
        ('license', 'Лицензия'),
        ('diploma', 'Диплом'),
    )

    specialist = models.ForeignKey(
        'Specialist',
        on_delete=models.CASCADE,
        related_name='images'
    )
    image_type = models.CharField(
        max_length=10,
        choices=IMAGE_TYPES,
        verbose_name="Тип изображения"
    )

    class Meta(BaseImageModel.Meta):
        verbose_name = "Изображение специалиста"
        verbose_name_plural = "Изображения специалистов"
