from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.core.cache import cache
from django.http import Http404
from django.db.models import Q
from jobwebsite.models import Job, Company

def single_job_view(request, id):
    try:
        id = int(id)
    except ValueError:
        raise Http404("Invalid job ID")

    job_cache_key = f'job_{id}'
    job = cache.get(job_cache_key)
    if job is None:
        job = get_object_or_404(Job, id=id)
        cache.set(job_cache_key, job, 60 * 15)

    company = job.company

    # Fetch related jobs based on shared tags
    related_job_list = []
    if hasattr(job, "tags") and job.tags.exists():
        related_job_list = Job.objects.filter(tags__in=job.tags.all()).exclude(id=job.id).distinct().order_by('-posted_date')[:10]

    paginator = Paginator(related_job_list, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 🆕 Add today's date
    today = timezone.now().date()

    context = {
        'job': job,
        'company': company,
        'page_obj': page_obj,
        'total': len(related_job_list),
        'today': today,   # ✅ Pass today's date to template
    }

    return render(request, 'single_job.html', context)
