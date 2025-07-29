from .models import ServiceCategory, Service


def service_categories(request):
    """
    Контекстный процессор для передачи категорий услуг во все шаблоны
    """
    try:
        # Получаем активные категории услуг в фиксированном порядке
        categories = []
        
        # 1. Лечение наркомании
        drug_addiction_category = ServiceCategory.objects.filter(
            slug='lechenie-narkomanii',
            is_active=True
        ).first()
        if drug_addiction_category:
            categories.append(drug_addiction_category)
        
        # 2. Лечение алкоголизма
        alcoholism_category = ServiceCategory.objects.filter(
            slug='lechenie-alkogolizma',
            is_active=True
        ).first()
        if alcoholism_category:
            categories.append(alcoholism_category)
        
        # 3. Другие услуги
        other_category = ServiceCategory.objects.filter(
            slug='drugie-uslugi',
            is_active=True
        ).first()
        if other_category:
            categories.append(other_category)
        
        # 4. Остальные категории (если есть) - по алфавиту
        other_categories = ServiceCategory.objects.filter(
            is_active=True
        ).exclude(
            slug__in=['lechenie-alkogolizma', 'lechenie-narkomanii', 'drugie-uslugi']
        ).order_by('name')
        
        categories.extend(other_categories)
        
        return {'service_categories': categories}
        
    except Exception:
        # В случае ошибки возвращаем пустой QuerySet
        return {'service_categories': ServiceCategory.objects.none()}


def footer_services(request):
    """
    Контекстный процессор для передачи данных услуг в футер
    """
    try:
        # Получаем основные категории услуг для футера
        alcoholism_category = ServiceCategory.objects.filter(
            slug='lechenie-alkogolizma',
            is_active=True
        ).first()
        
        drug_addiction_category = ServiceCategory.objects.filter(
            slug='lechenie-narkomanii',
            is_active=True
        ).first()
        
        other_category = ServiceCategory.objects.filter(
            slug='drugie-uslugi',
            is_active=True
        ).first()
        
        # Получаем услуги для каждой категории (максимум 8-10 для футера)
        footer_services = {}
        
        if alcoholism_category:
            footer_services['alcoholism'] = {
                'category': alcoholism_category,
                'services': Service.objects.filter(
                    categories=alcoholism_category,
                    is_active=True
                ).order_by('-display_priority', 'name')[:10]
            }
        
        if drug_addiction_category:
            footer_services['drug_addiction'] = {
                'category': drug_addiction_category,
                'services': Service.objects.filter(
                    categories=drug_addiction_category,
                    is_active=True
                ).order_by('-display_priority', 'name')[:10]
            }
        
        if other_category:
            footer_services['other'] = {
                'category': other_category,
                'services': Service.objects.filter(
                    categories=other_category,
                    is_active=True
                ).order_by('-display_priority', 'name')[:10]
            }
        
        return {'footer_services': footer_services}
        
    except Exception:
        # В случае ошибки возвращаем пустой словарь
        return {'footer_services': {}} 