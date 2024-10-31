# apps/users/models.py

# Existing imports remain the same
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from phonenumber_field.modelfields import PhoneNumberField
from simple_history.models import HistoricalRecords
import uuid
from datetime import timedelta
from django.utils import timezone
import jwt
from django.conf import settings
import logging

# NEW: Add logger
logger = logging.getLogger(__name__)

class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication."""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        try:
            with transaction.atomic():  # NEW: Add transaction
                email = self.normalize_email(email)
                extra_fields.setdefault('is_active', True)
                extra_fields.setdefault('last_active', timezone.now())  # NEW: Initialize last_active
                
                user = self.model(email=email, **extra_fields)
                if password:
                    user.set_password(password)
                user.save(using=self._db)
                return user
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', UserRole.ADMIN)
        return self.create_user(email, password, **extra_fields)

# UserRole remains the same
class UserRole(models.TextChoices):
    """User role choices."""
    ADMIN = 'ADMIN', _('Admin')
    TRAINER = 'TRAINER', _('Trainer')
    PARTICIPANT = 'PARTICIPANT', _('Participant')

class User(AbstractUser):
    """Enhanced user model with additional fields and functionality."""
    
    username = None  # Disable username field
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        help_text="Unique identifier for the user"  # NEW: Add help text
    )
    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.PARTICIPANT
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # MODIFIED: Added default and help_text to fields
    last_active = models.DateTimeField(
        null=True, 
        blank=True,
        default=timezone.now,
        help_text="Last time user was active"
    )
    deactivated_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="When user was deactivated"
    )
    deactivation_reason = models.TextField(
        blank=True,
        help_text="Reason for deactivation"
    )
    
    # Tracking fields
    failed_login_attempts = models.PositiveIntegerField(
        default=0,
        help_text="Number of failed login attempts"
    )
    last_failed_login = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Time of last failed login attempt"
    )
    password_changed_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="When password was last changed"
    )
    
    history = HistoricalRecords()
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    def save(self, *args, **kwargs):
        """MODIFIED: Enhanced save method with better error handling"""
        try:
            with transaction.atomic():
                self.email = self.email.lower()
                creating = not self.pk  # Check if new instance
                
                if creating:
                    # Set initial values for new users
                    if not self.last_active:
                        self.last_active = timezone.now()
                
                # Save user first
                super().save(*args, **kwargs)
                
                # Create related models for new users
                if creating:
                    profile = UserProfile.objects.create(
                        user=self,
                        ui_preferences={'theme': 'light', 'language': 'en'},
                        notification_settings={'email': True, 'in_app': True}
                    )
                    
                    TrainingPreference.objects.create(
                        user_profile=profile,
                        preferred_learning_style='VISUAL',
                        preferred_training_days=[],
                        preferred_time_slots=[],
                        notification_preferences={
                            'email': True,
                            'in_app': True,
                            'reminders': True
                        }
                    )
                    
                    # Log user creation
                    UserActivity.objects.create(
                        user=self,
                        activity_type='USER_CREATION',
                        activity_detail={
                            'role': self.role,
                            'email': self.email
                        }
                    )
        except Exception as e:
            logger.error(f"Error saving user {self.email}: {str(e)}")
            raise

    def record_login_attempt(self, success, ip_address=None):
        """Record login attempt and handle security measures."""
        try:
            with transaction.atomic():  # NEW: Add transaction
                if success:
                    self.failed_login_attempts = 0
                    self.last_active = timezone.now()
                    activity_type = 'LOGIN'
                    detail = {'success': True}
                else:
                    self.failed_login_attempts += 1
                    self.last_failed_login = timezone.now()
                    if self.failed_login_attempts >= settings.MAX_FAILED_LOGINS:
                        self.is_active = False
                        self.deactivated_at = timezone.now()
                        self.deactivation_reason = 'Multiple failed login attempts'
                    activity_type = 'LOGIN_FAILED'
                    detail = {
                        'success': False,
                        'attempt': self.failed_login_attempts
                    }
                
                self.save()
                
                # Create activity record
                UserActivity.objects.create(
                    user=self,
                    activity_type=activity_type,
                    ip_address=ip_address,
                    activity_detail=detail
                )
        except Exception as e:
            logger.error(f"Error recording login attempt for {self.email}: {str(e)}")
            raise

    def generate_tokens(self):
        """Generate access and refresh tokens."""
        try:
            access_token_payload = {
                'user_id': str(self.id),
                'exp': timezone.now() + timedelta(minutes=60),
                'iat': timezone.now(),
                'type': 'access'
            }
            refresh_token_payload = {
                'user_id': str(self.id),
                'exp': timezone.now() + timedelta(days=7),
                'iat': timezone.now(),
                'type': 'refresh'
            }
            
            access_token = jwt.encode(
                access_token_payload,
                settings.SECRET_KEY,
                algorithm='HS256'
            )
            refresh_token = jwt.encode(
                refresh_token_payload,
                settings.SECRET_KEY,
                algorithm='HS256'
            )
            
            return {
                'access': access_token,
                'refresh': refresh_token
            }
        except Exception as e:
            logger.error(f"Error generating tokens for {self.email}: {str(e)}")
            raise
# Continue in models.py after User class

class Skill(models.Model):
    """Skill model for tracking user competencies."""
    
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    name = models.CharField(
        max_length=100, 
        unique=True,
        help_text="Name of the skill"
    )
    category = models.CharField(
        max_length=50,
        help_text="Category of the skill"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed description of the skill"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Skill metadata with improved validation
    prerequisites = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='dependent_skills',
        help_text="Skills that must be completed before this one"
    )
    level_criteria = models.JSONField(
        default=dict,
        help_text="Criteria for each proficiency level"
    )

    class Meta:
        ordering = ['category', 'name']
        indexes = [
            models.Index(fields=['category', 'name']),  # NEW: Add index
        ]

    def __str__(self):
        return f"{self.name} ({self.category})"

    def clean(self):
        """NEW: Added validation method"""
        super().clean()
        if self.level_criteria:
            required_levels = {'BEGINNER', 'INTERMEDIATE', 'ADVANCED', 'EXPERT'}
            if not all(level in self.level_criteria for level in required_levels):
                raise ValidationError(
                    f"Level criteria must contain all proficiency levels: {required_levels}"
                )

    def save(self, *args, **kwargs):
        """NEW: Enhanced save method with validation"""
        self.clean()
        super().save(*args, **kwargs)

class UserProfile(models.Model):
    """Extended user profile information."""
    
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    phone_number = PhoneNumberField(
        blank=True, 
        null=True,
        help_text="Contact phone number"
    )
    department = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Department or division"
    )
    position = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Job position or title"
    )
    bio = models.TextField(
        blank=True,
        help_text="User biography or description"
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        help_text="Profile picture"
    )
    
    # Professional Info
    years_of_experience = models.PositiveIntegerField(
        default=0,
        help_text="Years of professional experience"
    )
    education = models.JSONField(
        default=list,
        help_text="List of educational qualifications"
    )
    certifications = models.JSONField(
        default=list,
        help_text="List of professional certifications"
    )
    
    # Social Links
    linkedin_profile = models.URLField(
        blank=True,
        help_text="LinkedIn profile URL"
    )
    github_profile = models.URLField(
        blank=True,
        help_text="GitHub profile URL"
    )
    portfolio_website = models.URLField(
        blank=True,
        help_text="Personal portfolio website"
    )
    
    # System Preferences with improved defaults
    ui_preferences = models.JSONField(
        default=dict,
        help_text="User interface preferences"
    )
    notification_settings = models.JSONField(
        default=dict,
        help_text="Notification preferences"
    )
    
    history = HistoricalRecords()

    class Meta:
        indexes = [
            models.Index(fields=['user']),  # NEW: Add index
        ]

    def __str__(self):
        return f"Profile for {self.user.email}"

    def save(self, *args, **kwargs):
        """NEW: Enhanced save method with defaults"""
        if not self.ui_preferences:
            self.ui_preferences = {
                'theme': 'light',
                'language': 'en',
                'notifications_enabled': True
            }
        if not self.notification_settings:
            self.notification_settings = {
                'email': True,
                'in_app': True,
                'push': False
            }
        super().save(*args, **kwargs)

    def get_skills_summary(self):
        """Get summary of user's skills and proficiency levels."""
        try:
            return self.skills.all().select_related('skill').values(
                'skill__name',
                'skill__category',
                'proficiency_level',
                'verified'
            )
        except Exception as e:
            logger.error(f"Error getting skills summary for {self.user.email}: {str(e)}")
            return []

