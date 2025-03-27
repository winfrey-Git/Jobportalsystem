from django import forms
from jobwebsite.models import CustomUser

class EmployerProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "email"]
        
        labels = {
            "first_name": "Company Name:",
            "last_name": "Company Address:",
            "email": "Company Email Address:",
        }

        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Company Name"}),
            "last_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Company Address"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Enter Company Email Address"}),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if CustomUser.objects.exclude(id=self.instance.id).filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email
