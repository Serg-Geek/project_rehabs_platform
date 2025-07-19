"""
Signals for blog app.

This module contains signals for automatic initialization of system tags.
"""

from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.apps import apps


@receiver(post_migrate)
def initialize_system_tags(sender, **kwargs):
    """
    Автоматически инициализирует системные теги после миграций.
    
    Этот сигнал срабатывает после выполнения миграций и создает
    системные теги, если они еще не существуют.
    """
    # Проверяем, что это миграция для приложения blog
    if sender.name == 'blog':
        try:
            # Получаем модель Tag
            Tag = apps.get_model('blog', 'Tag')
            
            # Инициализируем системные теги
            created_count, updated_count = Tag.initialize_system_tags()
            
            if created_count > 0 or updated_count > 0:
                print(f"Системные теги инициализированы: создано {created_count}, обновлено {updated_count}")
                
        except Exception as e:
            print(f"Ошибка при инициализации системных тегов: {e}") 