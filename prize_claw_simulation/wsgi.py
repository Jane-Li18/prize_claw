"""
WSGI config for prize_claw_simulation project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prize_claw_simulation.settings')

# Define the WSGI application callable
application = get_wsgi_application()

# If you want to use 'app' locally, you can create a reference
# but keep 'application' as the main callable for Vercel
app = application
