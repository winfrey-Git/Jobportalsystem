from django.shortcuts import render
from jobwebsite.models import JobseekerProfile, CustomUser
from django.db.models import Q

def search_resume(request):
    query = request.GET.get('q', '')
    results = []

    if query:
        # Search by user attributes or user profile fields
        results = JobseekerProfile.objects.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(user__email__icontains=query) |
            Q(role__icontains=query) |
            Q(skill_set__icontains=query) 
        )

    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'search_resume.html', context)
