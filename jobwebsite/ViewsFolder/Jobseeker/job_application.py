from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from jobwebsite.models import Job, Application, ResumeUpload, JobseekerProfile
from jobwebsite.forms.ApplyJobForm import JobApplicationForm
from jobwebsite.forms.JobResumeUploadForm import JobResumeUploadForm

@login_required
def apply_for_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    applicant_profile = request.user.JobseekerProfile
    existing_application = Application.objects.filter(applicant=request.user, job=job).first()

    if existing_application:
        messages.info(request, "You have already applied for this job.")
        return redirect('single_job', id=job.id)

    if request.method == 'POST':
        application_form = JobApplicationForm(request.POST)
        resume_form = JobResumeUploadForm(request.POST, request.FILES)

        if application_form.is_valid() and resume_form.is_valid():
            resume = resume_form.save(commit=False)
            resume.applicant = applicant_profile
            resume.job = job
            resume.save()

            application = application_form.save(user=request.user, job=job)  # Pass user and job
            application.resume = resume
            application.save()

            messages.success(request, "Your job application has been submitted successfully.")
            return redirect('single_job', id=job.id)

    else:
        application_form = JobApplicationForm()
        resume_form = JobResumeUploadForm()

    return render(request, 'job_seeker/apply.html', {
        'job': job,
        'application_form': application_form,
        'resume_form': resume_form
    })
