from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from facilities.models import RehabCenter, Clinic
from staff.models import FacilitySpecialist

class Command(BaseCommand):
    help = 'Links specialists with facilities'

    def handle(self, *args, **options):
        # Получаем все центры и клиники
        rehab_centers = RehabCenter.objects.all()
        clinics = Clinic.objects.all()
        facilities = list(rehab_centers) + list(clinics)
        
        # Получаем всех специалистов без привязки к учреждению
        specialists = FacilitySpecialist.objects.filter(content_type__isnull=True)
        
        if not specialists.exists():
            self.stdout.write(self.style.WARNING('No unlinked specialists found'))
            return
            
        # Получаем ContentType для RehabCenter и Clinic
        rehab_content_type = ContentType.objects.get_for_model(RehabCenter)
        clinic_content_type = ContentType.objects.get_for_model(Clinic)
        
        # Связываем каждого специалиста с учреждением
        for specialist in specialists:
            if facilities:
                facility = facilities[0]  # Берем первое учреждение
                specialist.content_type = ContentType.objects.get_for_model(facility.__class__)
                specialist.object_id = facility.id
                specialist.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Linked specialist {specialist.get_full_name()} with {facility}'
                    )
                )
            
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully linked {specialists.count()} specialists with facilities'
            )
        ) 