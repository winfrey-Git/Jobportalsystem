from django import forms
from jobwebsite.models import CustomUser
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

class JobSeekerRegistration(UserCreationForm):
    agree_to_terms = forms.BooleanField(
        required=True,
        error_messages={'required': 'You must agree to the terms and conditions to register.'}
    )
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name','email', 'password1','password2', 'gender']
        labels = {
            'first_name': 'First Name:',
            'last_name': 'Last Name:',
            'email': 'Email Address:',
            'password1': 'Password:',
            'password2': 'Confirm Password:',
            'gender': 'Gender:'
        }

        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Enter First Name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Enter Last Name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter Email'}),
            'password1': forms.PasswordInput(attrs={'placeholder': 'Enter Password'}),
            'password2': forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}),
        }

    def clean_gender(self):
        gender = self.cleaned_data.get('gender')
        if not gender:
            raise forms.ValidationError('Gender is required')
        return gender

    def clean_agree_to_terms(self):
        agree = self.cleaned_data.get('agree_to_terms')
        if not agree:
            raise ValidationError("You must agree to the terms and conditions.")
        return agree

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = "employee"
        if commit:
            user.save()
        return user
