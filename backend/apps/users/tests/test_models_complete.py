# apps/users/tests/test_models_complete.py

from django.test import TestCase, TransactionTestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.db import transaction
from ..models import (
    UserProfile, UserActivity, Skill, UserSkill,
    Achievement, UserAchievement, TrainingPreference,
    UserRole
)
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class UserModelFullTest(TestCase):
    """Comprehensive tests for User model."""
    
    def setUp(self):
        self.user_data = {
            'email': 'testuser@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        self.admin_data = {
            'email': 'admin@example.com',
            'password': 'adminpass123',
            'first_name': 'Admin',
            'last_name': 'User',
            'role': UserRole.ADMIN
        }

    def test_user_str_representation(self):
        """Test string representation of User model."""
        user = User.objects.create_user(**self.user_data)
        expected_str = f"{user.get_full_name()} ({user.email})"
        self.assertEqual(str(user), expected_str)

    def test_user_email_normalization(self):
        """Test email is normalized when saving."""
        email = 'TestUser@EXAMPLE.com'
        user = User.objects.create_user(
            email=email,
            password='test123',
            first_name='Test',
            last_name='User'
        )
        self.assertEqual(user.email, email.lower())

    def test_user_required_fields(self):
        """Test user creation with missing required fields."""
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password='test123')

    def test_superuser_creation(self):
        """Test superuser creation and permissions."""
        admin = User.objects.create_superuser(**self.admin_data)
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_staff)
        self.assertEqual(admin.role, UserRole.ADMIN)

    def test_user_related_models_creation(self):
        """Test related models are created with user."""
        user = User.objects.create_user(**self.user_data)
        
        # Test Profile
        self.assertIsInstance(user.profile, UserProfile)
        self.assertEqual(user.profile.user, user)
        
        # Test Training Preferences
        self.assertIsInstance(user.profile.training_preferences, TrainingPreference)
        
        # Test Default Settings
        self.assertIn('theme', user.profile.ui_preferences)
        self.assertIn('notifications_enabled', user.profile.ui_preferences)

class UserProfileFullTest(TestCase):
    """Comprehensive tests for UserProfile model."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.profile = self.user.profile

    def test_profile_defaults(self):
        """Test profile default values."""
        self.assertEqual(self.profile.years_of_experience, 0)
        self.assertIsInstance(self.profile.education, list)
        self.assertIsInstance(self.profile.certifications, list)

    def test_profile_update(self):
        """Test profile update functionality."""
        test_data = {
            'department': 'IT',
            'position': 'Developer',
            'bio': 'Test bio',
            'years_of_experience': 5
        }
        
        for field, value in test_data.items():
            setattr(self.profile, field, value)
        self.profile.save()
        
        updated_profile = UserProfile.objects.get(pk=self.profile.pk)
        for field, value in test_data.items():
            self.assertEqual(getattr(updated_profile, field), value)

class SkillModelTest(TestCase):
    """Tests for Skill model."""

    def setUp(self):
        self.skill_data = {
            'name': 'Python Programming',
            'category': 'Programming',
            'description': 'Python programming language skills',
            'level_criteria': {
                'BEGINNER': 'Basic syntax',
                'INTERMEDIATE': 'Functions and OOP',
                'ADVANCED': 'Advanced concepts',
                'EXPERT': 'Expert level'
            }
        }

    def test_skill_creation(self):
        """Test skill creation with valid data."""
        skill = Skill.objects.create(**self.skill_data)
        self.assertEqual(skill.name, self.skill_data['name'])
        self.assertEqual(skill.category, self.skill_data['category'])

    def test_skill_validation(self):
        """Test skill validation for required levels."""
        invalid_criteria = {'BEGINNER': 'Only beginner level'}
        
        with self.assertRaises(ValidationError):
            Skill.objects.create(
                name='Invalid Skill',
                category='Test',
                level_criteria=invalid_criteria
            )

class UserSkillTest(TransactionTestCase):
    """Tests for UserSkill model."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123'
        )
        
        self.skill = Skill.objects.create(
            name='Python',
            category='Programming',
            level_criteria={
                'BEGINNER': 'Basic syntax',
                'INTERMEDIATE': 'Functions and OOP',
                'ADVANCED': 'Advanced concepts',
                'EXPERT': 'Expert level'
            }
        )
        
        self.trainer = User.objects.create_user(
            email='trainer@example.com',
            password='trainer123',
            role=UserRole.TRAINER
        )

    def test_user_skill_creation(self):
        """Test creating user skill association."""
        with transaction.atomic():
            trainer_skill = UserSkill.objects.create(
                user_profile=self.trainer.profile,
                skill=self.skill,
                proficiency_level='EXPERT',
                verified=True
            )
            
            user_skill = UserSkill.objects.create(
                user_profile=self.user.profile,
                skill=self.skill,
                proficiency_level='INTERMEDIATE'
            )
            
        self.assertEqual(user_skill.proficiency_level, 'INTERMEDIATE')
        self.assertFalse(user_skill.verified)

    def test_skill_verification(self):
        """Test skill verification process."""
        with transaction.atomic():
            # Create trainer's skill first
            trainer_skill = UserSkill.objects.create(
                user_profile=self.trainer.profile,
                skill=self.skill,
                proficiency_level='EXPERT',
                verified=True
            )
            
            # Create user's skill
            user_skill = UserSkill.objects.create(
                user_profile=self.user.profile,
                skill=self.skill,
                proficiency_level='INTERMEDIATE'
            )
            
            # Verify the skill
            user_skill.verified = True
            user_skill.verified_by = self.trainer
            user_skill.save()
            
            self.assertTrue(user_skill.verified)
            self.assertEqual(user_skill.verified_by, self.trainer)

