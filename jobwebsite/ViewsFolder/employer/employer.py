from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from jobwebsite.models import Job, Application, SavedResume, CustomUser,Interview,ResumeUpload,Notification,Company
from jobwebsite.forms.JobForm import JobForm
from jobwebsite.forms.InterviewSchedule import InterviewScheduleForm
from jobwebsite.forms.EmployerProfileUpdateForm import EmployerProfileUpdateForm
from jobwebsite.utils import notify_applicant,match_resume_to_job
from django.db.models import Q,Count
from django.core.mail import send_mail
from jobwebsite.forms.InterviewUpdateStatus import InterviewStatusUpdateForm
from django.http import JsonResponse
from django.utils.timezone import now
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from reportlab.platypus import Table, TableStyle, Image
from reportlab.lib import colors
import matplotlib
matplotlib.use("Agg") 
import matplotlib.pyplot as plt
import base64
import io
import json


@login_required
def employer_dashboard_view(request):
    employer = request.user 

    try:
        company = employer.company  
    except AttributeError:
        company = None  

    jobs = Job.objects.filter(company=company) if company else Job.objects.none()

    applications = Application.objects.filter(job__company=company) if company else Application.objects.none()

    scheduled_interviews = Interview.objects.filter(application__job__company=company) if company else Interview.objects.none()
    
    total_applicants = applications.values('applicant').distinct().count()  



    context = {
        'jobs': jobs,
        'applications': applications,
        'scheduled_interviews': scheduled_interviews,
        'total_applicants': total_applicants,
    }
    return render(request, 'employer/employer_dashboard.html', context)

@login_required
def get_employer_chart_data(request):
    employer = request.user

    try:
        company = employer.company  
    except AttributeError:
        company = None  

    if not company:
        return JsonResponse({"error": "No company associated with this employer"}, status=400)

    # Fetch applications per job
    job_labels = []
    applications_data = []
    jobs = Job.objects.filter(company=company)

    for job in jobs:
        job_labels.append(job.title)
        applications_count = Application.objects.filter(job=job).count()
        applications_data.append(applications_count)

    # Fetch shortlisted vs rejected applications
    shortlisted_count = Application.objects.filter(job__company=company, status="shortlisted").count()
    rejected_count = Application.objects.filter(job__company=company, status="rejected").count()

    data = {
        "applications": {
            "labels": job_labels,
            "data": applications_data
        },
        "shortlisted": {
            "labels": ["Shortlisted", "Rejected"],
            "data": [shortlisted_count, rejected_count]
        }
    }
    
    return JsonResponse(data)

@login_required
def manage_jobs(request):
    employer = request.user  
    try:
        company = employer.company  
    except AttributeError:
        company = None  

    jobs = Job.objects.filter(company=company) if company else Job.objects.none()
    return render(request, 'employer/manage_jobs.html', {'jobs': jobs})

@login_required
def employer_notifications_view(request):
    # Ensure the logged-in user has an associated company
    if not hasattr(request.user, 'company'):
        return render(request, 'employer/employer_notifications.html', {
            'notifications': [],
            'new_applications': 0,
            'interview_responses': 0,
            'system_updates': 0,
        })

    notifications = Notification.objects.filter(user=request.user).order_by('-date_created')

    # Fix the queries to filter by company
    new_applications = Application.objects.filter(job__company=request.user.company, status='pending').count()
    interview_responses = Interview.objects.filter(application__job__company=request.user.company).exclude(status='pending').count()
    system_updates = notifications.filter(notification_type='system_update').count()

    context = {
        'notifications': notifications,
        'new_applications': new_applications,
        'interview_responses': interview_responses,
        'system_updates': system_updates,
    }
    return render(request, 'employer/employer_notifications.html', context)


@login_required
def edit_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, company=request.user.company)  # Use company
    if request.method == "POST":
        form = JobForm(request.POST, request.FILES, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Job updated successfully!")
            return redirect('manage_jobs')
    else:
        form = JobForm(instance=job)
    return render(request, 'employer/edit_job.html', {'form': form, 'job': job})

@login_required
def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, company=request.user.company)  # Use company
    if request.method == "POST":
        job.delete()
        messages.success(request, "Job deleted successfully!")
        return redirect('manage_jobs')
    return render(request, 'employer/confirm_delete.html', {'job': job})


