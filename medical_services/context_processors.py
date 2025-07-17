from .models import ServiceCategory, Service


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
                ).order_by('name')[:10]
            }
        
        if drug_addiction_category:
            footer_services['drug_addiction'] = {
                'category': drug_addiction_category,
                'services': Service.objects.filter(
                    categories=drug_addiction_category,
                    is_active=True
                ).order_by('name')[:10]
            }
        
        if other_category:
            footer_services['other'] = {
                'category': other_category,
                'services': Service.objects.filter(
                    categories=other_category,
                    is_active=True
                ).order_by('name')[:10]
            }
        
        return {'footer_services': footer_services}
        
    except Exception:
        # В случае ошибки возвращаем пустой словарь
        return {'footer_services': {}} 