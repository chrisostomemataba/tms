# apps/users/tests/test_initial.py

from django.test import TestCase, TransactionTestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class InitialSetupTest(TransactionTestCase):
    """Basic setup tests to ensure core functionality."""

    def test_database_structure(self):
        """Verify database setup and required fields."""
        try:
            # Test user creation with minimal fields
            user = User.objects.create_user(
                email='test@example.com',
                password='testpass123',
                first_name='Test',
                last_name='User'
            )
            
            # Verify required fields
            self.assertIsNotNone(user.id)
            self.assertEqual(user.email, 'test@example.com')
            self.assertTrue(user.check_password('testpass123'))
            self.assertEqual(user.role, 'PARTICIPANT')  # Default role
            self.assertTrue(user.is_active)
            
            # Verify auto-created fields
            self.assertIsNotNone(user.created_at)
            self.assertIsNotNone(user.updated_at)
            
            # Verify profile creation
            self.assertTrue(hasattr(user, 'profile'))
            self.assertIsNotNone(user.profile)
            
            # Verify training preferences
            self.assertTrue(hasattr(user.profile, 'training_preferences'))
            self.assertIsNotNone(user.profile.training_preferences)
            
            logger.info("Basic user creation test passed")
            
        except Exception as e:
            logger.error(f"Test failed: {str(e)}")
            raise

class UserModelTest(TestCase):
    """Test User model functionality."""
    
    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }

    def test_user_creation(self):
        """Test basic user creation and defaults."""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.first_name, self.user_data['first_name'])
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertEqual(user.role, 'PARTICIPANT')

    def test_user_profile_creation(self):
        """Test profile is automatically created."""
        user = User.objects.create_user(**self.user_data)
        self.assertIsNotNone(user.profile)
        self.assertEqual(user.profile.user, user)
        
        # Test default preferences
        self.assertIsNotNone(user.profile.ui_preferences)
        self.assertIsNotNone(user.profile.notification_settings)

    def test_user_training_preferences(self):
        """Test training preferences are automatically created."""
        user = User.objects.create_user(**self.user_data)
        prefs = user.profile.training_preferences
        self.assertIsNotNone(prefs)
        self.assertEqual(prefs.preferred_learning_style, 'VISUAL')
        self.assertTrue(isinstance(prefs.preferred_training_days, list))

class UserAPITest(APITestCase):
    """Test User API endpoints."""

    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        self.user = User.objects.create_user(**self.user_data)
        self.client.force_authenticate(user=self.user)


    def test_profile_endpoint(self):
        """Test profile retrieval and update."""
        url = reverse('current-user-profile')
        
        # Test GET
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test UPDATE
        update_data = {
            'department': 'IT',
            'position': 'Developer'
        }
        response = self.client.patch(url, update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['department'], update_data['department'])

def run_setup_test():
    """Run initial setup test."""
    try:
        # Create test database
        User.objects.create_superuser(
            email='admin@example.com',
            password='admin123',
            first_name='Admin',
            last_name='User'
        )
        logger.info("Initial setup test passed")
        return True
    except Exception as e:
        logger.error(f"Initial setup test failed: {str(e)}")
        return False

if __name__ == '__main__':
    run_setup_test()