@login_required
def candidate_management(request):
    applications = Application.objects.filter(job__company=request.user.company).select_related('applicant', 'job')

    if request.method == "POST":
        application_id = request.POST.get("application_id")
        new_status = request.POST.get("status")

        application = get_object_or_404(Application, id=application_id, job__company=request.user.company)
        application.status = new_status
        application.save()

        # Email notification logic remains the same...
        email_messages = {
            "shortlisted": "Congratulations! You have been shortlisted for the job.",
            "interview_scheduled": "You have been invited for an interview. Please check your email for details.",
            "rejected": "Unfortunately, your application was not successful.",
            "hired": "Congratulations! You have been hired for the position."
        }

        if new_status in email_messages:
            send_mail(
                "Job Application Update",
                f"Dear {application.applicant.get_full_name()},\n\n"
                f"{email_messages[new_status]}\n\n"
                "Best regards,\nYour Company",
                "yourcompany@example.com",
                [application.applicant.email],
                fail_silently=True,
            )

        messages.success(request, f"Application status updated to {new_status.title()}.")
        return redirect("candidate_management")

    return render(request, 'employer/candidate_management.html', {'applications': applications})


def view_candidate(request, application_id):
    """View details of a specific candidate's job application."""
    application = get_object_or_404(Application, id=application_id)
    return render(request, 'employer/view_candidate.html', {'application': application})

def shortlist_candidate(request, application_id):
    """Shortlist a candidate for a job."""
    application = get_object_or_404(Application, id=application_id)
    application.status = "Shortlisted"
    application.save()
    messages.success(request, f"{application.candidate.user.get_full_name} has been shortlisted successfully!")
    return redirect('employer_dashboard')

@login_required
def schedule_interview(request, application_id):
    """Schedule an interview for a job applicant."""
    application = get_object_or_404(Application, id=application_id)
    
    # Check if an interview is already scheduled for this application
    interview, created = Interview.objects.get_or_create(application=application)

    if request.method == "POST":
        form = InterviewScheduleForm(request.POST, instance=interview)
        if form.is_valid():
            form.save()

            # ✅ Update the application status
            application.status = "Interview Scheduled"  # Ensure this status exists
            application.save()

            # ✅ Send email notification
            subject = "Interview Invitation - Job Application"
            message = (
                f"Dear {application.applicant.get_full_name()},\n\n"
                f"You have been invited for an interview for the position: {application.job.title}.\n"
                f"Date: {interview.date}\n"
                f"Time: {interview.time}\n"
                f"Mode: {interview.mode}\n"
                f"{'Interview Link: ' + interview.interview_link if interview.interview_link else ''}\n\n"
                f"Best Regards,\n{request.user.get_full_name()} (Employer)"
            )
            send_mail(
                subject,
                message,
                request.user.email,  # ✅ Use employer's email as sender
                [application.applicant.email],
                fail_silently=True,
            )

            messages.success(request, f"Interview scheduled successfully for {application.applicant.get_full_name()}!")
            return redirect('employer_dashboard')

    else:
        form = InterviewScheduleForm(instance=interview)

    return render(request, 'employer/schedule_interview.html', {'form': form, 'application': application})


@login_required
def update_interview_status(request, interview_id):
    """Allows the employer to update the interview status and sync application status"""
    interview = get_object_or_404(Interview, id=interview_id, application__job__user=request.user)

    if request.method == "POST":
        form = InterviewStatusUpdateForm(request.POST, instance=interview)
        if form.is_valid():
            interview = form.save()

            # Sync application status based on interview status
            if interview.status == "completed":
                interview.application.status = "shortlisted"  # Adjust this as needed
            elif interview.status == "canceled":
                interview.application.status = "pending"  # Reset application status
            interview.application.save()

            messages.success(request, f"Interview status updated to {interview.get_status_display()}.")
            return redirect('candidate_management')  # Adjust as needed
    else:
        form = InterviewStatusUpdateForm(instance=interview)

    return render(request, 'employer/update_interview_status.html', {'form': form, 'interview': interview})

@login_required
def update_application_status(request, application_id):
    application = get_object_or_404(Application, id=application_id)

    if request.method == "POST":
        new_status = request.POST.get("status")
        application.status = new_status
        application.save()

        # Ensure the logged-in employer has an email
        sender_email = request.user.email if request.user.email else "noreply@jobportal.com"

        # Call the function with both arguments
        notify_applicant(application, sender_email)

        messages.success(request, "Application status updated successfully.")
        return redirect("employer_dashboard")

    return redirect("employer_dashboard")


@login_required
def job_applications(request):
    jobs = Job.objects.filter(company=request.user.company, application__isnull=False).distinct().prefetch_related('application__applicant')
    return render(request, 'employer/job_applications.html', {'jobs': jobs})




def shortlist_applicants(job_id):
    job = get_object_or_404(Job, id=job_id)
    applications = Application.objects.filter(job=job)
    
    for application in applications:
        if application.resume:
            score = match_resume_to_job(application.resume.parsed_text, job.description)
            if score > 0.7:  # Adjust the threshold
                application.status = "shortlisted"
                application.save()

