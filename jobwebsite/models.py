from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import AbstractUser, Group, Permission
from taggit.managers import TaggableManager
from django.conf import settings
from jobwebsite.managers import CustomUserManager
from ckeditor.fields import RichTextField


JOB_TYPE = [("full time", "Full time"), ("part time", "Part time"), ("internship", "Internship")]
GENDER_TYPE = [("M", "Male"), ("F", "Female")]
ROLE_CHOICES = [("employer", "Employer"), ("employee", "Employee")]
STATUS_CHOICES = [("open", "Open"), ("closed", "Closed")]
APPLICATION_STATUS = [("pending", "Pending"), ("shortlisted", "Shortlisted"), ("rejected", "Rejected"), ("hired", "Hired")]

class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True, blank=False, error_messages={'unique': "A user with that email already exists."})

    ROLE_CHOICES = [
        ('employer', 'Employer'),
        ('employee', 'Employee'),
    ]
    
    role = models.CharField(choices=ROLE_CHOICES, max_length=10)
    gender = models.CharField(choices=GENDER_TYPE, max_length=1, blank=True, null=True, default="M")

    groups = models.ManyToManyField(Group, related_name='custom_user_set', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_permissions_set', blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    objects = CustomUserManager()

    @property
    def is_employer(self):
        return self.role == "employer"




class Skill(models.Model):
    name = models.CharField(max_length=100,  unique=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=225)

    def __str__(self):
        return self.name

class Company(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='company')
    company_name = models.CharField(max_length=225)
    company_address = models.TextField(null=True)  # New field for company address
    industry = models.CharField(max_length=150)  # Field for industry
    company_description = RichTextField() 
    company_logo = models.ImageField(upload_to="company_logos/", blank=True, null=True)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    website = models.URLField(blank=True, null=True)  # Optional website field

    def __str__(self):
        return self.company_name


class Job(models.Model):
    company = models.ForeignKey("Company", on_delete=models.CASCADE, related_name="jobs",null=True)
    title = models.CharField(max_length=225)
    description = models.TextField()
    location = models.CharField(max_length=225)
    type = models.CharField(choices=JOB_TYPE, max_length=10)
    category = models.ForeignKey("Category", related_name="jobs", on_delete=models.CASCADE)
    salary = models.CharField(max_length=100, blank=True, null=True)  # Allows null values
    posted_date = models.DateTimeField(auto_now_add=True)
    deadline_date = models.DateTimeField()
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    vacancy = models.IntegerField(default=1)
    tags = TaggableManager()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='open')
    responsibilities = models.TextField(blank=True, null=True)
    requirements = models.TextField(blank=True, null=True)

    def __str__(self):
        if self.company and hasattr(self.company, "company_name"):
            return f"{self.title} at {self.company.company_name}"
        return f"{self.title} (No Company)"

    def get_absolute_url(self):
        return reverse("job_detail", args=[str(self.id)])


from django.db import models
from django.conf import settings

class JobseekerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'employee'}  # Restrict to jobseekers
    )
    skills = models.ManyToManyField(Skill, blank=True, related_name='user_profiles')
    saved_jobs = models.ManyToManyField(Job, related_name='saved_by_users', blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', default='default-profile.png', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    education = models.TextField(blank=True, null=True)
    preferred_category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    resume = models.FileField(upload_to='profile/resumes/', blank=True, null=True)  
    experience = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.user.email} - Jobseeker"




class ResumeUpload(models.Model):
    applicant = models.ForeignKey(JobseekerProfile, on_delete=models.CASCADE, related_name="uploaded_resumes")
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="resumes")
    resume = models.FileField(upload_to='resumes/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    parsed_text = models.TextField(blank=True, null=True)  

    def __str__(self):
        return f"{self.applicant.user.get_full_name()} - {self.job.title} Resume"

class Application(models.Model):
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="application")
    resume = models.ForeignKey(ResumeUpload, on_delete=models.CASCADE, null=True, blank=True)  
    cover_letter = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('shortlisted', 'Shortlisted'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('hired', 'Hired'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Application for {self.job.title} by {self.applicant.email}"




class Interview(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="interviews")
    date = models.DateField()  # Changed to store only the date
    time = models.TimeField(default="10:00:00")  # Added field for interview time
    mode = models.CharField(
        max_length=20, 
        choices=[('In-Person', 'In-Person'), ('Online', 'Online')], 
        default='In-Person'
    )  # Added field for interview mode
    interview_link = models.URLField(null=True, blank=True)  # Optional field for online meetings
    status = models.CharField(
        max_length=20, 
        choices=[('scheduled', 'Scheduled'), ('completed', 'Completed'), ('canceled', 'Canceled')], 
        default='scheduled'
    )

    def __str__(self):
        return f"Interview for {self.application.applicant.get_full_name()} on {self.date} at {self.time}"




class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('new_application', 'New Application'),
        ('interview_response', 'Interview Response'),
        ('system_update', 'System Update'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='system_update')
    is_read = models.BooleanField(default=False)
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Notification for {self.user.email} - {self.notification_type}"

    class Meta:
        ordering = ['-date_created'] 

class SavedResume(models.Model):
    employer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="saved_resumes")
    applicant = models.ForeignKey(JobseekerProfile, on_delete=models.CASCADE, related_name="saved_resumes")
    resume = models.FileField(upload_to='saved_resumes/')
    saved_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Resume of {self.applicant.user.email} saved by {self.employer.email}"


class JobApplicationTest(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="test_attempts")
    attempt_number = models.IntegerField(default=1)
    score = models.FloatField(default=0.0)
    passed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(auto_now_add=True)
    time_taken = models.IntegerField(default=0)  

    def __str__(self):
        return f"Test for {self.application.applicant.user.email} - Score: {self.score}"


class JobTest(models.Model):
    job = models.OneToOneField(Job, on_delete=models.CASCADE, related_name="test")
    total_questions = models.IntegerField()
    passing_score = models.IntegerField(default=85)

    def __str__(self):
        return f"Test for {self.job.title} (Passing Score: {self.passing_score})"
    
class BookmarkJob(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE, related_name='saved_job')
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True, auto_now_add=False)


    def __str__(self):
        return self.job.title