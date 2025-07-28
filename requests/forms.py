from django import forms
from django.contrib.contenttypes.models import ContentType
from facilities.models import Clinic, RehabCenter, PrivateDoctor, OrganizationType
from .models import AnonymousRequest, DependentRequest


class AnonymousRequestAdminForm(forms.ModelForm):
    """
    Admin form for AnonymousRequest with organization selection.
    """
    organization_choice = forms.CharField(
        required=False,
        label='Выбранная организация',
        widget=forms.Select(choices=[('', '---------')]),
        help_text='Выберите конкретную организацию'
    )
    
    class Meta:
        model = AnonymousRequest
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        """
        Initialize the form with organization choices.
        
        Args:
            *args: Additional arguments
            **kwargs: Additional keyword arguments
        """
        super().__init__(*args, **kwargs)
        
        # Загружаем организации для выбранного типа
        if self.instance and self.instance.pk and self.instance.organization_type:
            self.fields['organization_choice'].widget.choices = self._get_organization_choices(
                self.instance.organization_type
            )
            self.fields['organization_choice'].initial = self.instance.assigned_organization
    
    def _get_organization_choices(self, organization_type):
        """
        Get list of organizations for selected type.
        
        Args:
            organization_type: OrganizationType instance
            
        Returns:
            list: List of tuples (value, label) for select widget
        """
        choices = [('', '---------')]
        
        if organization_type:
            if organization_type.name == 'Клиника':
                organizations = Clinic.objects.filter(is_active=True)
                for org in organizations:
                    choices.append((org.name, org.name))
            elif organization_type.name == 'Реабилитационный центр':
                organizations = RehabCenter.objects.filter(is_active=True)
                for org in organizations:
                    choices.append((org.name, org.name))
            elif organization_type.name == 'Частный врач':
                organizations = PrivateDoctor.objects.filter(is_active=True)
                for org in organizations:
                    choices.append((org.get_full_name(), org.get_full_name()))
        
        return choices

    def save(self, commit=True):
        """
        Save the form with organization choice handling.
        
        Args:
            commit: Whether to save to database
            
        Returns:
            AnonymousRequest: Saved instance
        """
        # Сохраняем organization_choice отдельно
        org_choice = self.cleaned_data.get('organization_choice')
        
        # Удаляем organization_choice из cleaned_data чтобы Django не пытался его сохранить
        if 'organization_choice' in self.cleaned_data:
            del self.cleaned_data['organization_choice']
        
        instance = super().save(commit=False)
        
        # Устанавливаем assigned_organization только если выбрана организация
        if org_choice:
            instance.assigned_organization = org_choice
        
        if commit:
            instance.save()
        return instance


class DependentRequestAdminForm(forms.ModelForm):
    """
    Admin form for DependentRequest with organization selection.
    """
    organization_choice = forms.CharField(
        required=False,
        label='Выбранная организация',
        widget=forms.Select(choices=[('', '---------')]),
        help_text='Выберите конкретную организацию'
    )
    
    class Meta:
        model = DependentRequest
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        """
        Initialize the form with organization choices.
        
        Args:
            *args: Additional arguments
            **kwargs: Additional keyword arguments
        """
        super().__init__(*args, **kwargs)
        
        # Загружаем организации для выбранного типа
        if self.instance and self.instance.pk and self.instance.organization_type:
            self.fields['organization_choice'].widget.choices = self._get_organization_choices(
                self.instance.organization_type
            )
            self.fields['organization_choice'].initial = self.instance.assigned_organization
    
    def _get_organization_choices(self, organization_type):
        """
        Get list of organizations for selected type.
        
        Args:
            organization_type: OrganizationType instance
            
        Returns:
            list: List of tuples (value, label) for select widget
        """
        choices = [('', '---------')]
        
        if organization_type:
            if organization_type.name == 'Клиника':
                organizations = Clinic.objects.filter(is_active=True)
                for org in organizations:
                    choices.append((org.name, org.name))
            elif organization_type.name == 'Реабилитационный центр':
                organizations = RehabCenter.objects.filter(is_active=True)
                for org in organizations:
                    choices.append((org.name, org.name))
            elif organization_type.name == 'Частный врач':
                organizations = PrivateDoctor.objects.filter(is_active=True)
                for org in organizations:
                    choices.append((org.get_full_name(), org.get_full_name()))
        
        return choices

    def save(self, commit=True):
        """
        Save the form with organization choice handling.
        
        Args:
            commit: Whether to save to database
            
        Returns:
            DependentRequest: Saved instance
        """
        # Сохраняем organization_choice отдельно
        org_choice = self.cleaned_data.get('organization_choice')
        
        # Удаляем organization_choice из cleaned_data чтобы Django не пытался его сохранить
        if 'organization_choice' in self.cleaned_data:
            del self.cleaned_data['organization_choice']
        
        instance = super().save(commit=False)
        
        # Устанавливаем assigned_organization только если выбрана организация
        if org_choice:
            instance.assigned_organization = org_choice
        
        if commit:
            instance.save()
        return instance 