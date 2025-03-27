# forms.py
from django import forms
from jobwebsite.models import ResumeUpload

class JobResumeUploadForm(forms.ModelForm):
    class Meta:
        model = ResumeUpload
        fields = ['resume']
