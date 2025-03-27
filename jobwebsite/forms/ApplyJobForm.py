from django import forms
from jobwebsite.models import Application

class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['phone', 'cover_letter']  # Removed 'resume' to avoid redundancy

        labels = {
            'phone': 'Phone Number:',
            'cover_letter': 'Cover Letter:',
        }

        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Phone Number'}),
            'cover_letter': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Write your cover letter...'}),
        }

    def save(self, user=None, job=None, commit=True):
        """Save job application and associate it with logged-in user and job."""
        if not user or not job:
            raise ValueError("User and job must be provided to save the application.")
        
        application = super().save(commit=False)
        application.applicant = user  # Associate with logged-in user
        application.job = job  # Associate with selected job
        
        if commit:
            application.save()
        return application
