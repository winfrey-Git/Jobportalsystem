from django import forms
from jobwebsite.models import UserProfile, Skill

class JobseekerProfileForm(forms.ModelForm):
    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'bio', 'skills', 'education']
        labels = {
            'profile_picture': 'Profile Picture:',
            'bio': 'Bio:',
            'skills': 'Skills:',
            'education': 'Education:',
            
        }
        widgets = {
            'bio': forms.Textarea(attrs={'placeholder': 'Tell us about yourself', 'rows': 3}),
            'education': forms.Textarea(attrs={'placeholder': 'Mention your educational qualifications', 'rows': 3}),
        }

    def save(self, commit=True):
        profile = super().save(commit=False)  # Get profile instance without saving
        if commit:
            profile.save()  # Save the profile first
            if 'skills' in self.cleaned_data:
                profile.skills.set(self.cleaned_data['skills'])  # Correct way to update ManyToManyField
            self.save_m2m()  # Ensure ManyToMany fields are properly saved
        return profile
