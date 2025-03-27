from django import forms
from jobwebsite.models import Interview

class InterviewScheduleForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = ['date', 'time', 'mode', 'interview_link']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'mode': forms.Select(attrs={'class': 'form-control'}),
            'interview_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Enter meeting link (if online)'}),
        }
