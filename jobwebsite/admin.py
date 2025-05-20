from django.contrib import admin
from .models import Job, Category, Application, JobseekerProfile, Skill, Company,CustomUser, Interview, Education, Experience,BlogPost

# Register your models here.
admin.site.register(Job)
admin.site.register(Category)
admin.site.register(Application)
admin.site.register(JobseekerProfile)
admin.site.register(Skill)
admin.site.register(Company)
admin.site.register(CustomUser)
admin.site.register(Interview)
admin.site.register(Education)
admin.site.register(Experience)
admin.site.register(BlogPost)