from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.utils.translation import gettext_lazy as _


class CustomAdminSite(AdminSite):
    """
    Кастомный AdminSite с правильным порядком приложений и брендингом
    """
    site_header = _('Центр помощи зависимым - Админ-панель')
    site_title = _('Центр помощи зависимым')
    index_title = _('Управление платформой помощи зависимым')
    
    # Включаем боковую панель
    enable_nav_sidebar = True
    
    def get_app_list(self, request, app_label=None):
        """
        Возвращает список приложений в нужном порядке
        """
        app_list = super().get_app_list(request, app_label)
        
        # Если указан конкретный app_label, возвращаем как есть
        if app_label:
            return app_list
        
        # Определяем правильный порядок приложений
        app_order = [
            'requests',      # Заявки
            'facilities',    # Учреждения
            'medical_services',  # Медицинские услуги
            'staff',         # Персонал
            'recovery_stories',  # Истории выздоровления
            'content',       # Контент
            'blog',          # Блог
            'reviews',       # Отзывы
            'users',         # Пользователи
            'admin_logs',    # Система
            'core',          # Ядро
            'auth',          # Аутентификация
        ]
        
        # Сортируем приложения по нашему порядку
        app_dict = {app['app_label']: app for app in app_list}
        ordered_app_list = []
        
        # Добавляем приложения в нужном порядке
        for app_label in app_order:
            if app_label in app_dict:
                ordered_app_list.append(app_dict[app_label])
        
        # Добавляем остальные приложения (если есть)
        for app in app_list:
            if app['app_label'] not in app_order:
                ordered_app_list.append(app)
        
        return ordered_app_list


# Создаем экземпляр кастомного AdminSite
admin_site = CustomAdminSite(name='custom_admin')


def register_all_models():
    """
    Регистрирует все модели из стандартного admin.site в кастомном admin_site
    """
    # Копируем все зарегистрированные модели из стандартного admin.site
    for model, model_admin in admin.site._registry.items():
        admin_site.register(model, model_admin.__class__)


# Регистрируем все модели
register_all_models() 