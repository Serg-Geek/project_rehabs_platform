from django import forms
from .models import ConsultationRequest

class ConsultationRequestForm(forms.ModelForm):
    class Meta:
        model = ConsultationRequest
        fields = ['contact_method', 'contact_info', 'message']
        widgets = {
            'contact_method': forms.Select(attrs={
                'class': 'section-form__select',
                'id': 'contact-method'
            }),
            'contact_info': forms.TextInput(attrs={
                'class': 'section-form__input',
                'id': 'contact-input',
                'placeholder': '+7 (XXX) XXX-XX-XX'
            }),
            'message': forms.Textarea(attrs={
                'class': 'section-form__input',
                'id': 'message',
                'placeholder': 'Ваше сообщение'
            })
        } 