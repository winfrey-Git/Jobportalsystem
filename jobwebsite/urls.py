from django.urls import path
from jobwebsite.ViewsFolder.home import home, about_us, contact_us, job_listing, profile, profile, terms_and_conditions
from jobwebsite.ViewsFolder.employer import job_posting, employer
from jobwebsite.ViewsFolder.Jobseeker import job_application, jobseeker_dashboard
from jobwebsite.ViewsFolder.auth import login, logout, password_reset,JobSeekerRegistration,EmployerRegistration
from django.contrib.auth import views as auth_views
from jobwebsite.ViewsFolder.home import Search,single_job, save_job
from jobwebsite.ViewsFolder.home import home,privacy_policy,FAQs,blog
from django.conf.urls.static import static
from django.conf import settings


urlpatterns=[
    path('', home.home_view, name='home'),
    path('about/', about_us.about, name='about'),
    path('contact/', contact_us.contact, name='contact'),
    path('faqs/', FAQs.faqs_view, name='faqs'),
    path('user-guide/', FAQs.user_guide_view, name='user_guide'),
    path('thank-you/', contact_us.thank_you, name='thank_you'),
    path('logout/', logout.logout_view, name='logout'),
    path('login/', login.login_view, name='login'),
    path('job_list/', job_listing.job_list_View, name='job_list'),
    path('employer/dashboard/',employer.employer_dashboard_view, name='employer_dashboard'),
    path('jobseeker/dashboard/',jobseeker_dashboard.jobseeker_dashboard, name='jobseeker_dashboard'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name="password_reset.html"), name="password_reset"),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name="password_reset_done.html"), name="password_reset_done"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="password_reset_confirm.html"), name="password_reset_confirm"),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name="password_reset_complete.html"), name="password_reset_complete"),
    path('search_result/', Search.search_result_view, name='search_result'),
    path('job_posting/',job_posting.create_job_view, name='job_posting'),
    path('single_job/<int:id>/',single_job.single_job_view, name='single_job'),
    path('save-job/<int:job_id>/', save_job.save_job, name='save_job'),
    path('remove-saved-job/<int:job_id>/', jobseeker_dashboard.remove_saved_job, name='remove_saved_job'),
    path('saved-jobs/<int:user_id>/', jobseeker_dashboard.saved_jobs_list, name="saved_jobs"),
    path('view_profile/', jobseeker_dashboard.profile_view, name='view_profile'),  
    path('view_profile/<int:user_id>/', jobseeker_dashboard.profile_view, name='view_profile'),
    path('update_profile/', jobseeker_dashboard.update_profile, name='update_profile'),
    path('profile/delete/', jobseeker_dashboard.delete_profile, name='delete_profile'),
    path('profile/upload-resume/', jobseeker_dashboard.upload_resume_for_profile, name='upload_resume_for_profile'),
    path('jobs/<int:job_id>/upload-resume/', jobseeker_dashboard.upload_resume_for_job, name='upload_resume_for_job'),
    path('jobs/<int:job_id>/apply/', job_application.apply_for_job, name='apply'),
    path('jobseeker_register/',JobSeekerRegistration.Jobseeker_Registration_View, name='jobseeker_register'),
    path('interview/<int:interview_id>/', jobseeker_dashboard.view_interview, name='view_interview'),
    path('dashboard-search/', jobseeker_dashboard.dashboard_search_result, name='dashboard_search_result'),
    path('employer_registration/',EmployerRegistration.Employer_Registration_View, name='employer_registration'),
    path('terms/', terms_and_conditions.terms_and_conditions_view, name='terms_and_conditions'),
    path('privacy-policy/', privacy_policy.privacy_policy, name='privacy_policy'),
    path('blog/', blog.blog_list, name='blog_list'),
    path('blog/<int:post_id>/', blog.blog_post, name='blog_post'),

    path('dashboard/chart-data/', employer.get_employer_chart_data, name='employer-chart-data'),
    path('manage-jobs/', employer.manage_jobs, name='manage_jobs'),
    path('job/<int:job_id>/edit/', employer.edit_job, name='edit_job'),
    path('job/<int:job_id>/', employer.job_detail_view, name='job_detail'),
    path('job/<int:job_id>/delete/', employer.delete_job, name='delete_job'),
    path('resume/view/<int:id>/', employer.view_resume, name='view_resume'),
    path('save-resume/<int:id>/', employer.save_resume, name='save_resume'),
    path("saved-resumes/", employer.saved_resumes, name="saved_resumes"),
    path("saved-resumes/delete/<int:id>/", employer.delete_saved_resume, name="delete_saved_resume"),
    path('job-applications/<int:job_id>/', employer.job_applications, name='job_applications'),
    path('application/<int:application_id>/', employer.application_detail, name='application_detail'),
    path('candidate_management/', employer.candidate_management, name='candidate_management'),
    path('shortlist/<int:application_id>/', employer.shortlist_candidate, name='shortlist_candidate'),
    path('schedule_interview/<int:application_id>/', employer.schedule_interview, name='schedule_interview'),
    path('reschedule_interview/<int:interview_id>/', employer.reschedule_interview, name='reschedule_interview'),
    path('interview/cancel/<int:interview_id>/', employer.cancel_interview, name='cancel_interview'),
    path("interview_management/", employer.interview_management, name="interview_management"),
     path('interview/update-status/<int:interview_id>/', employer.update_interview_status, name='update_interview_status'),
    path('applications/update/<int:application_id>/', employer.update_application_status, name='update_application_status'),
    path('performance_analytics/', employer.performance_analytics, name='performance_analytics'),
    path("performance-analytics/print/", employer.print_performance_report, name="print_performance_report"),
    path('applications/update/<int:application_id>/<str:status>/', employer.update_application_status, name='update_application_status'),
    path('search-resumes/', employer.search_resumes, name='search_resumes'),
    path('employer/profile/', employer.view_employer_profile, name='view_employer_profile'),
    path('employer/delete-account/', employer.delete_employer_account, name='delete_employer_profile'),
    path('employer/edit-profile/', employer.edit_employer_profile, name='edit_employer_profile'),
    path("jobs/", employer.job_list, name="job_listing"),
    path("jobs/active/", employer.active_jobs, name="active_jobs"),
    path("jobs/expired/", employer.expired_jobs, name="expired_jobs"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)