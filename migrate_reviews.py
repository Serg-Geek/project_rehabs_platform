#!/usr/bin/env python
import os
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rehabs_platform.settings')
django.setup()

# Импорт моделей
from reviews.models import Review
from django.contrib.auth import get_user_model

User = get_user_model()
admin = User.objects.first()

# Обновление существующих отзывов
for review in Review.objects.all():
    if not review.created_by:
        review.created_by = admin
    if not review.author_name:
        review.author_name = 'Аноним'
    review.save()

print(f"Обновлено {Review.objects.count()} отзывов") 