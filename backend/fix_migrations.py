import os
import django
from django.db import connection
from django.core.management import call_command

def fix_migrations_state():
    """Fix migration state by faking migrations"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()
    
    try:
        # 1. First, mark all existing migrations as applied
        print("Faking initial migrations...")
        apps_to_fake = [
            'admin',
            'auth',
            'contenttypes',
            'sessions',
            'users',
            'courses'
        ]
        
        for app in apps_to_fake:
            call_command('migrate', app, 'zero', '--fake')
            print(f"Reset migrations for {app}")
        
        # 2. Now fake apply all migrations
        for app in apps_to_fake:
            call_command('migrate', app, '--fake')
            print(f"Faked migrations for {app}")
            
        print("\nMigration state has been fixed!")
        
        # 3. Verify the state
        print("\nVerifying migration state:")
        call_command('showmigrations')
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    fix_migrations_state()