class AchievementSystemTest(TestCase):
    """Tests for Achievement system."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123'
        )
        
        self.achievement = Achievement.objects.create(
            name='First Skill',
            description='Acquire first skill',
            category='Skills',
            points=100,
            criteria={'skill_count': 1},
            badge_image='test.jpg'
        )

    def test_achievement_award(self):
        """Test awarding achievement to user."""
        user_achievement = UserAchievement.objects.create(
            user=self.user,
            achievement=self.achievement,
            evidence={'skill_name': 'Python'}
        )
        
        self.assertEqual(user_achievement.achievement, self.achievement)
        self.assertIsNotNone(user_achievement.earned_at)

class UserActivityTest(TestCase):
    """Tests for UserActivity tracking."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123'
        )

    def test_activity_logging(self):
        """Test activity logging functionality."""
        activity = UserActivity.objects.create(
            user=self.user,
            activity_type='LOGIN',
            activity_detail={'ip': '127.0.0.1'}
        )
        
        self.assertEqual(activity.user, self.user)
        self.assertEqual(activity.activity_type, 'LOGIN')
        self.assertIsNotNone(activity.created_at)

class APIEndpointsTest(APITestCase):
    """Tests for API endpoints."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.client.force_authenticate(user=self.user)

    def test_user_profile_api(self):
        """Test profile API endpoints."""
        url = reverse('current-user-profile')
        
        # Test GET
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test UPDATE
        update_data = {'department': 'Engineering'}
        response = self.client.patch(url, update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['department'], update_data['department'])

def test_user_skills_api(self):
    """Test skills API endpoints."""
    with transaction.atomic():
        # Create test skill first
        skill = Skill.objects.create(
            name='Python',
            category='Programming',
            level_criteria={
                'BEGINNER': 'Basic',
                'INTERMEDIATE': 'Intermediate',
                'ADVANCED': 'Advanced',
                'EXPERT': 'Expert'
            }
        )
        
        # Test adding skill to user
        url = reverse('user-skill-list', kwargs={'user_pk': self.user.pk})
        data = {
            'skill_id': str(skill.id),
            'proficiency_level': 'INTERMEDIATE',
            'user_profile_id': str(self.user.profile.id)  # Added this line
        }
        
        response = self.client.post(url, data, format='json')
        
        # Print response data for debugging if needed
        if response.status_code != status.HTTP_201_CREATED:
            print(f"Response Status: {response.status_code}")
            print(f"Response Data: {response.data}")
            
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify the skill was created
        created_skill = UserSkill.objects.filter(
            user_profile=self.user.profile,
            skill=skill
        ).first()
        self.assertIsNotNone(created_skill)
        self.assertEqual(created_skill.proficiency_level, 'INTERMEDIATE')
    def test_achievements_api(self):
        """Test achievements API endpoints."""
        achievement = Achievement.objects.create(
            name='Test Achievement',
            description='Test description',
            category='Test',
            points=100,
            criteria={'requirement': 'test'},
            badge_image='test.jpg'
        )
        
        # Test achievement list
        url = reverse('achievement-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)