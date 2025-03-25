# facilities/models/region.py
from django.db import models
from django.utils.text import slugify

class Region(models.Model):
    """Модель региона (область, край)"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class City(models.Model):
    """Модель города"""
    name = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    slug = models.SlugField(blank=True)
    
    class Meta:
        unique_together = ('name', 'region')
        verbose_name_plural = "Города"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name}, {self.region}"
