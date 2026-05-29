"""ASGI application for the Django project.

This module exposes the ASGI callable as a module-level variable
named ``application`` which ASGI servers use to communicate with
the Django application.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SchoolManagementSystem.settings')

application = get_asgi_application()
