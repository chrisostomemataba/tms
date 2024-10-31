
# apps/users/serializers.py
from django.db import models
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator  # Add this import at the top
from .models import (
    UserProfile, UserActivity, Skill, UserSkill,
    TrainingPreference, Achievement, UserAchievement,
    UserRole
)
from phonenumber_field.serializerfields import PhoneNumberField
from django.db import transaction

User = get_user_model()

class SkillSerializer(serializers.ModelSerializer):
    """Serializer for Skill model."""
    
    class Meta:
        model = Skill
        fields = [
            'id', 'name', 'category', 'description',
            'prerequisites', 'level_criteria', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def validate_level_criteria(self, value):
        """Ensure level criteria contains required proficiency levels."""
        required_levels = ['BEGINNER', 'INTERMEDIATE', 'ADVANCED', 'EXPERT']
        if not all(level in value for level in required_levels):
            raise ValidationError(
                f"Level criteria must contain all proficiency levels: {required_levels}"
            )
        return value

class UserSkillSerializer(serializers.ModelSerializer):
    """Serializer for UserSkill model with nested Skill details."""
    
    skill_details = SkillSerializer(source='skill', read_only=True)
    skill_id = serializers.UUIDField(write_only=True)
    verified_by_email = serializers.EmailField(
        source='verified_by.email',
        read_only=True
    )

    class Meta:
        model = UserSkill
        fields = [
            'id', 'skill_id', 'skill_details', 'proficiency_level',
            'verified', 'verified_by_email', 'verification_date',
            'evidence'
        ]
        read_only_fields = ['id', 'verified', 'verified_by', 'verification_date']

    def validate_skill_id(self, value):
        try:
            Skill.objects.get(id=value)
            return value
        except Skill.DoesNotExist:
            raise ValidationError("Invalid skill ID provided")

class TrainingPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for TrainingPreference model."""

    class Meta:
        model = TrainingPreference
        fields = [
            'id', 'preferred_learning_style', 'preferred_training_days',
            'preferred_time_slots', 'preferred_group_size',
            'language_preferences', 'notification_preferences',
            'accessibility_requirements'
        ]
        read_only_fields = ['id']

    def validate_preferred_training_days(self, value):
        valid_days = [
            'MONDAY', 'TUESDAY', 'WEDNESDAY',
            'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY'
        ]
        if not all(day in valid_days for day in value):
            raise ValidationError(f"Invalid day format. Use: {valid_days}")
        return value

    def validate_preferred_time_slots(self, value):
        for slot in value:
            if 'start' not in slot or 'end' not in slot:
                raise ValidationError(
                    "Each time slot must contain 'start' and 'end' times"
                )
        return value

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model with nested relationships."""
    
    phone_number = PhoneNumberField(required=False)
    skills = UserSkillSerializer(many=True, read_only=True)
    training_preferences = TrainingPreferenceSerializer(required=False)
    total_points = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            'id', 'phone_number', 'department', 'position', 'bio',
            'avatar', 'years_of_experience', 'education', 'certifications',
            'linkedin_profile', 'github_profile', 'portfolio_website',
            'ui_preferences', 'notification_settings', 'skills',
            'training_preferences', 'total_points'
        ]
        read_only_fields = ['id']

    def get_total_points(self, obj):
        """Calculate total achievement points for the user."""
        return obj.user.achievements.aggregate(
            total=models.Sum('achievement__points')
        )['total'] or 0

    def update(self, instance, validated_data):
        training_prefs_data = validated_data.pop('training_preferences', None)
        
        # Update profile
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update training preferences if provided
        if training_prefs_data and hasattr(instance, 'training_preferences'):
            training_prefs_serializer = TrainingPreferenceSerializer(
                instance.training_preferences,
                data=training_prefs_data,
                partial=True
            )
            if training_prefs_serializer.is_valid():
                training_prefs_serializer.save()

        return instance

class AchievementSerializer(serializers.ModelSerializer):
    """Serializer for Achievement model."""

    class Meta:
        model = Achievement
        fields = [
            'id', 'name', 'description', 'category', 'badge_image',
            'points', 'criteria', 'is_active'
        ]
        read_only_fields = ['id']

class UserAchievementSerializer(serializers.ModelSerializer):
    """Serializer for UserAchievement model with achievement details."""
    
    achievement_details = AchievementSerializer(
        source='achievement',
        read_only=True
    )

    class Meta:
        model = UserAchievement
        fields = [
            'id', 'achievement_details', 'earned_at',
            'evidence', 'awarded_by'
        ]
        read_only_fields = ['id', 'earned_at', 'awarded_by']

class UserActivitySerializer(serializers.ModelSerializer):
    """Serializer for UserActivity model."""

    class Meta:
        model = UserActivity
        fields = [
            'id', 'activity_type', 'activity_detail', 'created_at',
            'ip_address', 'user_agent', 'session_id'
        ]
        read_only_fields = [
            'id', 'created_at', 'ip_address',
            'user_agent', 'session_id'
        ]

class UserSerializer(serializers.ModelSerializer):
    """Main serializer for User model with nested relationships."""
    
    profile = UserProfileSerializer(required=False)
    activities = UserActivitySerializer(many=True, read_only=True)
    achievements = UserAchievementSerializer(many=True, read_only=True)
    total_achievements = serializers.IntegerField(
        source='achievements.count',
        read_only=True
    )

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'role',
            'is_active', 'profile', 'activities', 'achievements',
            'total_achievements', 'created_at', 'updated_at',
            'last_active'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at',
            'last_active', 'total_achievements'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    @transaction.atomic
    def create(self, validated_data):
        profile_data = validated_data.pop('profile', {})
        password = validated_data.pop('password', None)
        
        # Create user
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()

        # Update profile if data provided
        if profile_data and hasattr(user, 'profile'):
            profile_serializer = UserProfileSerializer(
                user.profile,
                data=profile_data,
                partial=True
            )
            if profile_serializer.is_valid():
                profile_serializer.save()

        return user

class UserRegistrationSerializer(serializers.Serializer):
    """Serializer for user registration."""
    
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[MinLengthValidator(8)]
    )
    confirm_password = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    role = serializers.ChoiceField(
        choices=UserRole.choices,
        default=UserRole.PARTICIPANT
    )

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('confirm_password'):
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError(
                {"email": "User with this email already exists."}
            )
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
