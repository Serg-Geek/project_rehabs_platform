from django.core.management.base import BaseCommand
from facilities.models import MedicalFacility
from staff.models import FacilitySpecialist

class Command(BaseCommand):
    help = 'Links specialists with facilities'

    def handle(self, *args, **options):
        # Получаем все центры и специалистов
        facilities = MedicalFacility.objects.all()
        specialists = FacilitySpecialist.objects.all()
        
        # Связываем каждого специалиста с первым центром
        for specialist in specialists:
            facilities.first().specialists.add(specialist)
            
        self.stdout.write(self.style.SUCCESS(f'Successfully linked {specialists.count()} specialists with facilities')) 