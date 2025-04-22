from django.core.management.base import BaseCommand
from facilities.models import (
    OrganizationType, AbstractMedicalFacility, Clinic, RehabCenter,
    Review, FacilityImage, FacilityDocument
)
from staff.models import FacilitySpecialist
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    help = 'Deletes all fake data created by create_fake_data command'

    def handle(self, *args, **kwargs):
        # Удаляем все объекты, начиная с зависимых
        Review.objects.all().delete()
        FacilityImage.objects.all().delete()
        FacilityDocument.objects.all().delete()
        FacilitySpecialist.objects.all().delete()
        
        # Удаляем учреждения
        Clinic.objects.all().delete()
        RehabCenter.objects.all().delete()
        
        self.stdout.write(self.style.SUCCESS('Successfully deleted all fake data')) 