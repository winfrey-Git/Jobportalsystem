from django import forms
from jobwebsite.models import Job
from ckeditor.widgets import CKEditorWidget


class JobEditionForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title',
                  'location',
                  'type', 
                  'category',
                  'salary',
                  'description',
                  'tags',
                  'deadline_date',
                  'vacancy',
                  ]
        labels = {
            'title': 'Job Title :',
            'location': 'Job Location :',
            'salary': 'Salary :',
            'description': 'Job Description :',
            'tags': 'Tags :',
            'deadline_date': 'Submission Deadline :',
        }
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'eg: Software Developer'}),
            'location': forms.TextInput(attrs={'placeholder': 'eg: Nairobi'}),
            'salary': forms.TextInput(attrs={'placeholder': 'eg: KES 80,000 - KES 84,500'}),
            'tags': forms.TextInput(attrs={'placeholder': 'Use comma separated. eg: Python, JavaScript'}),
            'deadline_date': forms.DateInput(attrs={'placeholder': 'YYYY-MM-DD'}),
        }

    def clean_type(self):
        job_type = self.cleaned_data.get('type')
        if not job_type:
            raise forms.ValidationError("Job type is required")
        return job_type

    def clean_category(self):
        category = self.cleaned_data.get('category')
        if not category:
            raise forms.ValidationError("Category is required")
        return category

    def save(self, user=None, commit=True):
        job = super().save(commit=False)
        if user:
            job.user = user  # Set the user if provided
        if commit:
            job.save()
        return job
