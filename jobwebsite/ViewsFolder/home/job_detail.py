from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from jobwebsite.models import Job

@login_required
def job_detail_view(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    is_employer = request.user.role == 'employer'  # Check if user is an employer
    is_jobseeker = request.user.role == 'employee'  # Check if user is a job seeker

    context = {
        'job': job,
        'is_employer': is_employer,
        'is_jobseeker': is_jobseeker
    }
    return render(request, 'job_detail.html', context)
