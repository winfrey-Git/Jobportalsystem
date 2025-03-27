from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.core.cache import cache
from jobwebsite.models import Job, Company  # Import the Company model
from django.http import Http404

def single_job_view(request, id):
    try:
        id = int(id)  # Ensure ID is an integer
    except ValueError:
        raise Http404("Invalid job ID")

    job = cache.get(f'job_{id}')
    if job is None:
        job = get_object_or_404(Job, id=id)
        cache.set(f'job_{id}', job, 60 * 15)

    company = job.company  # Assuming Job model has a ForeignKey to Company
    
    related_job_list = job.tags.similar_objects() if hasattr(job, "tags") else []

    paginator = Paginator(related_job_list, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'job': job,
        'company': company,  # Pass company details to template
        'page_obj': page_obj,
        'total': len(related_job_list),
    }

    return render(request, 'single_job.html', context)
