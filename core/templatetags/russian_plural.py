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

@register.filter
def russian_plural(value, forms):
    """
    Возвращает правильное склонение слова в зависимости от числа.
    
    Args:
        value: число
        forms: строка с тремя формами слова через запятую (ед.ч., род.п. ед.ч., род.п. мн.ч.)
    
    Примеры:
    {{ 1|russian_plural:"учреждение,учреждения,учреждений" }} -> "1 учреждение"
    {{ 2|russian_plural:"учреждение,учреждения,учреждений" }} -> "2 учреждения"
    {{ 5|russian_plural:"учреждение,учреждения,учреждений" }} -> "5 учреждений"
    """
    try:
        num = int(value)
    except (ValueError, TypeError):
        return f"{value} {forms.split(',')[2].strip()}"
    
    forms_list = [form.strip() for form in forms.split(',')]
    if len(forms_list) != 3:
        return f"{num} {forms_list[0] if forms_list else ''}"
    
    if num % 10 == 1 and num % 100 != 11:
        return f"{num} {forms_list[0]}"
    elif num % 10 in [2, 3, 4] and num % 100 not in [12, 13, 14]:
        return f"{num} {forms_list[1]}"
    else:
        return f"{num} {forms_list[2]}" 