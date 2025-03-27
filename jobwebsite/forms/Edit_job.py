from django import forms
from jobwebsite.models import Job

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'description', 'location', 'type', 'category', 'salary', 'deadline_date', 'is_published']

        widgets = {
            'deadline_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
