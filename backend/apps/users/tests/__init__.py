# apps/users/tests/__init__.py

from django.test import TestCase, TransactionTestCase
from django.db import connection
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from ..models import UserRole
import logging
import psycopg2

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

User = get_user_model()

class DatabaseSetupTest(TransactionTestCase):
    """Verify database setup and configuration."""
    
    def test_database_connection(self):
        """Test database connection and configuration."""
        try:
            with connection.cursor() as cursor:
                # Test connection
                cursor.execute("SELECT 1")
                self.assertTrue(cursor.fetchone()[0] == 1)
                logger.info("✓ Database connection successful")

                # Check migrations table
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'django_migrations'
                    );
                """)
                self.assertTrue(cursor.fetchone()[0])
                logger.info("✓ Migrations table exists")

                # Check users table
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'users_user'
                    );
                """)
                self.assertTrue(cursor.fetchone()[0])
                logger.info("✓ Users table exists")

        except Exception as e:
            logger.error(f"Database test failed: {e}")
            raise

class UserModelTest(TestCase):
    """Test User model functionality."""

    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'role': UserRole.PARTICIPANT
        }

    def test_create_user(self):
        """Test basic user creation."""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.role, UserRole.PARTICIPANT)
        logger.info("✓ User creation successful")

        # Verify profile creation
        self.assertTrue(hasattr(user, 'profile'))
        logger.info("✓ Profile auto-creation successful")

class UserAPITest(APITestCase):
    """Test API endpoints."""

    def setUp(self):
        self.admin_data = {
            'email': 'admin@test.com',
            'password': 'adminpass123',
            'first_name': 'Admin',
            'last_name': 'User',
            'role': UserRole.ADMIN
        }
        self.admin = User.objects.create_superuser(**self.admin_data)

    def test_user_registration(self):
        """Test user registration endpoint."""
        url = reverse('register')  # Make sure this matches your URL name
        data = {
            'email': 'newuser@test.com',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        logger.info("✓ User registration successful")

    def test_user_authentication(self):
        """Test user authentication."""
        url = reverse('token_obtain_pair')  # Make sure this matches your URL name
        data = {
            'email': self.admin_data['email'],
            'password': self.admin_data['password']
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        logger.info("✓ User authentication successful")

def run_tests():
    """Run all tests."""
    logger.info("Starting tests...")
    import django
    django.setup()
    
    from django.test.runner import DiscoverRunner
    test_runner = DiscoverRunner(verbosity=2)
    failures = test_runner.run_tests(['users.tests'])
    if failures:
        logger.error("Tests failed!")
    else:
        logger.info("All tests passed!")

if __name__ == '__main__':
    run_tests()