class UserSkill(models.Model):
    """User's proficiency in specific skills."""
    
    PROFICIENCY_LEVELS = [
        ('BEGINNER', 'Beginner'),
        ('INTERMEDIATE', 'Intermediate'),
        ('ADVANCED', 'Advanced'),
        ('EXPERT', 'Expert')
    ]
    
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    user_profile = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='skills'
    )
    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name='user_skills'
    )
    proficiency_level = models.CharField(
        max_length=20,
        choices=PROFICIENCY_LEVELS,
        help_text="User's proficiency level in this skill"
    )
    verified = models.BooleanField(
        default=False,
        help_text="Whether this skill has been verified"
    )
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_skills',
        help_text="User who verified this skill"
    )
    verification_date = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="When this skill was verified"
    )
    evidence = models.JSONField(
        default=list,
        help_text="Evidence supporting skill level"
    )
    
    class Meta:
        unique_together = ['user_profile', 'skill']
        ordering = ['skill__category', 'skill__name']
        indexes = [
            models.Index(fields=['user_profile', 'skill']),
            models.Index(fields=['verified']),
        ]

    def verify(self, verifier):
        """Verify a user's skill."""
        try:
            with transaction.atomic():
                if not verifier.role in [UserRole.ADMIN, UserRole.TRAINER]:
                    raise ValidationError("Only admins and trainers can verify skills")
                
                # For trainers, verify they have the skill
                if verifier.role == UserRole.TRAINER:
                    verifier_skill = UserSkill.objects.filter(
                        user_profile=verifier.profile,
                        skill=self.skill,
                        verified=True
                    ).exists()
                    if not verifier_skill:
                        raise ValidationError(
                            "Trainer must have this skill verified to verify others"
                        )
                
                self.verified = True
                self.verified_by = verifier
                self.verification_date = timezone.now()
                self.save()
                
                # Create activity record
                UserActivity.objects.create(
                    user=self.user_profile.user,
                    activity_type='SKILL_VERIFICATION',
                    activity_detail={
                        'skill': self.skill.name,
                        'level': self.proficiency_level,
                        'verifier': verifier.email
                    }
                )
        except Exception as e:
            logger.error(f"Error verifying skill: {str(e)}")
            raise
