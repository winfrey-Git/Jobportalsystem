from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from jobwebsite.models import Category, Company
from jobwebsite.forms.JobForm import JobForm

@login_required
def create_job_view(request):
    user = request.user
    categories = Category.objects.all()

    try:
        company = user.company
    except Company.DoesNotExist:
        messages.error(request, "You need to create a company profile before posting a job.")
        return redirect("create_company")

    if request.method == 'POST':
        form = JobForm(request.POST, request.FILES)
        if form.is_valid():
            job = form.save(user=user, commit=False)
            job.company = company
            job.save()  # Save the job instance first

            form.instance = job  # Very important if form was customized
            form.save_m2m()  # 🔥 Save the many-to-many fields like tags!

            messages.success(request, 'You have successfully posted your job! Please wait for review.')
            return redirect(reverse("single_job", kwargs={'id': job.id}))
        else:
            messages.error(request, "There were errors in the form. Please check and try again.")
    else:
        form = JobForm()

    context = {
        'form': form,
        'categories': categories
    }

    return render(request, 'employer/job_posting.html', context)
