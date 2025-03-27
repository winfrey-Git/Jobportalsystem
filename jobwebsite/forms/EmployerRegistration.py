from django import forms
from jobwebsite.models import CustomUser
from django.contrib.auth.forms import UserCreationForm

class EmployerRegistration(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name','email', 'password1','password2']

        labels = {
            'first_name': 'First Name:',
            'last_name': 'Last Name:',
            'email': 'Email Address:',
            'password1': 'Password:',
            'password2': 'Confirm Password:',
        }

        widgets= {
            'first_name': forms.TextInput(attrs={'placeholder': 'Enter First Name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Enter Last Name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter Email'}),
            'password1': forms.PasswordInput(attrs={'placeholder': 'Enter Password'}),
            'password2': forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}),
        }


    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = "employer"
        if commit:
            user.save()
        return user