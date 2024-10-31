# apps/users/tests/test_endpoints.py

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from ..models import UserProfile
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class EndpointTests(APITestCase):
    """Test API endpoints functionality"""

    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        self.user = User.objects.create_user(**self.user_data)
        self.client.force_authenticate(user=self.user)
        logger.info("Test user created and authenticated")

    def test_current_user_endpoint(self):
        """Test current user endpoint"""
        url = reverse('current-user')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user_data['email'])
        logger.info("Current user endpoint test passed")

    def test_current_user_profile_endpoint(self):
        """Test current user profile endpoint"""
        url = reverse('current-user-profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('id' in response.data)
        logger.info("Current user profile endpoint test passed")

    def test_token_obtain(self):
        """Test token obtain endpoint"""
        url = reverse('token_obtain_pair')
        data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)
        logger.info("Token obtain endpoint test passed")

    def tearDown(self):
        self.user.delete()
        logger.info("Test cleanup completed")