# Continue in models.py after UserSkill class

class TrainingPreference(models.Model):
    """User's training preferences and learning style."""
    
    LEARNING_STYLES = [
        ('VISUAL', 'Visual'),
        ('AUDITORY', 'Auditory'),
        ('KINESTHETIC', 'Kinesthetic'),
        ('READING', 'Reading/Writing')
    ]
    
    GROUP_SIZES = [
        ('INDIVIDUAL', 'Individual'),
        ('SMALL', 'Small Group (2-5)'),
        ('MEDIUM', 'Medium Group (6-15)'),
        ('LARGE', 'Large Group (15+)')
    ]
    
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    user_profile = models.OneToOneField(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='training_preferences'
    )
    preferred_learning_style = models.CharField(
        max_length=20,
        choices=LEARNING_STYLES,
        default='VISUAL',  # NEW: Added default
        help_text="Preferred style of learning"
    )
    preferred_training_days = models.JSONField(
        default=list,
        help_text="List of preferred days for training"
    )
    preferred_time_slots = models.JSONField(
        default=list,
        help_text="List of preferred time slots"
    )
    preferred_group_size = models.CharField(
        max_length=20,
        choices=GROUP_SIZES,
        default='SMALL',
        help_text="Preferred training group size"
    )
    language_preferences = models.JSONField(
        default=list,
        help_text="Preferred languages for training"
    )
    notification_preferences = models.JSONField(
        default=dict,
        help_text="Notification settings for different events"
    )
    accessibility_requirements = models.JSONField(
        default=dict,
        help_text="Specific accessibility needs"
    )

    def save(self, *args, **kwargs):
        """NEW: Enhanced save method with validation and defaults"""
        if not self.notification_preferences:
            self.notification_preferences = {
                'email_reminders': True,
                'session_notifications': True,
                'progress_updates': True
            }
        if not self.preferred_training_days:
            self.preferred_training_days = ['MONDAY', 'WEDNESDAY', 'FRIDAY']
        
        # Validate days
        valid_days = {'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY'}
        if not all(day in valid_days for day in self.preferred_training_days):
            raise ValidationError(f"Invalid training day. Must be one of: {valid_days}")
        
        super().save(*args, **kwargs)

