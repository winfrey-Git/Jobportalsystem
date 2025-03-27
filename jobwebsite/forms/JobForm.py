from django import forms
from jobwebsite.models import Job
from ckeditor.widgets import CKEditorWidget

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            'title', 'location', 'type', 'category', 'salary', 'description', 'tags', 
            'deadline_date','vacancy', 'responsibilities', 'requirements'
        ]
        
        labels = {
            'title': 'Job Title:',
            'location': 'Job Location:',
            'salary': 'Salary:',
            'description': 'Job Description:',
            'tags': 'Tags:',
            'deadline_date': 'Submission Deadline:',
            'responsibilities': 'Responsibilities:',
            'requirements': 'Requirements:',
        }
        
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Software Developer'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Nairobi'}),
            'salary': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., KES 80,000 - KES 84,500'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Use comma-separated values, e.g., Python, JavaScript'}),
            'deadline_date': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'YYYY-MM-DD', 'type': 'date'}),
            'description': CKEditorWidget(),
            'responsibilities': CKEditorWidget(),
            'requirements': CKEditorWidget(),
        }

    def clean_type(self):
        job_type = self.cleaned_data.get('type')
        if not job_type:
            raise forms.ValidationError("Job type is required.")
        return job_type

    def clean_category(self):
        category = self.cleaned_data.get('category')
        if not category:
            raise forms.ValidationError("Category is required.")
        return category

    def save(self, user=None, commit=True):
        if not user:
            raise ValueError("A user must be provided when saving a job.")
        
        job = super().save(commit=False)
        job.user = user  # Assign user correctly
        if commit:
            job.save()
            self.save_m2m()  # Save many-to-many relationships if any
        return job

