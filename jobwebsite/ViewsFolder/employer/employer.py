from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from jobwebsite.models import Job, Application, SavedResume, CustomUser,Interview,ResumeUpload,Company,Experience,JobseekerProfile
from jobwebsite.forms.JobForm import JobForm
from jobwebsite.forms.InterviewSchedule import InterviewScheduleForm
from jobwebsite.forms.EmployerProfileUpdateForm import EmployerProfileUpdateForm
from jobwebsite.utils import notify_applicant,match_resume_to_job
from django.db.models import Q,Count
from django.core.mail import send_mail
from jobwebsite.forms.InterviewUpdateStatus import InterviewStatusUpdateForm
from django.http import JsonResponse,FileResponse
import mimetypes
from django.utils.timezone import now
from datetime import datetime, timedelta
from django.template.loader import render_to_string
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

    scheduled_interviews = Interview.objects.filter(application__job__company=company, status="scheduled").count() if company else 0
    
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
from django.db.models import Prefetch
@login_required
def manage_jobs(request):
    employer = request.user  
    try:
        company = employer.company  
    except AttributeError:
        company = None  

    if company:
        jobs = Job.objects.filter(company=company).prefetch_related(
            Prefetch('application', queryset=Application.objects.all(), to_attr='applications_list')
        )
    else:
        jobs = Job.objects.none()

    for job in jobs:
        print(f"Job: {job.title}, Applications Count: {len(job.applications_list)}")  # Debugging

    return render(request, 'employer/manage_jobs.html', {'jobs': jobs})



@login_required
def edit_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, company=request.user.company)
    next_url = request.GET.get('next', '')  # Preserve the previous page

    if request.method == "POST":
        form = JobForm(request.POST, request.FILES, instance=job)
        if form.is_valid():
            form.save(user=request.user)  # Pass the user when saving
            messages.success(request, "Job updated successfully!")
            # If next_url is provided and valid, redirect to it, otherwise redirect to the job detail page
            if next_url:
                return redirect(next_url)
            return redirect('job_detail.html', id=job.id)  # Default redirect to job detail page

    else:
        form = JobForm(instance=job)

    return render(request, 'employer/edit_job.html', {'form': form, 'job': job, 'next': next_url})


def job_detail_view(request, job_id):
    job = get_object_or_404(Job, id=job_id, company=request.user.company)
    return render(request, 'employer/job_detail.html', {'job': job})

@login_required
def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, company=request.user.company)

    if request.method == "POST":
        job.delete()
        messages.success(request, "Job deleted successfully!")
        return redirect('manage_jobs')  # Always go to manage_jobs after deletion

    return render(request, 'employer/confirm_delete.html', {'job': job})



@login_required
def candidate_management(request):
    try:
        # Fetch the employer's company
        employer_company = request.user.company  # Ensure your User model has a One-To-One with Company

        # Filter applications for jobs that belong to this company
        applications = Application.objects.filter(job__company=employer_company)

        return render(request, 'employer/candidate_management.html', {'applications': applications})
    except AttributeError:
        # If the user doesn't have a company, return an empty list
        return render(request, 'employer/candidate_management.html', {'applications': []})


def shortlist_candidate(request, application_id):
    """Shortlist a candidate for a job."""
    application = get_object_or_404(Application, id=application_id)
    application.status = "Shortlisted"
    application.save()
    messages.success(request, f"{application.candidate.user.get_full_name} has been shortlisted successfully!")
    return redirect('employer_dashboard')

