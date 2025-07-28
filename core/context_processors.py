from django.core.exceptions import ObjectDoesNotExist
from core.models import City, Region


def geo_data(request):
    """
    Контекст-процессор для добавления гео-данных на все страницы
    
    Возвращает дефолтные гео-данные для России, если нет специфичных данных
    """
    return {
        'geo_region': 'RU',
        'geo_placename': 'Россия',
        'geo_position': '65.0000;105.0000',
        'icbm': '65.0000, 105.0000',
        'city_name': 'Анапа',
        'region_name': 'Краснодарский край',
        'full_location': 'Анапа, Краснодарский край'
    } 