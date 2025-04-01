from django.contrib import admin
from .models import (
    Employee,
    Department,
    Position,
    Specialization,
    Education,
    WorkExperience,
    Achievement,
    Schedule
)

class EducationInline(admin.TabularInline):
    model = Education
    extra = 1

class WorkExperienceInline(admin.TabularInline):
    model = WorkExperience
    extra = 1

class AchievementInline(admin.TabularInline):
    model = Achievement
    extra = 1

class ScheduleInline(admin.TabularInline):
    model = Schedule
    extra = 1

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = [
        'full_name',
        'position',
        'department',
        'phone',
        'email',
        'is_active'
    ]
    list_filter = [
        'is_active',
        'department',
        'position',
        'specializations',
        'employment_date'
    ]
    search_fields = [
        'last_name',
        'first_name',
        'middle_name',
        'phone',
        'email'
    ]
    filter_horizontal = ['specializations']
    inlines = [
        EducationInline,
        WorkExperienceInline,
        AchievementInline,
        ScheduleInline
    ]
    fieldsets = (
        ('Основная информация', {
            'fields': (
                ('last_name', 'first_name', 'middle_name'),
                'birth_date',
                'gender',
                'photo',
            )
        }),
        ('Контактная информация', {
            'fields': (
                'phone',
                'email',
                'address',
            )
        }),
        ('Работа', {
            'fields': (
                'department',
                'position',
                'specializations',
                'employment_date',
                'dismissal_date',
                'is_active',
            )
        }),
        ('Профессиональная информация', {
            'fields': (
                'bio',
                'professional_interests',
                'certificates',
            )
        }),
    )

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'head', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_medical']
    list_filter = ['is_medical']
    search_fields = ['name', 'description']

@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name', 'description']

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = [
        'employee',
        'institution',
        'degree',
        'field_of_study',
        'graduation_year'
    ]
    list_filter = ['degree', 'graduation_year']
    search_fields = [
        'employee__last_name',
        'institution',
        'field_of_study'
    ]

@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    list_display = [
        'employee',
        'organization',
        'position',
        'start_date',
        'end_date'
    ]
    list_filter = ['start_date', 'end_date']
    search_fields = [
        'employee__last_name',
        'organization',
        'position'
    ]

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = [
        'employee',
        'title',
        'date'
    ]
    list_filter = ['date']
    search_fields = [
        'employee__last_name',
        'title',
        'description'
    ]

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = [
        'employee',
        'day_of_week',
        'start_time',
        'end_time'
    ]
    list_filter = ['day_of_week']
    search_fields = ['employee__last_name']
