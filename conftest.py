import os
import django

# Ensure this is the correct settings module for your project
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "App.settings")
django.setup()