def application_detail(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    return render(request, 'employer/application_detail.html', {'application': application})

@login_required
def search_resumes(request):
    query = request.GET.get('q', '')

    if query:
        resumes = ResumeUpload.objects.filter(
            Q(applicant__email__icontains=query) |  # Corrected field
            Q(parsed_text__icontains=query)
        )
    else:
        resumes = ResumeUpload.objects.all()

    # Ensure skills list is handled safely
    for resume in resumes:
        user_profile = getattr(resume.applicant, 'userprofile', None)
        resume.skills_list = list(user_profile.skills.values_list("name", flat=True)) if user_profile else []

    return render(request, 'employer/search_resumes.html', {'resumes': resumes, 'query': query})


@login_required
def view_resume(request, id):
    """View a specific resume."""
    resume = get_object_or_404(ResumeUpload, id=id)

    return render(request, 'employer/view_resume.html', {'resume': resume})


@login_required
def save_resume(request, id):
    """Save a resume to the employer's saved list."""
    resume = get_object_or_404(ResumeUpload, id=id)

    if request.user.role != "employer":
        messages.error(request, "Only employers can save resumes.")
        return redirect('view_resume', id=resume.id)

    saved_resume, created = SavedResume.objects.get_or_create(
        employer=request.user,  
        resume=resume
    )

    messages.success(request, "Resume saved successfully.") if created else messages.info(request, "Already saved.")
    return redirect('view_resume', id=resume.id)



@login_required
def performance_analytics(request):
    employer = request.user
    jobs = Job.objects.filter(company=employer.company)


    # Key Metrics
    total_jobs = jobs.count()
    total_applications = Application.objects.filter(job__in=jobs).count()
    total_shortlisted = Application.objects.filter(job__in=jobs, status="shortlisted").count()
    total_hired = Application.objects.filter(job__in=jobs, status="hired").count()

    # Recent Applications (Latest 10)
    recent_applications = Application.objects.filter(job__in=jobs).order_by("-created_at")[:10]

    # Job Performance Overview Query
    job_performance = jobs.annotate(
        applications=Count("application"),
        shortlisted=Count("application", filter=Q(application__status="shortlisted")),
        hired=Count("application", filter=Q(application__status="hired")),
    ).values("title", "applications", "shortlisted", "hired", "status")

    # Debugging: Print to see if job_performance has data
    print(list(job_performance))

    # Define Last Six Months Dynamically
    today = now().date()
    last_six_months = [(today.replace(day=1) - timedelta(days=30 * i)).month for i in range(6)][::-1]
    month_labels = [datetime(2025, m, 1).strftime("%b") for m in last_six_months]

    # Get Actual Applications Per Month
    applications_per_month = [
        Application.objects.filter(job__in=jobs, created_at__month=m).count() for m in last_six_months
    ]

    # Generate Graph
    buffer = io.BytesIO()
    plt.figure(figsize=(7, 4))
    plt.bar(month_labels, applications_per_month, color="blue")
    plt.xlabel("Month")
    plt.ylabel("Applications")
    plt.title("Application Trends (Last 6 Months)")
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.savefig(buffer, format="png")
    plt.close()
    buffer.seek(0)
    
    # Convert graph to base64
    graph_url = base64.b64encode(buffer.getvalue()).decode("utf-8")

    context = {
        "total_jobs": total_jobs,
        "total_applications": total_applications,
        "total_shortlisted": total_shortlisted,
        "total_hired": total_hired,
        "recent_applications": recent_applications,
        "job_performance": job_performance,  # ✅ Add this line
        "month_labels": month_labels,
        "applications_per_month": applications_per_month,
        "graph_url": f"data:image/png;base64,{graph_url}",
    }

    return render(request, "employer/performance_analytics.html", context)




@login_required
def print_performance_report(request):
    employer = request.user
    jobs = Job.objects.filter(company=employer.company)
    # Key Metrics
    total_jobs = jobs.count()
    total_applications = Application.objects.filter(job__in=jobs).count()
    total_shortlisted = Application.objects.filter(job__in=jobs, status="shortlisted").count()
    total_hired = Application.objects.filter(job__in=jobs, status="hired").count()

    # Recent Applications (Latest 10)
    recent_applications = Application.objects.filter(job__in=jobs).order_by("-created_at")[:10]

    # Define Last Six Months Dynamically
    today = now().date()
    last_six_months = [(today.replace(day=1) - timedelta(days=30 * i)).month for i in range(6)][::-1]
    month_labels = [datetime(2025, m, 1).strftime("%b") for m in last_six_months]

    # Get Actual Applications Per Month
    applications_per_month = [
        Application.objects.filter(job__in=jobs, created_at__month=m).count() for m in last_six_months
    ]

    # Create PDF Response
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "inline; filename=Performance_Report.pdf"

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter
    y_position = height - 50

    # PDF Title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(180, y_position, "Performance Analytics Report")
    y_position -= 30

    # Section: Key Metrics
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, y_position, "📊 Key Metrics")
    y_position -= 20

    p.setFont("Helvetica", 12)
    p.drawString(100, y_position, f"✔ Total Job Posts: {total_jobs}")
    y_position -= 20
    p.drawString(100, y_position, f"✔ Total Applications: {total_applications}")
    y_position -= 20
    p.drawString(100, y_position, f"✔ Shortlisted Candidates: {total_shortlisted}")
    y_position -= 20
    p.drawString(100, y_position, f"✔ Hired Candidates: {total_hired}")
    y_position -= 40

    # Generate and Add Graph Image
    buffer = io.BytesIO()
    plt.figure(figsize=(5, 3))
    plt.bar(month_labels, applications_per_month, color='blue')
    plt.title("Application Trends (Last 6 Months)")
    plt.xlabel("Month")
    plt.ylabel("Applications")
    plt.savefig(buffer, format="png")
    plt.close()
    buffer.seek(0)

    # Add Image to PDF
    img = Image(buffer, width=300, height=150)
    img.drawOn(p, 130, y_position - 150)
    y_position -= 180

    # Section: Job Performance Table
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, y_position, "📌 Job Performance")
    y_position -= 20

    data = [["Job Title", "Applications", "Shortlisted", "Hired", "Status"]]
    for job in jobs:
        data.append([
            job.title,
            Application.objects.filter(job=job).count(),
            Application.objects.filter(job=job, status="shortlisted").count(),
            Application.objects.filter(job=job, status="hired").count(),
            "Open" if job.status == "open" else "Closed"
        ])

    table = Table(data, colWidths=[120, 80, 80, 80, 80])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
    ]))

    table.wrapOn(p, width, height)
    table.drawOn(p, 50, y_position - 100)
    y_position -= 130

    # Section: Recent Applications
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, y_position, "📝 Recent Applications")
    y_position -= 20

    app_data = [["Candidate Name", "Job Applied", "Status", "Date Applied"]]
    for app in recent_applications:
        app_data.append([app.applicant.get_full_name(), app.job.title, app.status.capitalize(), app.created_at.strftime("%d %b %Y")])

    app_table = Table(app_data, colWidths=[120, 120, 100, 100])
    app_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.green),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ("BACKGROUND", (0, 1), (-1, -1), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
    ]))

    app_table.wrapOn(p, width, height)
    app_table.drawOn(p, 50, y_position - 100)

    # Finalize PDF
    p.showPage()
    p.save()
    return response


