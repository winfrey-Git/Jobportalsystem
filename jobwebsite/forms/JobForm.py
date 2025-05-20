from taggit.forms import TagWidget
from django import forms
from jobwebsite.models import Job
from ckeditor.widgets import CKEditorWidget
from datetime import date

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
            'tags': TagWidget(attrs={'class': 'form-control', 'placeholder': 'e.g., Python, JavaScript'}),  # ✅ Fix
            'deadline_date': forms.DateInput(attrs={'class': 'form-control','placeholder': 'YYYY-MM-DD','type': 'date','min': date.today().strftime('%Y-%m-%d'),'max': (date.today().replace(year=date.today().year + 3)).strftime('%Y-%m-%d'),}),
            'description': CKEditorWidget(),
            'responsibilities': CKEditorWidget(),
            'requirements': CKEditorWidget(),
        }

    def clean_tags(self):
        """
        Ensure tags are properly formatted: 
        - No extra spaces
        - Capitalized correctly
        - No duplicate tags
        """
        tags = self.cleaned_data.get('tags', [])
        cleaned_tags = []

        for tag in tags:
            cleaned_tag = tag.strip().title()  # Remove spaces & capitalize first letter
            cleaned_tags.append(cleaned_tag)

        return cleaned_tags

    def save(self, user=None, commit=True):
        if not user:
            raise ValueError("A user must be provided when saving a job.")

        job = super().save(commit=False)
        job.user = user  # Assign user correctly

        if commit:
            job.save()
            if 'tags' in self.cleaned_data:
                job.tags.set(self.cleaned_data['tags'])  # ✅ Assign tags properly
            self.save_m2m()

        return job
