from django.contrib.auth import authenticate
from django import forms
from jobwebsite.models import User

class UserLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email Address'}))
    password = forms.CharField(strip=False, widge=forms.PasswordInput(attrs={'placeholder': 'Password'}))

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")

        if email and password:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise forms.ValidationError("User does not exist.")
            
            if not user.check_password(password):
                raise forms.ValidationError("Incorrect Password.")
           
            if not user.is_active:
                 forms.ValidationError("User is not active.")
            
            self.user = authenticate(email=email, password=password)
            if not self.user:
                raise forms.ValidationError("Invalid Login credentials")
            return super().clean()
        
    def get_user(self):
        return getattr(self, 'user', None)