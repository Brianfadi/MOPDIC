"""
WSGI config for mopdic project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path

from django.core.wsgi import get_wsgi_application

# Add the project directory to the Python path
project_path = Path(__file__).resolve().parent.parent
if str(project_path) not in sys.path:
    sys.path.append(str(project_path))

# Set the default settings module for the 'wsgi' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mopdic.settings')

# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server, if the WSGI_APPLICATION
# setting points here.
application = get_wsgi_application()

# Apply WSGI middleware here if needed
# from whitenoise import WhiteNoise
# application = WhiteNoise(application, root=os.path.join(project_path, 'staticfiles'))
# application.add_files(os.path.join(project_path, 'media'), prefix='media/')
