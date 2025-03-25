# facilities/models/__init__.py
from .region import Region, City
from .facility import BaseFacility, MedicalInstitution, PrivateDoctor
from .specialization import Specialization  # Новая модель
from .specialist import Specialist  # Заменяем Doctor
from .services import Service, InstitutionService # Обновляем
from .images import FacilityImage, SpecialistImage  # Переименовываем DoctorImage

__all__ = [
    'Region',
    'City',
    'BaseFacility',
    'MedicalInstitution',
    'PrivateDoctor',
    'Specialization',  # Добавляем
    'Specialist',  # Заменяем Doctor
    'Service',
    'InstitutionService',
    'FacilityImage',
    'SpecialistImage'  # Переименовываем
]