from django import template
from django.contrib.auth import get_user_model
from jobwebsite.models import Application, BookmarkJob, Job  

register = template.Library()
User = get_user_model()

@register.simple_tag
def is_job_already_applied(user, job):
    if not isinstance(user, User) or not isinstance(job, Job):
        return False 
    return Application.objects.filter(applicant=user, job=job).exists()

@register.simple_tag(takes_context=True)
def is_job_already_saved(context, user, job):
    request = context['request']  
    return BookmarkJob.objects.filter(user=user, job=job).exists()
