from django import forms
from jobwebsite.models import CustomUser, Company

class EmployerProfileUpdateForm(forms.ModelForm):
    full_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Full Name"}),
    )
    company_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Company Name"}),
    )
    company_address = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Company Address"}),
    )
    company_contact_phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Company Phone"}),
    )
    company_website = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={"class": "form-control", "placeholder": "Enter Company Website"}),
    )
    company_industry = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Industry Type"}),
    )
    company_logo = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = CustomUser
        fields = ["gender"]  # Removed 'email' field

        labels = {
            "gender": "Gender",
        }

        widgets = {
            "gender": forms.Select(attrs={"class": "form-control"}, choices=[("M", "Male"), ("F", "Female")]),
        }

    def save(self, commit=True):
        user = super().save(commit=False)

        # Update full name if provided
        full_name = self.cleaned_data.get("full_name")
        if full_name:
            user.first_name = full_name.split()[0]
            user.last_name = " ".join(full_name.split()[1:]) if len(full_name.split()) > 1 else ""

        if commit:
            user.save()

        # Save company details
        if hasattr(user, "company"):
            company = user.company
            company_fields = [
                "company_name", "company_address",
                "company_contact_phone", "company_website", "company_industry", "company_logo"
            ]

            updated = False
            for field in company_fields:
                if self.cleaned_data.get(field):
                    setattr(company, field, self.cleaned_data[field])
                    updated = True

            if updated:
                company.save()

        return user
