from django import forms
from jobwebsite.models import Job

class EmployerBusinessProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ["company_description", "company_logo", "location", "contact_email", "contact_phone"]

        labels = {
            "company_description": "Company Description:",
            "company_logo": "Company Logo:",
            "location": "Company Location:",
            "contact_email": "Contact Email:",
            "contact_phone": "Contact Phone:",
        }

        widgets = {
            "company_description": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Briefly describe your company"}),
            "location": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Location"}),
            "contact_email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Enter Contact Email"}),
            "contact_phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Contact Number"}),
        }
