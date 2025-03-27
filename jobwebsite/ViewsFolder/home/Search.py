from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.timezone import now
from jobwebsite.models import Job, Company

def search_result_view(request):
    job_list = Job.objects.filter(is_published=True).order_by('-posted_date')
    print("Total Jobs Before Filtering:", job_list.count())

    job_title_or_company_name = request.GET.get('job_title_or_company_name', '').strip()
    location = request.GET.get('location', '').strip()
    job_type = request.GET.get('job_type', '').strip()  # Fixed 'type' to 'job_type' to match the form field
    industry = request.GET.get('industry', '').strip()  # Added industry field

    if job_title_or_company_name:
        job_list = job_list.filter(
            Q(title__icontains=job_title_or_company_name) | 
            Q(company__company_name__icontains=job_title_or_company_name)  # Use company_name instead of name
        )


    if location:
        job_list = job_list.filter(location__icontains=location)

    if job_type:
        job_list = job_list.filter(type__iexact=job_type)

    if industry:
        job_list = job_list.filter(company__industry__icontains=industry)  
    print("Total Jobs After Filtering:", job_list.count())  # Debugging

    paginator = Paginator(job_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': job_title_or_company_name,
        'selected_location': location,
        'selected_job_type': job_type,
        'selected_industry': industry,  # Include industry in the context
    }

    return render(request, 'search_result.html', context)
