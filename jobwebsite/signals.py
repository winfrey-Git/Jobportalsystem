from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, JobseekerProfile

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created and instance.role == 'employee':  # Only create for jobseekers
        JobseekerProfile.objects.create(user=instance)
