from django.shortcuts import render, redirect
from django.contrib import messages
from jobwebsite.forms.JobSeekerRegistrationForm import JobSeekerRegistration
from jobwebsite.models import CustomUser  # Assuming your custom user model is named CustomUser

def Jobseeker_Registration_View(request):
    form = JobSeekerRegistration()

    if request.method == "POST":
        form = JobSeekerRegistration(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            
            # Check if this email belongs to a previously deleted user
            if CustomUser.objects.filter(email=email, is_deleted=True).exists():
                messages.error(request, "This email address has already been used and cannot be reused for registration.")
                return render(request, "job_seeker/jobseeker_register.html", {"form": form})

            form.save()
            messages.success(request, "Registration successful! You can now log in.")
            return redirect('login')

    return render(request, "job_seeker/jobseeker_register.html", {"form": form})
