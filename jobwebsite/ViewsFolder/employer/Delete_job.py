from django.shortcuts import get_object_or_404, redirect,render
from django.contrib import messages
from jobwebsite.models import Job

def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    # Restrict deletion to the employer who created the job
    if job.created_by != request.user:
        messages.error(request, "You are not authorized to delete this job.")
        return redirect('employer_dashboard')

    if request.method == 'POST':
        job.delete()
        messages.success(request, "Job deleted successfully!")
        return redirect('employer_dashboard')

    context = {'job': job}
    return render(request, 'employer/delete_job.html', context)