@login_required
def schedule_interview(request, application_id):
    """Allows an employer to schedule an interview only if one doesn't already exist or previous one was canceled."""
    current_date = timezone.now().date()
    max_date = current_date + timedelta(days=365*4)
    
    application = get_object_or_404(
        Application,
        id=application_id,
        job__company__user=request.user
    )
    
    # Check if an active interview already exists — do not allow scheduling again
    active_interview = Interview.objects.filter(
        application=application
    ).exclude(status="canceled").first()
    
    if active_interview:
        messages.warning(request, "This application already has a scheduled interview. Please use reschedule instead.")
        return redirect("interview_management")
    
    if request.method == "POST":
        date_value = request.POST.get("date")
        time_value = request.POST.get("time") or "10:00:00"
        mode_value = request.POST.get("mode")
        interview_link_value = request.POST.get("interview_link", "").strip()
        
        # Validation
        if not date_value:
            messages.error(request, "Interview date is required.")
            return render(request, "employer/schedule_interview.html", {"application": application})
        
        if mode_value == "Online" and not interview_link_value:
            messages.error(request, "Meeting link is required for online interviews.")
            return render(request, "employer/schedule_interview.html", {"application": application})
        
        # Check for existing interview and update it instead of creating a new one
        existing_interview = Interview.objects.filter(application=application).first()
        
        if existing_interview:
            # Update the existing interview record instead of creating a new one
            existing_interview.date = date_value
            existing_interview.time = time_value
            existing_interview.mode = mode_value
            existing_interview.interview_link = interview_link_value if mode_value == "Online" else None
            existing_interview.status = "scheduled"
            existing_interview.save()
            messages.success(request, "Interview scheduled successfully.")
        else:
            # Create a new interview if none exists
            Interview.objects.create(
                application=application,
                date=date_value,
                time=time_value,
                mode=mode_value,
                interview_link=interview_link_value if mode_value == "Online" else None,
                status="scheduled"
            )
            messages.success(request, "Interview scheduled successfully.")
        
        return redirect("interview_management")
    
    return render(request, "employer/schedule_interview.html", {
        "current_date": current_date, 
        "max_date": max_date,
        "application": application
    })
from django.utils import timezone

@login_required
def reschedule_interview(request, interview_id):
    """Handles rescheduling an existing interview."""
    current_date = timezone.now().date()
    max_date = current_date + timedelta(days=365*4)
    # Retrieve the interview using the interview ID and ensure it's linked to the logged-in employer's application
    interview = get_object_or_404(Interview, id=interview_id, application__job__company__user=request.user)

    # Handle form submission (POST request)
    if request.method == "POST":
        # Retrieve the new date, time, mode, and interview link
        date_value = request.POST.get("date")
        time_value = request.POST.get("time")
        mode_value = request.POST.get("mode")
        interview_link_value = request.POST.get("interview_link", "")

        # Validation: Ensure that the date is provided
        if not date_value:
            messages.error(request, "Interview date is required.")
            return render(request, "employer/reschedule_interview.html", {"interview": interview})

        # If the mode is "Online", ensure the interview link is provided
        if mode_value == "Online" and not interview_link_value:
            messages.error(request, "Meeting link is required for Online interviews.")
            return render(request, "employer/reschedule_interview.html", {"interview": interview})

        # Update the interview details
        interview.date = date_value
        interview.time = time_value if time_value else "10:00:00"  # Use default time if none provided
        interview.mode = mode_value
        interview.interview_link = interview_link_value if mode_value == "Online" else None
        interview.status = "scheduled"  # Ensure that the interview status is "scheduled"
        interview.save()  # Save the updated interview

        messages.success(request, "Interview rescheduled successfully.")
        return redirect("interview_management")  # Redirect to interview management page or any other page

    # Render the reschedule interview page with the current interview details
    return render(request, "employer/reschedule_interview.html", {'current_date': current_date, 'max_date': max_date, 'interview': interview})


@login_required
def cancel_interview(request, interview_id):
    """Marks an interview as canceled."""
    interview = get_object_or_404(Interview, id=interview_id, application__job__company__user=request.user)

    if request.method == "POST":  # Ensure only POST requests can cancel
        interview.status = "canceled"  # Update status
        interview.save()
        messages.success(request, "Interview has been canceled.")
        return redirect("interview_management")

    messages.error(request, "Invalid request method.")
    return redirect("interview_management")


def interview_management(request):
    """Displays the list of scheduled interviews for the employer."""
    # Filter interviews for the jobs where the employer (company) is associated with the logged-in user (request.user)
    interviews = Interview.objects.filter(
        status="scheduled",
        application__job__company__user=request.user  # Correct relationship to filter by employer (company) and user
    ).select_related("application__applicant", "application__job")

    return render(request, "employer/interview_management.html", {"interviews": interviews})




@login_required
def update_interview_status(request, interview_id):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect("interview_management")
        
    # Get the interview, ensuring it's related to the current employer
    interview = get_object_or_404(
        Interview,
        id=interview_id,
        application__job__company__user=request.user
    )

    # Only update if the interview is scheduled
    if interview.status == 'scheduled':
        interview.status = 'completed'
        interview.save()
        messages.success(request, "Interview marked as completed.")
    else:
        messages.warning(request, "This interview is already completed.")

    return redirect('interview_management')



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
        return redirect("candidate_management")

    return redirect("application_detail")


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


