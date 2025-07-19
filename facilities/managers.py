"""
Custom managers for facilities models.

This module provides optimized query methods for facilities models.
"""

from django.db import models
from django.db.models import Q, Prefetch


class FacilityManager(models.Manager):
    """
    Base manager for facility models with common query optimizations.
    """
    
    def with_related_data(self):
        """
        Get facilities with basic related data (images, city, region).
        
        Returns:
            QuerySet: Facilities with prefetched related data
        """
        return self.select_related('city', 'city__region')\
                   .prefetch_related('images')
    
    def with_full_data(self):
        """
        Get facilities with all related data for detail views.
        
        Returns:
            QuerySet: Facilities with all prefetched related data
        """
        return self.select_related('city', 'city__region')\
                   .prefetch_related(
                       'reviews',
                       'images',
                       'documents',
                       'specialists'
                   )
    
    def active(self):
        """
        Get only active facilities.
        
        Returns:
            QuerySet: Active facilities
        """
        return self.filter(is_active=True)
    
    def by_region(self, region):
        """
        Get facilities by region.
        
        Args:
            region: Region object or slug
            
        Returns:
            QuerySet: Facilities in the specified region
        """
        if hasattr(region, 'slug'):
            return self.filter(city__region=region)
        return self.filter(city__region__slug=region)
    
    def by_city(self, city):
        """
        Get facilities by city.
        
        Args:
            city: City object or slug
            
        Returns:
            QuerySet: Facilities in the specified city
        """
        if hasattr(city, 'slug'):
            return self.filter(city=city)
        return self.filter(city__slug=city)
    
    def search(self, query):
        """
        Search facilities by name, description, or address.
        
        Args:
            query: Search query string
            
        Returns:
            QuerySet: Matching facilities
        """
        if not query:
            return self.none()
        
        return self.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(address__icontains=query)
        )


class ClinicManager(FacilityManager):
    """
    Manager for Clinic model with clinic-specific query methods.
    """
    
    def with_related_data(self):
        """
        Get clinics with basic related data.
        
        Returns:
            QuerySet: Clinics with prefetched related data
        """
        return super().with_related_data().order_by('name')
    
    def with_full_data(self):
        """
        Get clinics with all related data for detail views.
        
        Returns:
            QuerySet: Clinics with all prefetched related data
        """
        return super().with_full_data().order_by('name')
    
    def by_specialization(self, specialization):
        """
        Get clinics by medical specialization.
        
        Args:
            specialization: Specialization object or slug
            
        Returns:
            QuerySet: Clinics with the specified specialization
        """
        if hasattr(specialization, 'slug'):
            return self.filter(specializations=specialization)
        return self.filter(specializations__slug=specialization)


class RehabCenterManager(FacilityManager):
    """
    Manager for RehabCenter model with rehab-specific query methods.
    """
    
    def with_related_data(self):
        """
        Get rehab centers with basic related data.
        
        Returns:
            QuerySet: Rehab centers with prefetched related data
        """
        return super().with_related_data().order_by('name')
    
    def with_full_data(self):
        """
        Get rehab centers with all related data for detail views.
        
        Returns:
            QuerySet: Rehab centers with all prefetched related data
        """
        return super().with_full_data().order_by('name')
    
    def by_addiction_type(self, addiction_type):
        """
        Get rehab centers by addiction type.
        
        Args:
            addiction_type: Addiction type object or slug
            
        Returns:
            QuerySet: Rehab centers for the specified addiction type
        """
        if hasattr(addiction_type, 'slug'):
            return self.filter(addiction_types=addiction_type)
        return self.filter(addiction_types__slug=addiction_type)
    
    def with_home_visits(self):
        """
        Get rehab centers that offer home visits.
        
        Returns:
            QuerySet: Rehab centers with home visits
        """
        return self.filter(home_visits=True)


class PrivateDoctorManager(FacilityManager):
    """
    Manager for PrivateDoctor model with doctor-specific query methods.
    """
    
    def with_related_data(self):
        """
        Get private doctors with basic related data.
        
        Returns:
            QuerySet: Private doctors with prefetched related data
        """
        return self.filter(is_active=True)\
                   .select_related('city', 'city__region')\
                   .prefetch_related('specializations', 'images')\
                   .order_by('last_name', 'first_name')
    
    def with_full_data(self):
        """
        Get private doctors with all related data for detail views.
        
        Returns:
            QuerySet: Private doctors with all prefetched related data
        """
        return self.filter(is_active=True)\
                   .select_related('city', 'city__region')\
                   .prefetch_related(
                       'specializations',
                       'images',
                       'documents',
                       'reviews'
                   )\
                   .order_by('last_name', 'first_name')
    
    def by_specialization(self, specialization):
        """
        Get private doctors by specialization.
        
        Args:
            specialization: Specialization object or slug
            
        Returns:
            QuerySet: Private doctors with the specified specialization
        """
        if hasattr(specialization, 'slug'):
            return self.filter(specializations=specialization)
        return self.filter(specializations__slug=specialization)
    
    def with_home_visits(self):
        """
        Get private doctors who offer home visits.
        
        Returns:
            QuerySet: Private doctors with home visits
        """
        return self.filter(home_visits=True)
    
    def search(self, query):
        """
        Search private doctors by name, specialization, or city.
        
        Args:
            query: Search query string
            
        Returns:
            QuerySet: Matching private doctors
        """
        if not query:
            return self.none()
        
        return self.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(middle_name__icontains=query) |
            Q(specializations__name__icontains=query) |
            Q(city__name__icontains=query)
        ).distinct() 