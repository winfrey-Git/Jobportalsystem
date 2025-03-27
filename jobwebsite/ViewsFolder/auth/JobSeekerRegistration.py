from django.shortcuts import render, redirect
from jobwebsite.forms.JobSeekerRegistrationForm import JobSeekerRegistration

def Jobseeker_Registration_View(request):
    form = JobSeekerRegistration()  

    if request.method == "POST":
        form = JobSeekerRegistration(request.POST)
        if form.is_valid():
            form.save()  
            return redirect('login')

    context = {
        "form": form,
    }
    return render(request, "job_seeker/jobseeker_register.html", context)
