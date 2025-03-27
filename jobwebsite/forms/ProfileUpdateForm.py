from django import forms
from jobwebsite.models import JobseekerProfile, Skill
from ckeditor.widgets import CKEditorWidget
from django.core.exceptions import ValidationError

class UserProfileUpdateForm(forms.ModelForm):
    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        widget=forms.CheckboxSelectMultiple(),  # This allows skills to be selected properly
        required=False,
        label='Skills (Select Multiple):'
    )

    class Meta:
        model = JobseekerProfile
        fields = ['skills', 'profile_picture', 'bio', 'education', 'preferred_category', 'resume']

        labels = {
            'skills': 'Skills (Select Multiple):',
            'profile_picture': 'Profile Picture:',
            'bio': 'Bio:',
            'education': 'Education:',
            'preferred_category': 'Preferred Job Category:',
            'resume': 'Upload Resume:'
        }

        widgets = {
            'bio': CKEditorWidget(),
            'education': CKEditorWidget(),
            'preferred_category': forms.Select(attrs={'class': 'form-control'}),
            'resume': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

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
        if commit:
            user_profile.save()
            self.save_m2m()  # Save many-to-many relationships (skills)
        return user_profile
