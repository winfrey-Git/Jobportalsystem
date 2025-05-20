from django import forms
from jobwebsite.models import Job

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            'title', 'description', 'location', 'type', 'category', 'salary', 
            'deadline_date', 'is_published', 'is_featured', 'vacancy', 'tags', 
            'status', 'responsibilities', 'requirements'
        ]

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'salary': forms.TextInput(attrs={'class': 'form-control'}),
            'deadline_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'vacancy': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'tags': forms.TextInput(attrs={'class': 'form-control'}),  # Assuming text input for tag manager
            'status': forms.Select(attrs={'class': 'form-control'}),
            'responsibilities': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'requirements': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }
