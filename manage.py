#!/usr/bin/env python
"""Django command-line utility entrypoint.

This module exposes a :func:`main` helper that bootstraps Django and
dispatches management commands. It is the standard entrypoint used by
``django-admin`` and by running this file as a script.
"""
import os
import sys


def main():
    """Run administrative tasks.

    This function sets the default Django settings module and invokes the
    Django management command runner with the arguments provided on the
    command line.
    """
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SchoolManagementSystem.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
