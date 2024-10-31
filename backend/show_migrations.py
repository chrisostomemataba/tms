from django.core.management import execute_from_command_line
import os
import django

def show_migrations_status():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()
    
    # Show migrations status
    print("\nCurrent Migration Status:")
    execute_from_command_line(['manage.py', 'showmigrations'])

if __name__ == "__main__":
    show_migrations_status()