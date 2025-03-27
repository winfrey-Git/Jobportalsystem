from django import forms
from jobwebsite.models import Interview

class InterviewStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = ['status']
