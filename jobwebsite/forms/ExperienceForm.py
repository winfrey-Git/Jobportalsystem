from django import forms
from jobwebsite.models import Experience

class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = ['job_title', 'company_in', 'company_location', 'years']
        labels = {
            'job_title': 'Job Title',
            'company_in': 'Company Name',
            'company_location': 'Company Location',
            'years': 'Years of Experience',
        }
        widgets = {
            'job_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Software Engineer'}),
            'company_in': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Google Inc.'}),
            'company_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., New York, USA'}),
            'years': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 5'}),
        }
