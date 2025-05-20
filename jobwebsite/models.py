from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import AbstractUser, Group, Permission
from taggit.managers import TaggableManager
from django.conf import settings
from jobwebsite.managers import CustomUserManager
from ckeditor.fields import RichTextField
import fitz  
import docx
import os


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
    is_deleted = models.BooleanField(default=False)
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
    company = models.ForeignKey("Company", on_delete=models.CASCADE, related_name="jobs", null=True)
    title = models.CharField(max_length=225)
    description = models.TextField()
    location = models.CharField(max_length=225)
    type = models.CharField(choices=JOB_TYPE, max_length=10)
    category = models.ForeignKey("Category", related_name="jobs", on_delete=models.CASCADE)
    salary = models.CharField(max_length=100, blank=True, null=True)  # Allows null values
    posted_date = models.DateTimeField(auto_now_add=True)
    deadline_date = models.DateTimeField()
    is_published = models.BooleanField(default=False)  # If the job is visible or not
    is_featured = models.BooleanField(default=False)
    vacancy = models.IntegerField(default=1)
    tags = TaggableManager()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='open')  # 'draft' or 'open'
    responsibilities = models.TextField(blank=True, null=True)
    requirements = models.TextField(blank=True, null=True)
    saved = models.BooleanField(default=False)  # True if the job is saved as a draft

    def __str__(self):
        if self.company and hasattr(self.company, "company_name"):
            return f"{self.title} at {self.company.company_name}"
        return f"{self.title} (No Company)"

    def get_absolute_url(self):
        return reverse("job_detail", args=[str(self.id)])

    def save_job_as_draft(self):
        """Mark the job as saved but not posted."""
        self.saved = True
        self.status = 'draft'  # Set the status as draft
        self.is_published = False  # Job is not published
        self.save()

    def publish_job(self):
        """Publish the job, making it visible to the public."""
        self.saved = False
        self.status = 'open'  # Set the status to open (active job)
        self.is_published = True  # Job is now published
        self.save()



class JobseekerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'employee'} ,
        related_name="jobseeker_profile" 
    )
    skills = models.ManyToManyField(Skill, blank=True, related_name='user_profiles')
    profile_picture = models.ImageField(upload_to='profile_pics/', default='default-profile.png', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    preferred_category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    resume = models.FileField(upload_to='profile/resumes/', blank=True, null=True)  
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    job_alert = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.user.email} - Jobseeker"
    
class Experience(models.Model):
    jobseeker = models.ForeignKey(JobseekerProfile, on_delete=models.CASCADE, related_name="experience_entries")
    job_title = models.CharField(max_length=255)
    company_in = models.CharField(max_length=255)
    company_location = models.CharField(max_length=255, blank=True, null=True)  # Updated field name
    years = models.IntegerField()

    def __str__(self):
        return f"{self.job_title} at {self.company_in}, {self.company_location} ({self.years} years)"
    
class Education(models.Model):
    jobseeker = models.ForeignKey(JobseekerProfile, on_delete=models.CASCADE, related_name="education_entries")
    degree = models.CharField(max_length=255)
    institution = models.CharField(max_length=255)
    year = models.IntegerField()

    def __str__(self):
        return f"{self.degree} - {self.institution} ({self.year})"




class ResumeUpload(models.Model):
    applicant = models.ForeignKey(JobseekerProfile, on_delete=models.CASCADE, related_name="uploaded_resumes")
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="resumes")
    resume = models.FileField(upload_to='resumes/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    parsed_text = models.TextField(blank=True, null=True)  # Stores extracted text

    def extract_text_from_pdf(self, pdf_path):
        """Extract text from a PDF file."""
        extracted_text = ""
        try:
            with fitz.open(pdf_path) as doc:
                extracted_text = "\n".join(page.get_text("text") for page in doc)
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
        return extracted_text

    def extract_text_from_docx(self, docx_path):
        """Extract text from a DOCX file."""
        extracted_text = ""
        try:
            doc = docx.Document(docx_path)
            extracted_text = "\n".join(para.text for para in doc.paragraphs)
        except Exception as e:
            print(f"Error extracting text from DOCX: {e}")
        return extracted_text

    def save(self, *args, **kwargs):
        """Save resume and extract text if it's a PDF or DOCX."""
        super().save(*args, **kwargs)  # Save the file first

        # Extract text after saving the file
        resume_path = self.resume.path
        extracted_text = ""

        if self.resume and os.path.exists(resume_path):
            file_extension = self.resume.name.lower().split(".")[-1]

            if file_extension == "pdf":
                extracted_text = self.extract_text_from_pdf(resume_path)
            elif file_extension in ["docx", "doc"]:  # Handle both DOCX and legacy DOC
                extracted_text = self.extract_text_from_docx(resume_path)

        # Store extracted text in `parsed_text` field
        if extracted_text:
            self.parsed_text = extracted_text
            super().save(update_fields=["parsed_text"])  # Save only the extracted text

    def __str__(self):
        return f"{self.applicant.user.get_full_name()} - {self.job.title} Resume"

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    published_date = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)

    def __str__(self):
        return self.title

class Application(models.Model):
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="application")
    resume = models.ForeignKey(ResumeUpload, on_delete=models.CASCADE, null=True, blank=True)  
    cover_letter = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    job_alert = models.BooleanField(default=False)

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('shortlisted', 'Shortlisted'),
        ('hired', 'Hired'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Application for {self.job.title} by {self.applicant.email}"
    
    def is_interview_scheduled(self):
        """Check if an interview is scheduled for this application."""
        return self.interviews.filter(status='scheduled').exists()

class Interview(models.Model):
    application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name="interview")
    date = models.DateField()
    time = models.TimeField(default="10:00:00")
    mode = models.CharField(
        max_length=20, 
        choices=[('In-Person', 'In-Person'), ('Online', 'Online')], 
        default='In-Person'
    )
    interview_link = models.URLField(null=True, blank=True)
    status = models.CharField(
        max_length=20, 
        choices=[('scheduled', 'Scheduled'), ('completed', 'Completed'), ('canceled', 'Canceled')], 
        default='scheduled'
    )

    def __str__(self):
        return f"Interview for {self.application.applicant.get_full_name()} on {self.date} at {self.time}"




class SavedResume(models.Model):
    employer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="saved_resumes")
    resume = models.ForeignKey(ResumeUpload, on_delete=models.CASCADE, related_name="saved_by_employers")
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('employer', 'resume')  # Prevent duplicate saves

    def __str__(self):
        return f"Resume of {self.resume.applicant.user.email} saved by {self.employer.email}"


    
class BookmarkJob(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE, related_name='saved_job')
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True, auto_now_add=False)


    def __str__(self):
        return self.job.title