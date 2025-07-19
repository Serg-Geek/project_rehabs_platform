"""
Managers for facility models.

This module provides custom managers for facility models
with optimized queries and business logic.
"""

from django.db import models
from django.db.models import Avg, Count, Q
from django.utils import timezone


class FacilityManager(models.Manager):
    """
    Custom manager for medical facilities.
    
    Provides optimized queries and business logic for facility operations.
    """
    
    def active_with_related(self):
        """
        Get active facilities with related objects optimized.
        
        Returns:
            QuerySet: Active facilities with city, organization_type, reviews, and images
        """
        return self.select_related('city', 'organization_type')\
                   .prefetch_related('reviews', 'images')\
                   .filter(is_active=True)
    
    def by_city_and_type(self, city_slug=None, org_type_slug=None):
        """
        Filter facilities by city and organization type.
        
        Args:
            city_slug: City slug to filter by
            org_type_slug: Organization type slug to filter by
            
        Returns:
            QuerySet: Filtered facilities
        """
        queryset = self.active_with_related()
        
        if city_slug:
            queryset = queryset.filter(city__slug=city_slug)
            
        if org_type_slug:
            queryset = queryset.filter(organization_type__slug=org_type_slug)
            
        return queryset
    
    def with_rating_above(self, min_rating):
        """
        Get facilities with average rating above specified value.
        
        Args:
            min_rating: Minimum average rating
            
        Returns:
            QuerySet: Facilities with rating above minimum
        """
        return self.active_with_related()\
                   .annotate(avg_rating=Avg('reviews__rating'))\
                   .filter(avg_rating__gte=min_rating)
    
    def with_review_count(self, min_reviews=1):
        """
        Get facilities with minimum number of reviews.
        
        Args:
            min_reviews: Minimum number of reviews
            
        Returns:
            QuerySet: Facilities with minimum reviews
        """
        return self.active_with_related()\
                   .annotate(review_count=Count('reviews'))\
                   .filter(review_count__gte=min_reviews)
    
    def search_by_name(self, search_term):
        """
        Search facilities by name.
        
        Args:
            search_term: Search term for facility name
            
        Returns:
            QuerySet: Facilities matching search term
        """
        return self.active_with_related()\
                   .filter(name__icontains=search_term)
    
    def by_services(self, service_names):
        """
        Get facilities that provide specific services.
        
        Args:
            service_names: List of service names
            
        Returns:
            QuerySet: Facilities providing specified services
        """
        return self.active_with_related()\
                   .filter(services__name__in=service_names)\
                   .distinct()
    
    def recently_updated(self, days=30):
        """
        Get facilities updated recently.
        
        Args:
            days: Number of days to look back
            
        Returns:
            QuerySet: Recently updated facilities
        """
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        return self.active_with_related()\
                   .filter(updated_at__gte=cutoff_date)
    
    def with_images(self):
        """
        Get facilities that have images.
        
        Returns:
            QuerySet: Facilities with images
        """
        return self.active_with_related()\
                   .filter(images__isnull=False)\
                   .distinct()
    
    def top_rated(self, limit=10):
        """
        Get top rated facilities.
        
        Args:
            limit: Maximum number of facilities to return
            
        Returns:
            QuerySet: Top rated facilities
        """
        return self.active_with_related()\
                   .annotate(avg_rating=Avg('reviews__rating'))\
                   .filter(avg_rating__isnull=False)\
                   .order_by('-avg_rating')[:limit]
    
    def by_license_status(self, has_license=True):
        """
        Get facilities by license status.
        
        Args:
            has_license: Whether to get facilities with or without license
            
        Returns:
            QuerySet: Facilities by license status
        """
        if has_license:
            return self.active_with_related()\
                       .exclude(license_number='')
        else:
            return self.active_with_related()\
                       .filter(license_number='')


