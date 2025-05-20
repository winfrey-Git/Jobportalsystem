from django import forms
from jobwebsite.models import Education

class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ['degree', 'institution', 'year']
        labels = {
            'degree': 'Degree',
            'institution': 'Institution Name',
            'year': 'Year of Completion',
        }
        widgets = {
            'degree': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., BSc in Computer Science'}),
            'institution': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Harvard University'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 2024'}),
        }
