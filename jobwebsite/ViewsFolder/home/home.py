from django.shortcuts import render
from jobwebsite.models import Job, CustomUser
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils import timezone

def home_view(request):
    # Fetch only published and open jobs
    published_jobs = Job.objects.filter(is_published=True).order_by('-posted_date')
    jobs = published_jobs.filter(status="open")

    # Get distinct locations from published jobs
    locations = published_jobs.values_list('location', flat=True).distinct()

    # Count total candidates and companies
    total_candidates = CustomUser.objects.filter(role='employee').count()
    total_companies = CustomUser.objects.filter(role='employer').count()

    # Get featured jobs (trending jobs)
    trending_jobs = Job.objects.filter(is_featured=True, is_published=True, status="open",deadline_date__gte=timezone.now().date()).order_by('-posted_date')[:6]

    # Paginate job listings (3 per page)
    paginator = Paginator(jobs, 3)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Handle AJAX request for pagination
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        job_lists = list(page_obj.object_list.values("id", "title", "location", "type", "status", "company_id"))
        
        data = {
            'job_lists': job_lists,
            'current_page_no': page_obj.number,
            'locations': list(locations),
            'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
            'prev_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
            'no_of_page': paginator.num_pages,
        }
        return JsonResponse(data)  

    # Context for the template
    context = {
        'total_candidates': total_candidates,
        'total_companies': total_companies,
        'total_jobs': jobs.count(),
        'total_completed_jobs': published_jobs.filter(status="closed").count(),
        'page_obj': page_obj,
        "trending_jobs": trending_jobs,
    }

    return render(request, 'home.html', context)