@login_required
def application_detail(request, application_id):
    
    # Rest of your view code...
    # Fetch the application, ensuring the job is associated with the user's company
    application = get_object_or_404(Application, id=application_id, job__company=request.user.company)
    
    # Fetch the applicant (user associated with the application)
    applicant = application.applicant
    
    # Access the JobseekerProfile associated with the applicant
    jobseeker_profile = applicant.jobseeker_profile  # Accessing the JobseekerProfile
    
    # Fetch education and experience entries related to the jobseeker profile
    education = jobseeker_profile.education_entries.all() if jobseeker_profile.education_entries.exists() else None
    experience = jobseeker_profile.experience_entries.all() if jobseeker_profile.experience_entries.exists() else None
    
    # Check if an interview exists for the application
    latest_interview = application.interview if hasattr(application, "interview") else None
    
    context = {
        'application': application,
        'latest_interview': latest_interview,
        'education': education,
        'experience': experience
    }
    
    # Check if it's an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Return just the content without layout for AJAX requests
        return render(request, 'employer/application_detail.html', context)
    
    # Return the full page with layout for direct navigation
    return render(request, 'employer/application_detail.html', context)


@login_required
def search_resumes(request):
    employer = request.user
    resumes = []
    query = request.GET.get('q', '').strip()
    
    # Only process and display results if a search query was submitted
    if query:
        try:
            company = employer.company
            jobs = Job.objects.filter(company=company)
        except:
            jobs = []
        
        # Get applications for those jobs (including resume they used)
        applications = Application.objects.filter(job__in=jobs).select_related('resume', 'applicant')
        
        # Handle search query
        keywords = query.split(",")
        query_filter = Q()
        for keyword in keywords:
            query_filter |= Q(resume__parsed_text__icontains=keyword.strip())
        applications = applications.filter(query_filter)
        
        # Get the resumes from applications and add skills/experience
        seen_resume_ids = set()
        
        for application in applications:
            if application.resume and application.resume.id not in seen_resume_ids:
                seen_resume_ids.add(application.resume.id)
                resume = application.resume
                
                # The ResumeUpload model has 'applicant' field which is a JobseekerProfile
                jobseeker_profile = resume.applicant
                
                # Fetch skills for the applicant
                resume.skills_list = list(jobseeker_profile.skills.values_list("name", flat=True))
                
                # Fetch experience for the applicant
                resume.experience = Experience.objects.filter(jobseeker=jobseeker_profile).order_by('-years')
                
                # Add user information for displaying name
                resume.user = jobseeker_profile.user
                
                resumes.append(resume)
    
    context = {
        'resumes': resumes,
        'query': query,
        'search_performed': bool(query),
    }
    
    # Check if this is an AJAX request (for dashboard integration)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'employer/search_resumes.html', context)
    else:
        # For direct access, you might want to render with your full template
        return render(request, 'employer/search_resumes.html', context)

@login_required
def view_resume(request, id):
    """Serve the resume file (PDF or DOCX) for viewing."""
    resume = get_object_or_404(ResumeUpload, id=id)

    if not resume.resume:
        return HttpResponse("Resume file not found", status=404)

    file_path = resume.resume.path
    content_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'

    return FileResponse(open(file_path, 'rb'), content_type=content_type)

@login_required
def save_resume(request, id):
    """Save a resume to the employer's saved list and redirect to saved resumes page."""
    
    resume = get_object_or_404(ResumeUpload, id=id)

    # Ensure the resume belongs to an application for the employer's jobs
    application = Application.objects.filter(
        resume=resume,
        job__company__user=request.user
    ).first()

    if not application:
        messages.error(request, "You can only save resumes from candidates who applied to your job.")
        return redirect('search_resumes')  # Redirect back to search if unauthorized

    if request.user.role != "employer":
        messages.error(request, "Only employers can save resumes.")
        return redirect('search_resumes')

    # Save the resume
    saved_resume, created = SavedResume.objects.get_or_create(
        employer=request.user,
        resume=resume
    )

    if created:
        messages.success(request, "Resume saved successfully.")
    else:
        messages.info(request, "This resume was already saved.")

    # ✅ Redirect to saved resumes page
    return redirect('saved_resumes')  

