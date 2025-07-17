def transliterate(text):
    """
    Транслитерация кириллицы в латиницу
    
    Args:
        text (str): Текст на кириллице
        
    Returns:
        str: Текст, транслитерированный в латиницу
    """
    translit_dict = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'E',
        'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
        'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
        'Ф': 'F', 'Х': 'H', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sch',
        'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
    }
    return ''.join(translit_dict.get(char, char) for char in text)


def generate_slug(text, model_class, instance=None):
    """
    Генерирует уникальный slug из текста с транслитерацией
    
    Args:
        text (str): Исходный текст
        model_class: Класс модели для проверки уникальности
        instance: Экземпляр модели (для исключения из проверки при обновлении)
        
    Returns:
        str: Уникальный slug
    """
    from django.utils.text import slugify
    
    # Транслитерируем текст
    transliterated_text = transliterate(text)
    
    # Формируем базовый slug
    base_slug = slugify(transliterated_text)
    
    # Если slug пустой после транслитерации, используем fallback
    if not base_slug:
        base_slug = f"item-{instance.id}" if instance and instance.id else "item"
    
    slug = base_slug
    
    # Проверяем уникальность и добавляем суффикс при необходимости
    counter = 1
    while model_class.objects.filter(slug=slug).exclude(pk=instance.pk if instance else None).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    return slug 