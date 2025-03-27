from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from jobwebsite.models import Application, JobseekerProfile, Job, Notification, ResumeUpload, Skill, Interview, CustomUser
from jobwebsite.forms.ProfileUpdateForm import UserProfileUpdateForm
from jobwebsite.forms.JobResumeUploadForm import JobResumeUploadForm
from jobwebsite.forms.ResumeUploadForm import ResumeUploadForm
from jobwebsite.utils import extract_text_from_resume 
from django.db.models import Q
from django import template
register = template.Library()

@login_required
def jobseeker_dashboard(request):
    user_profile = get_object_or_404(JobseekerProfile, user=request.user)
    profile_picture = user_profile.profile_picture.url if user_profile.profile_picture else "/static/default-profile.png"
    saved_jobs = user_profile.saved_jobs.all()
    print("Saved Jobs:", saved_jobs)  # Debugging output

    total_applications = Application.objects.filter(applicant_id=request.user.id).count()
    interviews_scheduled = Interview.objects.filter(application__applicant=request.user).count()

    def calculate_profile_completion(profile):
        fields = ['profile_picture', 'phone_number', 'resume', 'address']
        filled_fields = sum(1 for field in fields if getattr(profile, field, None) is not None)
        return int((filled_fields / len(fields)) * 100) if fields else 0

    profile_completion = calculate_profile_completion(user_profile)
    job_applications = Application.objects.filter(applicant_id=request.user.id).order_by('-created_at')
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-date_created')

    recommended_jobs = Job.objects.none()
    if user_profile.preferred_category:
        recommended_jobs = Job.objects.filter(category=user_profile.preferred_category, status="open")[:5]

    context = {
        'user_profile': user_profile,
        'profile_picture': profile_picture,
        'saved_jobs': saved_jobs,
        'total_applications': total_applications,
        'interviews_scheduled': interviews_scheduled,
        'profile_completion': profile_completion,
        'job_applications': job_applications,
        'notifications': notifications,
        'recommended_jobs': recommended_jobs,
        
    }
    
    return render(request, 'job_seeker/jobseeker_dashboard.html', context)


@login_required
def profile_view(request, user_id=None):
    if user_id:
        user = get_object_or_404(CustomUser, id=user_id)  # Get the applicant by ID
    else:
        user = request.user  # Default to logged-in user if no ID is provided

    user_profile = get_object_or_404(JobseekerProfile, user=user)
    job_applications = Application.objects.filter(applicant=user)
    resumes = ResumeUpload.objects.filter(applicant__user=user)
    saved_jobs = user_profile.saved_jobs.all() if not user_id else None  # Only jobseeker sees saved jobs

    context = {
        'user_profile': user_profile,
        'job_applications': job_applications,
        'resumes': resumes,
        'saved_jobs': saved_jobs,
    }
    return render(request, 'job_seeker/view_profile.html', context)



@login_required
def update_profile(request):
    user_profile = get_object_or_404(JobseekerProfile, user=request.user)

    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            profile = form.save(commit=False)  
            profile.save()
            form.save_m2m() 
            messages.success(request, 'Profile updated successfully!')
            return redirect('view_profile')
    else:
        form = UserProfileUpdateForm(instance=user_profile)

    form.fields['skills'].queryset = Skill.objects.all()

    return render(request, 'job_seeker/update_profile.html', {'form': form})


@login_required
def delete_profile(request):
    profile = get_object_or_404(JobseekerProfile, user=request.user)

    if request.method == 'POST':
        profile.delete()
        messages.success(request, "Your profile has been deleted successfully.")
        return redirect('home')

    return render(request, 'job_seeker/delete_profile.html')


@login_required
def upload_resume_for_profile(request):
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            resume_upload = form.save(commit=False)
            resume_upload.applicant = request.user.userprofile  # Correctly assign user profile
            resume_upload.save()
            messages.success(request, "Resume uploaded successfully!")
            return redirect('view_profile')
    else:
        form = ResumeUploadForm()

    return render(request, 'job_seeker/upload_resume.html', {'form': form})


@login_required
def upload_resume_for_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    applicant_profile = get_object_or_404(JobseekerProfile, user=request.user)

    if request.method == 'POST':
        form = JobResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            resume_upload = form.save(commit=False)
            resume_upload.applicant = applicant_profile
            resume_upload.job = job
            resume_upload.save()

            if resume_upload.resume: 
                extracted_text = extract_text_from_resume(resume_upload.resume.path)
                resume_upload.parsed_text = extracted_text 
                resume_upload.save()

            messages.success(request, "Resume uploaded for job application!")
            return redirect('single_job', job_id=job.id)
    else:
        form = JobResumeUploadForm()

    return render(request, 'job_seeker/upload_resume_for_job.html', {'form': form, 'job': job})

@login_required
def job_applications(request):
    job_applications = Application.objects.filter(applicant=request.user).order_by('-created_at')
    return render(request, 'job_seeker/job_applications.html', {'job_applications': job_applications})


@login_required
def notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-date_created')
    notifications.update(is_read=True)  # Mark all as read
    return render(request, 'job_seeker/notifications.html', {'notifications': notifications})


@login_required
def recommended_jobs(request):
    user_profile = get_object_or_404(JobseekerProfile, user=request.user)
    recommended_jobs = Job.objects.filter(category=user_profile.preferred_category)

    return render(request, 'job_seeker/recommended_jobs.html', {'recommended_jobs': recommended_jobs})


@login_required
def saved_jobs_list(request):
    user_profile = JobseekerProfile.objects.select_related("user").get(user=request.user)
    saved_jobs = user_profile.saved_jobs.all()

    context = {"saved_jobs": saved_jobs}
    return render(request, "job_seeker/saved_jobs.html", context)


@login_required
def remove_saved_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    if job in request.user.userprofile.saved_jobs.all():
        request.user.userprofile.saved_jobs.remove(job)
    return redirect('jobseeker_dashboard')


def dashboard_search_result(request):
    query = request.GET.get('query', '')

    jobs = Job.objects.filter(status='active')

    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) |
            Q(company_name__icontains=query) |
            Q(description__icontains=query)  
        )

    if request.user.is_authenticated:
        user_profile = request.user.userprofile
        preferred_categories = user_profile.preferred_categories.all() 
        preferred_locations = user_profile.preferred_locations.all()  
        
        jobs = jobs.filter(category__in=preferred_categories, location__in=preferred_locations)

    return render(request, 'job_seeker/dashboard_search_results.html', {'jobs': jobs, 'query': query})

@register.simple_tag
def is_job_already_applied(user, job):
    return Application.objects.filter(applicant=user, job=job).exists()