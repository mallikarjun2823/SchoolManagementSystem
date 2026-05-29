"""WSGI application for the Django project.

This module exposes the WSGI callable as a module-level variable
named ``application`` which the WSGI server can use to forward
requests to Django.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SchoolManagementSystem.settings')

application = get_wsgi_application()
