from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from PIL import Image
import os
from .constants import DEFAULT_SIZES
import io

def validate_image_format(image, size):
    """
    Валидатор для проверки формата и размера изображения.
    
    Args:
        image: Файл изображения
        size: Словарь с требуемыми размерами {'min_width': int, 'min_height': int}
    """
    try:
        # Открываем изображение
        img = Image.open(io.BytesIO(image.read()))
        
        # Проверяем размеры
        if img.width < size['min_width'] or img.height < size['min_height']:
            raise ValidationError(
                _('Изображение должно быть не меньше %(width)sx%(height)s пикселей.'),
                params={'width': size['min_width'], 'height': size['min_height']},
            )
            
        # Проверяем формат
        if img.format not in ['JPEG', 'PNG', 'WEBP']:
            raise ValidationError(
                _('Поддерживаются только форматы JPEG, PNG и WEBP.')
            )
            
        # Возвращаем курсор в начало файла
        image.seek(0)
        
    except Exception as e:
        raise ValidationError(
            _('Ошибка при обработке изображения: %(error)s'),
            params={'error': str(e)},
        )

def validate_image_dimensions(value, min_width, min_height, max_width, max_height):
    """Проверка размеров изображения"""
    try:
        img = Image.open(value)
        width, height = img.size
        
        if width < min_width or height < min_height:
            raise ValidationError(
                _('Изображение слишком маленькое. Минимальный размер: %(min_width)sx%(min_height)s пикселей.') % {
                    'min_width': min_width,
                    'min_height': min_height
                }
            )
            
        if width > max_width or height > max_height:
            raise ValidationError(
                _('Изображение слишком большое. Максимальный размер: %(max_width)sx%(max_height)s пикселей.') % {
                    'max_width': max_width,
                    'max_height': max_height
                }
            )
            
    except Exception as e:
        raise ValidationError(_('Ошибка при проверке изображения: %(error)s') % {'error': str(e)})

def validate_image_aspect_ratio(value, target_ratio, tolerance=0.1):
    """Проверка пропорций изображения"""
    try:
        img = Image.open(value)
        width, height = img.size
        current_ratio = width / height
        
        if abs(current_ratio - target_ratio) > tolerance:
            raise ValidationError(
                _('Неверные пропорции изображения. Требуемое соотношение: %(ratio)s:1') % {
                    'ratio': target_ratio
                }
            )
            
    except Exception as e:
        raise ValidationError(_('Ошибка при проверке пропорций изображения: %(error)s') % {'error': str(e)})

def validate_banner_image(value, device_type):
    """Проверка изображения баннера на соответствие размерам для определенного типа устройства"""
    # Получаем все форматы для данного типа устройства
    device_sizes = [size for size in DEFAULT_SIZES if size['device_type'] == device_type]
    
    if not device_sizes:
        raise ValidationError(_('Не найдены форматы для данного типа устройства'))
    
    # Проверяем формат файла
    validate_image_format(value, device_sizes[0])
    
    try:
        # Открываем изображение для проверки размеров
        img = Image.open(value)
        width, height = img.size
        current_ratio = width / height
        
        # Проверяем, соответствует ли изображение хотя бы одному формату
        valid_for_any_size = False
        error_messages = []
        
        for size in device_sizes:
            try:
                # Проверяем размеры
                if width < size['min_width'] or height < size['min_height']:
                    error_messages.append(
                        f"Для формата {size['name']}: изображение слишком маленькое. "
                        f"Минимальный размер: {size['min_width']}x{size['min_height']} пикселей."
                    )
                    continue
                    
                if width > size['max_width'] or height > size['max_height']:
                    error_messages.append(
                        f"Для формата {size['name']}: изображение слишком большое. "
                        f"Максимальный размер: {size['max_width']}x{size['max_height']} пикселей."
                    )
                    continue
                
                # Проверяем пропорции
                if abs(current_ratio - size['aspect_ratio']) <= 0.1:
                    valid_for_any_size = True
                    break
                else:
                    ratio_display = get_ratio_display(size['aspect_ratio'])
                    error_messages.append(
                        f"Для формата {size['name']}: неверные пропорции изображения. "
                        f"Требуемое соотношение: {ratio_display}"
                    )
                    
            except Exception as e:
                error_messages.append(f"Ошибка при проверке формата {size['name']}: {str(e)}")
        
        if not valid_for_any_size:
            raise ValidationError(
                _('Изображение не соответствует ни одному из доступных форматов:\n%(errors)s') % {
                    'errors': '\n'.join(error_messages)
                }
            )
            
    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        raise ValidationError(_('Ошибка при проверке изображения: %(error)s') % {'error': str(e)})

def get_ratio_display(ratio):
    """Возвращает соотношение сторон в формате 'X:Y'"""
    if ratio == 1.0:
        return "1:1"
    elif ratio == 3.0:
        return "3:1"
    elif ratio == 16/9:
        return "16:9"
    elif ratio == 9/16:
        return "9:16"
    elif ratio == 4/3:
        return "4:3"
    elif ratio == 3/4:
        return "3:4"
    return f"{ratio:.2f}:1"

def validate_desktop_image(value):
    """Проверка изображения для десктопа"""
    validate_banner_image(value, 'desktop')

def validate_tablet_image(value):
    """Проверка изображения для планшета"""
    validate_banner_image(value, 'tablet')

def validate_mobile_image(value):
    """Проверка изображения для мобильных"""
    validate_banner_image(value, 'mobile') 