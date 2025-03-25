# facilities/admin.py
from django.contrib import admin
from facilities.models.facility import MedicalInstitution, PrivateDoctor
from facilities.models.region import Region, City
from facilities.models.images import FacilityImage, DoctorImage
from facilities.models.specialist import Specialist
from facilities.models.specialization import Specialization
from facilities.models.services import Service, ServiceCategory

@admin.register(MedicalInstitution)
class MedicalInstitutionAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'city', 'license_number', 'is_active')
    list_filter = ('type', 'city', 'is_active')
    search_fields = ('name', 'license_number')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('license_issued', 'license_expires')  # Добавлено для полей дат

@admin.register(PrivateDoctor)
class PrivateDoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialization', 'city', 'license_number', 'is_active')
    list_filter = ('specialization', 'city', 'is_active')
    search_fields = ('name', 'license_number')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('license_issued', 'license_expires')

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'region', 'slug')
    list_filter = ('region',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(FacilityImage)
class FacilityImageAdmin(admin.ModelAdmin):
    list_display = ('facility', 'image_type', 'created_at')
    list_filter = ('image_type', 'facility')
    date_hierarchy = 'created_at'

@admin.register(DoctorImage)
class DoctorImageAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'image_type', 'created_at')
    list_filter = ('image_type', 'doctor')
    date_hierarchy = 'created_at'

@admin.register(Specialist)
class SpecialistAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'institution', 'license_number', 'is_accepting_new_patients')
    list_filter = ('institution', 'specializations', 'is_accepting_new_patients')
    search_fields = ('last_name', 'first_name', 'license_number')
    filter_horizontal = ('specializations',)

@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
# from django.contrib import admin
# from facilities.models.facility import MedicalInstitution, PrivateDoctor
# from facilities.models.region import Region, City
# from facilities.models.images import FacilityImage, DoctorImage
# from facilities.models.specialist import Specialist
# from facilities.models.specialization import Specialization
# from facilities.models.services import Service, ServiceCategory

# @admin.register(MedicalInstitution)
# class MedicalInstitutionAdmin(admin.ModelAdmin):
#     list_display = ('name', 'type', 'city', 'license_number', 'is_active')
#     list_filter = ('type', 'city', 'is_active')
#     search_fields = ('name', 'license_number')
#     prepopulated_fields = {'slug': ('name',)}
#     filter_horizontal = ('specializations',)

# @admin.register(PrivateDoctor)
# class PrivateDoctorAdmin(admin.ModelAdmin):
#     list_display = ('name', 'specialization', 'city', 'license_number', 'is_active')
#     list_filter = ('specialization', 'city', 'is_active')
#     search_fields = ('name', 'license_number')
#     prepopulated_fields = {'slug': ('name',)}

# @admin.register(Region)
# class RegionAdmin(admin.ModelAdmin):
#     list_display = ('name', 'slug')
#     search_fields = ('name',)
#     prepopulated_fields = {'slug': ('name',)}

# @admin.register(City)
# class CityAdmin(admin.ModelAdmin):
#     list_display = ('name', 'region', 'slug')
#     list_filter = ('region',)
#     search_fields = ('name',)
#     prepopulated_fields = {'slug': ('name',)}

# @admin.register(FacilityImage)
# class FacilityImageAdmin(admin.ModelAdmin):
#     list_display = ('facility', 'image_type', 'created_at')
#     list_filter = ('image_type', 'facility')
#     date_hierarchy = 'created_at'

# @admin.register(DoctorImage)
# class DoctorImageAdmin(admin.ModelAdmin):
#     list_display = ('doctor', 'image_type', 'created_at')
#     list_filter = ('image_type', 'doctor')
#     date_hierarchy = 'created_at'

# @admin.register(Specialist)
# class SpecialistAdmin(admin.ModelAdmin):
#     list_display = ('full_name', 'institution', 'license_number', 'is_accepting_new_patients')
#     list_filter = ('institution', 'specializations', 'is_accepting_new_patients')
#     search_fields = ('last_name', 'first_name', 'license_number')
#     filter_horizontal = ('specializations',)

# @admin.register(Specialization)
# class SpecializationAdmin(admin.ModelAdmin):
#     list_display = ('name', 'slug', 'is_active')
#     list_filter = ('is_active',)
#     search_fields = ('name',)
#     prepopulated_fields = {'slug': ('name',)}

# @admin.register(Service)
# class ServiceAdmin(admin.ModelAdmin):
#     list_display = ('name', 'category', 'is_active')
#     list_filter = ('category', 'is_active')
#     search_fields = ('name', 'description')
#     prepopulated_fields = {'slug': ('name',)}

# @admin.register(ServiceCategory)
# class ServiceCategoryAdmin(admin.ModelAdmin):
#     list_display = ('name', 'slug')
#     search_fields = ('name',)
#     prepopulated_fields = {'slug': ('name',)}