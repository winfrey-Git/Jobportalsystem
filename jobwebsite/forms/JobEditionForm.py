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
                  'company_name',
                  'company_description',
                  'vacancy',
                  ]
        labels = {
            'title': 'Job Title :',
            'location': 'Job Location :',
            'salary' : 'Salary :',
            'description': 'Job Description :',
            'tags': 'Tags :',
            'deadline_date': 'Submission Deadline :',
            'company_name': 'Company Name :',
            'company_description': 'Company Description :',
            'url': 'Website :'
        }
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'eg: Software Developer'}),
            'location': forms.TextInput(attrs={'placeholder': 'eg: Nairobi'}),
            'salary': forms.TextInput(attrs={'placeholder': 'eg: KES 80,000 - KES 84,500'}),
            'tags': forms.TextInput(attrs={'placeholder': 'Use comma separated. eg: Python, JavaScript'}),
            'deadline_date': forms.DateInput(attrs={'placeholder': 'YYYY-MM-DD'}),
            'company_name': forms.TextInput(attrs={'placeholder': 'Company Name'}),
            'url': forms.TextInput(attrs={'placeholder': 'https://example.com'})
        }

        def clean_job_type(self):
            type = self.cleaned_data.get('type')
            if not type:
                raise forms.ValidationError("Service is required")
            return type

        def cleaned_category(self):
            category = self.cleaned_data.get('category')
            if not category:
                raise forms.ValidationError("category is required")
            return category
        
        def save(self, commit=True):
            job = super().save(commit=False)
            if commit:
                job.save()
            return job
        