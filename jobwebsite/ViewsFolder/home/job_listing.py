from django.shortcuts import render
from jobwebsite.models import Job
from django.utils.timezone import now
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def job_list_View(request):
    # Fetch all jobs and select related company to optimize queries
    jobs = Job.objects.select_related('company').order_by('-posted_date')

    paginator = Paginator(jobs, 10)
    page_number = request.GET.get('page')

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1) 
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)  

    context = {
        'page_obj': page_obj,
        'now': now().date()  # Pass the current date to the template
    }
    return render(request, 'job_list.html', context)
