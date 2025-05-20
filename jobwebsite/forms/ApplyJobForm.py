from django import forms
from jobwebsite.models import Application
import re

class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['phone', 'cover_letter']
        labels = {
            'phone': 'Phone Number:',
            'cover_letter': 'Cover Letter:',
        }
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 0712345678 or +254712345678',
                'pattern': '^(\\+254|254|0[17])\\d{8}$',  # HTML5 validation
                'title': 'Enter Kenyan number (07..., 01..., +254... or 254...)'
            }),
            'cover_letter': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'placeholder': 'Write your cover letter...'
            }),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        
        if not phone:
            raise forms.ValidationError("Phone number is required.")

        # Remove all non-digit characters except leading +
        cleaned_phone = re.sub(r'(?!^\+)[^0-9]', '', phone)

        # Check for valid Kenyan prefixes
        if not re.match(r'^(\+?254|0[17])\d+$', cleaned_phone):
            raise forms.ValidationError(
                "Invalid prefix. Use +254, 254, 07, or 01."
            )

        # Extract pure digits for length validation
        digits = cleaned_phone.lstrip('+').replace('254', '', 1) if cleaned_phone.startswith(('+254', '254')) else cleaned_phone[1:]
        
        # Validate total length (9 digits after prefix)
        if len(digits) != 9:
            raise forms.ValidationError(
                "Phone number must be 9 digits after prefix (e.g., 712345678 for +254712345678)"
            )

        # Standardize to 254 format
        if cleaned_phone.startswith('0'):
            standardized_phone = '254' + cleaned_phone[1:]
        elif cleaned_phone.startswith('+254'):
            standardized_phone = cleaned_phone[1:]
        elif cleaned_phone.startswith('254'):
            standardized_phone = cleaned_phone
        else:
            raise forms.ValidationError("Invalid phone number format")

        return standardized_phone

    def save(self, user=None, job=None, commit=True):
        """Save job application and associate it with logged-in user and job."""
        if not user or not job:
            raise ValueError("User and job must be provided to save the application.")
        
        application = super().save(commit=False)
        application.applicant = user
        application.job = job
        
        if commit:
            application.save()
        return application