@login_required
def saved_resumes(request):
    """Display all resumes saved by the employer."""
    if request.user.role != "employer":  # Ensure only employers can access
        messages.error(request, "Only employers can view saved resumes.")
        return redirect("dashboard")  # Redirect to the appropriate page

    # Get only resumes from jobseekers who applied to the employer's jobs
    saved_resumes = SavedResume.objects.filter(
        employer=request.user, 
        resume__application__job__company__user=request.user
    ).select_related("resume__applicant")

    return render(request, "employer/saved_resumes.html", {"saved_resumes": saved_resumes})

@login_required
def delete_saved_resume(request, id):
    """Remove a saved resume from the employer's list."""
    saved_resume = get_object_or_404(SavedResume, id=id, employer=request.user)
    saved_resume.delete()
    messages.success(request, "Resume removed successfully.")
    return redirect("saved_resumes")


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

    # Define Last Six Weeks Dynamically
    today = now().date()
    last_six_weeks = [(today - timedelta(weeks=i)).strftime("%U") for i in range(6)][::-1]  # Week numbers
    week_labels = [f"Week {week}" for week in last_six_weeks]

    # Get Actual Applications Per Week
    applications_per_week = [
        Application.objects.filter(job__in=jobs, created_at__week=(today - timedelta(weeks=i)).isocalendar()[1]).count()
        for i in range(6)
    ]

    # Generate Graph
    buffer = io.BytesIO()
    plt.figure(figsize=(7, 4))
    plt.bar(week_labels, applications_per_week, color="green")
    plt.xlabel("Week")
    plt.ylabel("Applications")
    plt.title("Application Trends (Last 6 Weeks)")
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
        "week_labels": week_labels,
        "applications_per_week": applications_per_week,
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
    plt.bar(month_labels, applications_per_month, color='green')
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
        ("BACKGROUND", (0, 0), (-1, 0), colors.orange),
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
    company = employer.company  

    if request.method == "POST":
        form = EmployerProfileUpdateForm(request.POST, request.FILES, instance=employer)

        if form.is_valid():
            employer_update = form.save(commit=False)  

            # Handle employer fields manually
            if form.cleaned_data.get('full_name'):
                full_name = form.cleaned_data['full_name']
                employer_update.first_name, employer_update.last_name = (
                    full_name.split(' ', 1) if ' ' in full_name else (full_name, "")
                )

            if form.cleaned_data.get('gender'):
                employer_update.gender = form.cleaned_data['gender']

            employer_update.save()  

            # Handle company updates manually
            company_fields = ['company_name', 'company_contact_phone', 
                              'company_website', 'company_address', 'company_industry']

            updated = False  

            for field in company_fields:
                if field in form.cleaned_data and form.cleaned_data[field]:
                    setattr(company, field, form.cleaned_data[field])
                    updated = True

            if 'company_logo' in request.FILES:
                company.company_logo = request.FILES['company_logo']
                updated = True

            if updated:
                company.save()  


            messages.success(request, "Your profile has been updated successfully.")
            
            # Return the profile view for AJAX requests
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return render(request, "employer/view_employer_profile.html", {"employer": employer})
            
            return redirect("view_employer_profile")
    else:
        form = EmployerProfileUpdateForm(instance=employer)
    
    context = {"form": form, "employer": employer}
    return render(request, "employer/edit_employer_profile.html", context)

@login_required
def delete_employer_account(request):
    if request.method == 'POST':
        user = request.user
        user.is_deleted = True  # Soft delete
        user.is_active = False
        user.save()
        messages.success(request, "Your account has been deleted. You can no longer use this email to register.")
        return redirect('home')

@login_required
def job_list(request):
    """Displays all jobs posted by the logged-in employer."""  
    jobs = Job.objects.filter(company__user=request.user) \
                    .annotate(application_count=Count('application'))  # Counting related applications
    return render(request, "employer/job_listing.html", {"jobs": jobs})


@login_required
def active_jobs(request):
    """Displays only active (open) jobs posted by the logged-in employer, including the application count."""
    jobs = Job.objects.filter(company__user=request.user, status="open") \
                      .annotate(application_count=Count('application'))  # Counting related applications

    return render(request, "employer/active_jobs.html", {"jobs": jobs})


@login_required
def expired_jobs(request):
    """Displays expired (closed) jobs posted by the logged-in employer."""
    jobs = Job.objects.filter(company__user=request.user, status="closed")\
                      .annotate(application_count=Count('application'))
 
    return render(request, "employer/expired_jobs.html", {"jobs": jobs})
