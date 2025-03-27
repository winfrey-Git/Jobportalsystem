from django.shortcuts import render, get_object_or_404, redirect
from jobwebsite.models import Job
from jobwebsite.forms import JobForm  # Assuming you have a JobForm defined
from django.contrib import messages

def edit_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    # Restrict editing to only the employer who created the job
    if job.created_by != request.user:
        messages.error(request, "You are not authorized to edit this job.")
        return redirect('employer_dashboard')

    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Job updated successfully!")
            return redirect('employer_dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = JobForm(instance=job)

    context = {
        'form': form,
        'job': job,
    }
    return render(request, 'employer/edit_job.html', context)
