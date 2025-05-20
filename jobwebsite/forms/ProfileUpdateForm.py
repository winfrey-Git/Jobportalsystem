from django import forms
from jobwebsite.models import JobseekerProfile, Skill
from django.contrib.auth import get_user_model
from ckeditor.widgets import CKEditorWidget
from django.core.exceptions import ValidationError

User = get_user_model()

class UserProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'd-none'}),  # Hide default checkboxes
        required=False
    )
    job_alert = forms.BooleanField(required=False)

    class Meta:
        model = JobseekerProfile
        fields = ['first_name', 'last_name', 'skills', 'profile_picture', 'bio', 'preferred_category', 'resume', 'phone_number', 'job_alert']

        labels = {
            'first_name': 'First Name:',
            'last_name': 'Last Name:',
            'skills': 'Skills (Select Multiple):',
            'profile_picture': 'Profile Picture:',
            'bio': 'Bio:',
            'preferred_category': 'Preferred Job Category:',
            'resume': 'Upload Resume:',
            'phone_number': 'Phone Number:',
            'job_alert': 'Receive Job Alerts:'
        }

        widgets = {
            'bio': CKEditorWidget(),
            'preferred_category': forms.Select(attrs={'class': 'form-control'}),
            'resume': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].initial = self.instance.user.first_name
        self.fields['last_name'].initial = self.instance.user.last_name

    def clean_resume(self):
        resume = self.cleaned_data.get('resume')

        if resume:
            file_extension = resume.name.split('.')[-1].lower()
            if file_extension not in ['pdf', 'docx']:
                raise ValidationError("The resume must be a PDF or DOCX file.")
            max_size = 5 * 1024 * 1024  
            if resume.size > max_size:
                raise ValidationError("The resume file size must be less than 5MB.")

        return resume

    def save(self, commit=True):
        user_profile = super().save(commit=False)
        user_profile.user.first_name = self.cleaned_data['first_name']
        user_profile.user.last_name = self.cleaned_data['last_name']

        if commit:
            user_profile.user.save()  # Save name updates in User model
            user_profile.save()
            self.save_m2m()  # Save many-to-many relationships (skills)
        
        return user_profile