class ClinicManager(FacilityManager):
    """
    Custom manager for clinics.
    
    Provides clinic-specific queries and business logic.
    """
    
    def with_emergency_support(self):
        """
        Get clinics with emergency support.
        
        Returns:
            QuerySet: Clinics with emergency support
        """
        return self.active_with_related()\
                   .filter(emergency_support=True)
    
    def with_hospital(self):
        """
        Get clinics with hospital facilities.
        
        Returns:
            QuerySet: Clinics with hospital
        """
        return self.active_with_related()\
                   .filter(has_hospital=True)
    
    def by_specialization(self, specialization):
        """
        Get clinics by medical specialization.
        
        Args:
            specialization: Medical specialization
            
        Returns:
            QuerySet: Clinics with specified specialization
        """
        return self.active_with_related()\
                   .filter(specializations__name__icontains=specialization)\
                   .distinct()


class RehabCenterManager(FacilityManager):
    """
    Custom manager for rehabilitation centers.
    
    Provides rehab center-specific queries and business logic.
    """
    
    def by_capacity(self, min_capacity=None, max_capacity=None):
        """
        Get rehab centers by capacity.
        
        Args:
            min_capacity: Minimum capacity
            max_capacity: Maximum capacity
            
        Returns:
            QuerySet: Rehab centers within capacity range
        """
        queryset = self.active_with_related()
        
        if min_capacity is not None:
            queryset = queryset.filter(capacity__gte=min_capacity)
            
        if max_capacity is not None:
            queryset = queryset.filter(capacity__lte=max_capacity)
            
        return queryset
    
    def by_program_duration(self, min_duration=None, max_duration=None):
        """
        Get rehab centers by program duration.
        
        Args:
            min_duration: Minimum program duration in days
            max_duration: Maximum program duration in days
            
        Returns:
            QuerySet: Rehab centers within duration range
        """
        queryset = self.active_with_related()
        
        if min_duration is not None:
            queryset = queryset.filter(program_duration__gte=min_duration)
            
        if max_duration is not None:
            queryset = queryset.filter(program_duration__lte=max_duration)
            
        return queryset
    
    def by_price_range(self, min_price=None, max_price=None):
        """
        Get rehab centers by price range.
        
        Args:
            min_price: Minimum price
            max_price: Maximum price
            
        Returns:
            QuerySet: Rehab centers within price range
        """
        queryset = self.active_with_related()
        
        if min_price is not None:
            queryset = queryset.filter(min_price__gte=min_price)
            
        if max_price is not None:
            queryset = queryset.filter(min_price__lte=max_price)
            
        return queryset
    
    def with_special_programs(self):
        """
        Get rehab centers with special programs.
        
        Returns:
            QuerySet: Rehab centers with special programs
        """
        return self.active_with_related()\
                   .exclude(special_programs='')


class PrivateDoctorManager(FacilityManager):
    """
    Custom manager for private doctors.
    
    Provides private doctor-specific queries and business logic.
    """
    
    def by_specialization(self, specialization):
        """
        Get private doctors by specialization.
        
        Args:
            specialization: Medical specialization
            
        Returns:
            QuerySet: Private doctors with specified specialization
        """
        return self.active_with_related()\
                   .filter(specializations__name__icontains=specialization)\
                   .distinct()
    
    def with_consultation_available(self):
        """
        Get private doctors with consultation available.
        
        Returns:
            QuerySet: Private doctors with consultation
        """
        return self.active_with_related()\
                   .filter(consultation_available=True)
    
    def by_experience_years(self, min_years=None, max_years=None):
        """
        Get private doctors by experience years.
        
        Args:
            min_years: Minimum years of experience
            max_years: Maximum years of experience
            
        Returns:
            QuerySet: Private doctors within experience range
        """
        queryset = self.active_with_related()
        
        if min_years is not None:
            queryset = queryset.filter(experience_years__gte=min_years)
            
        if max_years is not None:
            queryset = queryset.filter(experience_years__lte=max_years)
            
        return queryset
    
    def with_emergency_consultation(self):
        """
        Get private doctors with emergency consultation.
        
        Returns:
            QuerySet: Private doctors with emergency consultation
        """
        return self.active_with_related()\
                   .filter(emergency_consultation=True) 