class Achievement(models.Model):
    """Achievements and badges that users can earn."""
    
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    name = models.CharField(
        max_length=100,
        help_text="Name of the achievement"
    )
    description = models.TextField(
        help_text="Detailed description of the achievement"
    )
    category = models.CharField(
        max_length=50,
        help_text="Category of the achievement"
    )
    badge_image = models.ImageField(
        upload_to='achievements/',
        help_text="Badge image for the achievement"
    )
    points = models.IntegerField(
        default=0,
        help_text="Points awarded for this achievement"
    )
    criteria = models.JSONField(
        help_text="Criteria for earning achievement"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this achievement can be earned"
    )
    
    class Meta:
        ordering = ['category', 'points']
        indexes = [
            models.Index(fields=['category', 'points']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.points} points)"

    def clean(self):
        """NEW: Added validation method"""
        super().clean()
        if self.points < 0:
            raise ValidationError("Points cannot be negative")
        if not self.criteria:
            raise ValidationError("Achievement must have earning criteria")

    def save(self, *args, **kwargs):
        """NEW: Enhanced save method"""
        self.clean()
        super().save(*args, **kwargs)

class UserAchievement(models.Model):
    """Track achievements earned by users."""
    
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='achievements'
    )
    achievement = models.ForeignKey(
        Achievement,
        on_delete=models.CASCADE
    )
    earned_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the achievement was earned"
    )
    evidence = models.JSONField(
        default=dict,
        help_text="Supporting evidence for achievement"
    )
    awarded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='awarded_achievements',
        help_text="User who awarded this achievement"
    )
    
    class Meta:
        unique_together = ['user', 'achievement']
        ordering = ['-earned_at']
        indexes = [
            models.Index(fields=['user', 'achievement']),
            models.Index(fields=['-earned_at']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.achievement.name}"

    def save(self, *args, **kwargs):
        """NEW: Enhanced save method with activity tracking"""
        creating = not self.pk
        with transaction.atomic():
            super().save(*args, **kwargs)
            
            if creating:
                # Create activity record
                UserActivity.objects.create(
                    user=self.user,
                    activity_type='ACHIEVEMENT_EARNED',
                    activity_detail={
                        'achievement': self.achievement.name,
                        'points': self.achievement.points,
                        'awarded_by': self.awarded_by.email if self.awarded_by else 'System'
                    }
                )

class UserActivity(models.Model):
    """Track user activities and system interactions."""
    
    ACTIVITY_TYPES = [
        ('LOGIN', 'User Login'),
        ('LOGOUT', 'User Logout'),
        ('ENROLL', 'Course Enrollment'),
        ('COMPLETE', 'Course Completion'),
        ('CERTIFICATE', 'Certificate Generated'),
        ('ASSESSMENT', 'Assessment Taken'),
        ('SKILL_UPDATE', 'Skill Updated'),
        ('ACHIEVEMENT_EARNED', 'Achievement Earned'),
        ('PROFILE_UPDATE', 'Profile Updated'),
        ('PASSWORD_CHANGE', 'Password Changed'),
        ('ROLE_CHANGE', 'Role Changed'),  # NEW: Added activity type
        ('USER_CREATION', 'User Created'),  # NEW: Added activity type
        ('SKILL_VERIFICATION', 'Skill Verified')  # NEW: Added activity type
    ]
    
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='activities'
    )
    activity_type = models.CharField(
        max_length=20, 
        choices=ACTIVITY_TYPES,
        help_text="Type of activity"
    )
    activity_detail = models.JSONField(
        default=dict,
        help_text="Additional details about the activity"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the activity occurred"
    )
    ip_address = models.GenericIPAddressField(
        null=True, 
        blank=True,
        help_text="IP address of the user"
    )
    user_agent = models.TextField(
        blank=True,
        help_text="User agent string"
    )
    session_id = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Session identifier"
    )
    
    class Meta:
        verbose_name_plural = 'User activities'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['activity_type', '-created_at']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.activity_type} - {self.created_at}"

    def save(self, *args, **kwargs):
        """NEW: Enhanced save method with validation"""
        if not self.activity_type in dict(self.ACTIVITY_TYPES):
            raise ValidationError(f"Invalid activity type: {self.activity_type}")
        super().save(*args, **kwargs)

    @classmethod
    def log_activity(cls, user, activity_type, detail=None, request=None):
        """NEW: Helper method for logging activities"""
        try:
            activity_data = {
                'user': user,
                'activity_type': activity_type,
                'activity_detail': detail or {}
            }
            
            if request:
                activity_data.update({
                    'ip_address': request.META.get('REMOTE_ADDR'),
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                    'session_id': request.session.session_key
                })
            
            return cls.objects.create(**activity_data)
        except Exception as e:
            logger.error(f"Error logging activity for {user.email}: {str(e)}")
            raise