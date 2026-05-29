from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

import os

def user_directory_path(instance, filename):
    folder = settings.MEDIA_ROOT + instance.username 
    if not os.path.exists(folder):
        os.makedirs(folder)
    return folder + '/' + filename

class Role(models.TextChoices):
    TEACHER = 'teacher', 'Teacher'
    STUDENT = 'student', 'Student'
    ADMIN = 'admin', 'Admin'

class Profile(AbstractUser):
    profile_picture = models.ImageField(upload_to=user_directory_path, blank=True, null=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    created_at = models.DateTimeField(auto_now_add=True)
# Create your models here.
