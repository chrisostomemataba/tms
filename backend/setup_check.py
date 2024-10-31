import os
import sys
from pathlib import Path

def check_structure():
    current_dir = Path.cwd()
    
    # Required directories
    required_dirs = [
        'apps',
        'apps/courses',
        'apps/users',
        'apps/calendar_app',
        'config',
        'config/settings',
        'core',
        'static',
        'media',
        'templates'
    ]
    
    # Required files
    required_files = [
        'apps/__init__.py',
        'apps/courses/__init__.py',
        'apps/courses/apps.py',
        'apps/courses/models.py',
        'apps/users/__init__.py',
        'apps/users/apps.py',
        'apps/users/models.py',
        'apps/calendar_app/__init__.py',
        'apps/calendar_app/apps.py',
        'apps/calendar_app/models.py',
        'config/__init__.py',
        'config/settings/__init__.py',
        'config/settings/base.py',
        'config/settings/development.py',
        'config/settings/production.py',
        'config/urls.py',
        'config/wsgi.py',
        'core/__init__.py',
        'manage.py',
        '.env'
    ]
    
    # Check and create directories
    for dir_path in required_dirs:
        full_path = current_dir / dir_path
        if not full_path.exists():
            full_path.mkdir(parents=True)
            print(f"Created directory: {dir_path}")
    
    # Check and create files
    for file_path in required_files:
        full_path = current_dir / file_path
        if not full_path.exists():
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.touch()
            print(f"Created file: {file_path}")

    # Update apps.py files
    apps_config = {
        'courses': '''from django.apps import AppConfig

class CoursesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.courses'
    verbose_name = 'Courses'
''',
        'users': '''from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    verbose_name = 'Users'
''',
        'calendar_app': '''from django.apps import AppConfig

class CalendarAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.calendar_app'
    verbose_name = 'Calendar'
'''
    }
    
    for app, content in apps_config.items():
        app_config_path = current_dir / f'apps/{app}/apps.py'
        with open(app_config_path, 'w') as f:
            f.write(content)
        print(f"Updated {app}/apps.py")

if __name__ == "__main__":
    check_structure()