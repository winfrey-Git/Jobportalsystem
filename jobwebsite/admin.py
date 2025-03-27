from django.contrib import admin
from .models import Job, Category, Application, JobseekerProfile, Skill, Company

# Register your models here.
admin.site.register(Job)
admin.site.register(Category)
admin.site.register(Application)
admin.site.register(JobseekerProfile)
admin.site.register(Skill)
admin.site.register(Company)