@login_required
def view_employer_profile(request):
    # Get the logged-in employer
    employer = get_object_or_404(CustomUser, id=request.user.id, role="employer")

    # Fetch the company linked to this employer
    company = get_object_or_404(Company, user=employer)

    context = {
        'employer': employer,
        'company': company,
    }
    return render(request, 'employer/view_employer_profile.html', context)

@login_required
def edit_employer_profile(request):
    employer = request.user
    if request.method == "POST":
        form = EmployerProfileUpdateForm(request.POST, request.FILES, instance=employer)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect("view_employer_profile")
    else:
        form = EmployerProfileUpdateForm(instance=employer)
    return render(request, "employer/edit_employer_profile.html", {"form": form})

@login_required
def delete_employer_profile(request):
    employer = request.user
    if request.method == "POST":
        employer.jobs.all().delete()  # Assuming related_name="jobs"
        employer.delete()
        messages.success(request, "Your account has been deleted.")
        logout(request)
        return redirect('home')
    return render(request, 'employer/delete_employer_profile.html')

@login_required
def job_list(request):
    """Displays all jobs posted by the logged-in employer."""
    jobs = Job.objects.filter(user=request.user)  # Ensure 'user' is the correct field
    return render(request, "employer/job_listing.html", {"jobs": jobs})

@login_required
def active_jobs(request):
    """Displays only active (open) jobs posted by the logged-in employer."""
    jobs = Job.objects.filter(user=request.user, status="open")  
    return render(request, "employer/active_jobs.html", {"jobs": jobs})

@login_required
def expired_jobs(request):
    """Displays expired (closed) jobs posted by the logged-in employer."""
    jobs = Job.objects.filter(user=request.user, status="closed")  
    return render(request, "employer/expired_jobs.html", {"jobs": jobs})
