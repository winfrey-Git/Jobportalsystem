from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from jobwebsite.models import Job, BookmarkJob
def save_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    saved_job, created = BookmarkJob.objects.get_or_create(user=request.user, job=job)

    if created:
        messages.success(request, "Job saved successfully!")
    else:
        saved_job.delete()
        messages.warning(request, "Job removed successfully!")

    return redirect(request.META.get('HTTP_REFERER', 'job_list'))

