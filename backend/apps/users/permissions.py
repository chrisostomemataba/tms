# apps/users/permissions.py

from rest_framework import permissions
from django.core.exceptions import ObjectDoesNotExist
from .models import UserRole

class IsAdminUser(permissions.BasePermission):
    """
    Permission to only allow admin users.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role == UserRole.ADMIN
        )

class IsTrainerOrAdmin(permissions.BasePermission):
    """
    Permission to allow trainers and admins.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role in [UserRole.TRAINER, UserRole.ADMIN]
        )

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission to allow owners of an object or admins.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        # Admin has full access
        if request.user.role == UserRole.ADMIN:
            return True

        # Handle different object types
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'user_profile'):
            return obj.user_profile.user == request.user
        
        # For User model itself
        return obj == request.user

class IsUserProfileOwner(permissions.BasePermission):
    """
    Permission to only allow users to modify their own profile.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        # Admin has full access
        if request.user.role == UserRole.ADMIN:
            return True

        # Check if the user owns the profile
        return obj.user == request.user

class CanVerifySkills(permissions.BasePermission):
    """
    Permission to verify user skills.
    Trainers can only verify skills in their expertise areas.
    Admins can verify any skill.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role in [UserRole.TRAINER, UserRole.ADMIN]
        )

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        # Admin can verify any skill
        if request.user.role == UserRole.ADMIN:
            return True

        # Trainers can verify skills in their expertise areas
        if request.user.role == UserRole.TRAINER:
            try:
                trainer_skills = request.user.profile.skills.filter(
                    verified=True,
                    skill__category=obj.skill.category
                ).exists()
                return trainer_skills
            except ObjectDoesNotExist:
                return False

        return False

class CanAwardAchievements(permissions.BasePermission):
    """
    Permission to award achievements.
    Trainers can award achievements related to their expertise.
    Admins can award any achievement.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role in [UserRole.TRAINER, UserRole.ADMIN]
        )

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        # Admin can award any achievement
        if request.user.role == UserRole.ADMIN:
            return True

        # Trainers can award achievements in their expertise areas
        if request.user.role == UserRole.TRAINER:
            try:
                trainer_category = request.user.profile.skills.filter(
                    verified=True,
                    skill__category=obj.category
                ).exists()
                return trainer_category
            except ObjectDoesNotExist:
                return False

        return False

class CanAccessActivityLogs(permissions.BasePermission):
    """
    Permission to access activity logs.
    Users can only see their own activities.
    Admins can see all activities.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        # Admin can access all logs
        if request.user.role == UserRole.ADMIN:
            return True

        # Users can only access their own logs
        return obj.user == request.user

class CanManageTrainingPreferences(permissions.BasePermission):
    """
    Permission to manage training preferences.
    Users can only manage their own preferences.
    Trainers can view preferences of their trainees.
    Admins can manage all preferences.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        # Admin has full access
        if request.user.role == UserRole.ADMIN:
            return True

        # Trainers can view preferences but not modify them
        if request.user.role == UserRole.TRAINER and request.method in permissions.SAFE_METHODS:
            # Check if trainer is assigned to the user
            return obj.user_profile.user.trainers.filter(id=request.user.id).exists()

        # Users can manage their own preferences
        return obj.user_profile.user == request.user

class IsActiveUser(permissions.BasePermission):
    """
    Permission to check if user is active.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.is_active
        )

class CanAccessReports(permissions.BasePermission):
    """
    Permission to access reports and analytics.
    Trainers can access reports for their trainees.
    Admins can access all reports.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Admin has full access
        if request.user.role == UserRole.ADMIN:
            return True

        # Trainers can access reports
        if request.user.role == UserRole.TRAINER:
            return True

        return False

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        # Admin has full access
        if request.user.role == UserRole.ADMIN:
            return True

        # Trainers can only access reports for their trainees
        if request.user.role == UserRole.TRAINER:
            return obj.user.trainers.filter(id=request.user.id).exists()

        return False