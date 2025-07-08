from django import template

register = template.Library()

@register.filter
def year_plural(value):
    """
    Возвращает правильное склонение слова "год" в зависимости от числа.
    
    Примеры:
    1 -> "1 год"
    2 -> "2 года" 
    5 -> "5 лет"
    21 -> "21 год"
    22 -> "22 года"
    25 -> "25 лет"
    """
    try:
        num = int(value)
    except (ValueError, TypeError):
        return f"{value} лет"
    
    if num % 10 == 1 and num % 100 != 11:
        return f"{num} год"
    elif num % 10 in [2, 3, 4] and num % 100 not in [12, 13, 14]:
        return f"{num} года"
    else:
        return f"{num} лет" 