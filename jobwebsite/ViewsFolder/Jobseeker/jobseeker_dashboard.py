from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from jobwebsite.models import Application, JobseekerProfile, Job, ResumeUpload, Skill, Interview, CustomUser,Category
from jobwebsite.forms.ProfileUpdateForm import UserProfileUpdateForm
from jobwebsite.forms.JobResumeUploadForm import JobResumeUploadForm
from jobwebsite.forms.EducationForm import EducationForm
from jobwebsite.forms.ExperienceForm import ExperienceForm
from jobwebsite.forms.ResumeUploadForm import ResumeUploadForm
from jobwebsite.utils import extract_text_from_resume 
from django.db.models import Q
from django import template
from jobwebsite.models import Education, Experience
register = template.Library()


@login_required
def jobseeker_dashboard(request):
    user_profile = get_object_or_404(JobseekerProfile, user=request.user)
    profile_picture = user_profile.profile_picture.url if user_profile.profile_picture else "/static/default-profile.png"
    saved_jobs = Job.objects.filter(bookmarkjob__user=request.user)  # ✅ Corrected
    print("Saved Jobs:", saved_jobs)  # Debugging output

    total_applications = Application.objects.filter(applicant_id=request.user.id).count()
    
    interview_invites = Interview.objects.filter(application__applicant=request.user, status="scheduled")
    interviews_invited_count = interview_invites.count()  # ✅ Count for the card

    def calculate_profile_completion(profile):
        fields = ['profile_picture', 'phone_number', 'resume', 'bio', 'preferred_category', 'skills']
        filled_fields = sum(1 for field in fields if getattr(profile, field, None) is not None)
        return int((filled_fields / len(fields)) * 100) if fields else 0


    profile_completion = calculate_profile_completion(user_profile)
    job_applications = Application.objects.filter(applicant_id=request.user.id).order_by('-created_at')

    recommended_jobs = Job.objects.none()
    if user_profile.preferred_category:
        recommended_jobs = Job.objects.filter(category=user_profile.preferred_category, status="open")[:5]

    context = {
    'user_profile': user_profile,
    'profile_picture': profile_picture,
    'saved_jobs': saved_jobs,
    'total_applications': total_applications,
    'interview_invites': interview_invites,  # ✅ Pass the full list for display
    'interviews_invited_count': interviews_invited_count,  # ✅ Pass count for the card
    'profile_completion': profile_completion,
    'job_applications': job_applications,
    'notifications': notifications,
    'recommended_jobs': recommended_jobs,
    }

    return render(request, 'job_seeker/jobseeker_dashboard.html', context)

from django.http import HttpResponseBadRequest

@login_required
def profile_view(request, user_id=None):
    print(f"Received user_id: {user_id}")  # Debugging

    if user_id:
        try:
            user_id = int(user_id)  # Ensure user_id is an integer
            user = get_object_or_404(CustomUser, pk=user_id)
        except ValueError:
            return HttpResponseBadRequest("Invalid user ID format.")
    else:
        user = request.user  # Default to logged-in user

    # Fetch JobseekerProfile
    user_profile = get_object_or_404(JobseekerProfile, user=user)

    # Fetch related data
    job_applications = Application.objects.filter(applicant=user)  # Uses CustomUser
    resumes = ResumeUpload.objects.filter(applicant=user_profile)  # Uses JobseekerProfile

    # Fetch education and experience details
    education_entries = Education.objects.filter(jobseeker=user_profile)
    experience_entries = Experience.objects.filter(jobseeker=user_profile)

    context = {
        'user_profile': user_profile,
        'job_applications': job_applications,
        'resumes': resumes,
        'education_entries': education_entries,  # ✅ Education data
        'experience_entries': experience_entries,  # ✅ Experience data
    }
    
    return render(request, 'job_seeker/view_profile.html', context)

@login_required
def update_profile(request):
    user_profile = get_object_or_404(JobseekerProfile, user=request.user)
    categories = Category.objects.all()

    # Fetch existing education and experience records
    education_entries = Education.objects.filter(jobseeker=user_profile)
    experience_entries = Experience.objects.filter(jobseeker=user_profile)

    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=user_profile)

        # Handle Education edits or new entries
        education_forms = []
        if education_entries.exists():
            for education in education_entries:
                education_form = EducationForm(request.POST, instance=education)
                if education_form.is_valid():
                    education_form.save()
                education_forms.append(education_form)
        else:
            new_education_form = EducationForm(request.POST)
            if new_education_form.is_valid():
                new_education = new_education_form.save(commit=False)
                new_education.jobseeker = user_profile  # ✅ Associate with the jobseeker
                new_education.save()
            education_forms.append(new_education_form)

        # Handle Experience edits or new entries
        experience_forms = []
        if experience_entries.exists():
            for experience in experience_entries:
                experience_form = ExperienceForm(request.POST, instance=experience)
                if experience_form.is_valid():
                    experience_form.save()
                experience_forms.append(experience_form)
        else:
            new_experience_form = ExperienceForm(request.POST)
            if new_experience_form.is_valid():
                new_experience = new_experience_form.save(commit=False)
                new_experience.jobseeker = user_profile  # ✅ Associate with the jobseeker
                new_experience.save()
            experience_forms.append(new_experience_form)

        # Save the user profile form
        if form.is_valid():
            profile = form.save(commit=False)
            profile.save()
            form.save_m2m()
            messages.success(request, 'Profile updated successfully!')

        return redirect('view_profile')

    else:
        form = UserProfileUpdateForm(instance=user_profile)

        # Initialize education and experience forms
        education_forms = [EducationForm(instance=education) for education in education_entries] if education_entries.exists() else [EducationForm()]
        experience_forms = [ExperienceForm(instance=experience) for experience in experience_entries] if experience_entries.exists() else [ExperienceForm()]

    form.fields['skills'].queryset = Skill.objects.all()

    return render(request, 'job_seeker/update_profile.html', {
        'form': form,
        'education_forms': education_forms,
        'experience_forms': experience_forms,
        'education_entries': education_entries,
        'experience_entries': experience_entries,
        'categories': categories,
    })


@login_required
def delete_profile(request):
    profile = get_object_or_404(JobseekerProfile, user=request.user)

    if request.method == 'POST':
        user = request.user
        profile.delete()  # Delete the jobseeker profile

        # Mark the user as deleted
        user.is_active = False
        user.is_deleted = True
        user.save()

        messages.success(request, "Your account has been deleted. You cannot register again with this email.")
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

    # Get only open jobs
    jobs = Job.objects.filter(status='open')

    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) |
            Q(company__company_name__icontains=query) |  # ✅ Fixed lookup for company name
            Q(description__icontains=query)
        )

    if request.user.is_authenticated:
        try:
            user_profile = JobseekerProfile.objects.get(user=request.user)

            # ✅ Since preferred_category is a ForeignKey, check if it's not None
            if user_profile.preferred_category:
                jobs = jobs.filter(category=user_profile.preferred_category)

        except JobseekerProfile.DoesNotExist:
            pass  # If profile doesn't exist, continue without filtering

    return render(request, 'job_seeker/dashboard_search_results.html', {'jobs': jobs, 'query': query})


register = template.Library()

@register.simple_tag
def is_job_already_applied(user, job):
    if not user.is_authenticated:  # Prevent errors for anonymous users
        return False
    return Application.objects.filter(applicant=user, job=job).exists()

@login_required
def view_interview(request, interview_id):
    interview = get_object_or_404(Interview, id=interview_id)
    
    context = {
        'interview': interview,
    }
    return render(request, 'job_seeker/view_interview.html', context)