from django.db import models
from django.utils.text import slugify

class Region(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Facility(models.Model):
    class FacilityType(models.TextChoices):
        CLINIC = "clinic", "Клиника"
        REHAB = "rehab", "Реабилитационный центр"

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, related_name="facilities")
    type = models.CharField(max_length=10, choices=FacilityType.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.get_type_display()}: {self.name}"

class Service(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    admin_name = models.CharField(max_length=255)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class FacilityService(models.Model):
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name="facility_services")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="facility_services")
    date_added = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.facility.name} - {self.service.name}"

class ServicePrice(models.Model):
    facility_service = models.ForeignKey(FacilityService, on_delete=models.CASCADE, related_name="prices")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date_set = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.facility_service} - {self.price} руб."

class Doctor(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    experience = models.IntegerField()
    education = models.CharField(max_length=255)
    is_independent = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class DoctorFacility(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="facilities")
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name="doctors")
    position = models.CharField(max_length=255)
    date_added = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.doctor.name} - {self.position} в {self.facility.name}"

class Image(models.Model):
    image = models.ImageField(upload_to="images/")
    description = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Image {self.id}"

class FacilityImage(models.Model):
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name="images")
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name="facility_images")
    
    def __str__(self):
        return f"{self.facility.name} - Image {self.image.id}"

class DoctorImage(models.Model):
    class ImageType(models.TextChoices):
        PHOTO = "photo", "Фото доктора"
        DOCUMENT = "document", "Документ"
    
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="images")
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name="doctor_images")
    type = models.CharField(max_length=10, choices=ImageType.choices)
    
    def __str__(self):
        return f"{self.doctor.name} - {self.get_type_display()} {self.image.id}"
