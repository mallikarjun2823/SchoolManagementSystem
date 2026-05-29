"""Models for the accounts app.

Defines the custom ``Profile`` user model and helper utilities used for
storing profile pictures and roles.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

import os


def user_directory_path(instance, filename):
    """Return the upload path for a user's profile picture.

    The directory is created under ``MEDIA_ROOT/<username>`` when missing.

    Args:
        instance (Profile): The user profile instance.
        filename (str): Original filename of the uploaded file.

    Returns:
        str: Full path where the file should be stored.
    """

    folder = settings.MEDIA_ROOT + instance.username
    if not os.path.exists(folder):
        os.makedirs(folder)
    return folder + '/' + filename


class Role(models.TextChoices):
    """Enumeration of available user roles.

    Values: ``teacher``, ``student``, ``admin``.
    """

    TEACHER = 'teacher', 'Teacher'
    STUDENT = 'student', 'Student'
    ADMIN = 'admin', 'Admin'


class Profile(AbstractUser):
    """Custom user model extending Django's AbstractUser.

    Adds a profile picture, a role field and a creation timestamp.
    """

    profile_picture = models.ImageField(upload_to=user_directory_path, blank=True, null=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    created_at = models.DateTimeField(auto_now_add=True)
