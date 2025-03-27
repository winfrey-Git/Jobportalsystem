from django import forms
from jobwebsite.models import JobseekerProfile

class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model = JobseekerProfile
        fields = ['resume']
