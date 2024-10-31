# apps/users/signals.py

from django.db.models.signals import post_save, pre_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import transaction
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.cache import cache
import logging
import os
import json
from datetime import timedelta
from .models import (
    UserProfile, UserActivity, Skill, UserSkill,
    Achievement, UserAchievement, TrainingPreference,
    UserRole
)

# Configure logger
logger = logging.getLogger('apps.users')

User = get_user_model()

class SignalError(Exception):
    """Custom exception for signal-related errors."""
    pass

def log_signal_error(error_type: str, instance: any, error: Exception) -> None:
    """Centralized error logging for signals."""
    logger.error(
        f"Signal Error - Type: {error_type}, "
        f"Model: {instance.__class__.__name__}, "
        f"ID: {getattr(instance, 'id', 'N/A')}, "
        f"Error: {str(error)}"
    )

@receiver(pre_save, sender=User)
def user_pre_save(sender, instance, **kwargs):
    """
    Enhanced pre-save signal for User model with comprehensive validation 
    and state tracking.
    """
    try:
        # Email normalization and validation
        if instance.email:
            instance.email = instance.email.lower().strip()
        
        # Handle existing user updates
        if not instance._state.adding:
            try:
                old_instance = User.objects.get(id=instance.id)
                
                # Track state changes for post-save processing
                state_changes = {
                    'role_changed': old_instance.role != instance.role,
                    'old_role': old_instance.role,
                    'status_changed': old_instance.is_active != instance.is_active,
                    'old_status': old_instance.is_active,
                }
                
                # Store state changes for post_save signal
                instance._state_changes = state_changes
                
                # Role change validation
                if (old_instance.role == UserRole.ADMIN and 
                    instance.role != UserRole.ADMIN):
                    # Prevent removal of last admin
                    admin_count = User.objects.filter(
                        role=UserRole.ADMIN
                    ).exclude(id=instance.id).count()
                    
                    if admin_count < 1:
                        raise ValidationError(
                            "Cannot remove the last admin user"
                        )
                
                # Handle deactivation
                if old_instance.is_active and not instance.is_active:
                    if not instance.deactivation_reason:
                        instance.deactivation_reason = "Manual deactivation"
                    instance.deactivated_at = timezone.now()
                
                # Handle reactivation
                elif not old_instance.is_active and instance.is_active:
                    instance.deactivated_at = None
                    instance.deactivation_reason = ""
                    instance.failed_login_attempts = 0
                    instance.last_failed_login = None

            except User.DoesNotExist:
                # Handle race condition
                logger.warning(
                    f"Race condition detected in user_pre_save for user {instance.id}"
                )
                
    except Exception as e:
        log_signal_error("pre_save", instance, e)
        raise SignalError(f"Error in user_pre_save: {str(e)}")

@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    """
    Enhanced post-save signal for User model with atomic operations 
    and comprehensive activity tracking.
    """
    try:
        with transaction.atomic():
            if created:
                # Initialize user profile with default preferences
                profile = UserProfile.objects.create(
                    user=instance,
                    ui_preferences={
                        'theme': 'light',
                        'notifications_enabled': True,
                        'language': settings.LANGUAGE_CODE,
                        'timezone': settings.TIME_ZONE
                    }
                )

                # Initialize training preferences
                TrainingPreference.objects.create(
                    user_profile=profile,
                    preferred_learning_style='VISUAL',
                    preferred_training_days=['MONDAY', 'WEDNESDAY', 'FRIDAY'],
                    preferred_time_slots=[
                        {'start': '09:00', 'end': '17:00'}
                    ],
                    notification_preferences={
                        'email': True,
                        'in_app': True,
                        'reminders': {
                            'enabled': True,
                            'advance_notice': '1d'
                        }
                    }
                )

                # Record creation activity
                UserActivity.objects.create(
                    user=instance,
                    activity_type='USER_CREATION',
                    activity_detail={
                        'role': instance.role,
                        'email': instance.email,
                        'source': 'system'
                    }
                )

                # Initialize default trainer skills if applicable
                if instance.role == UserRole.TRAINER:
                    default_trainer_skill = Skill.objects.filter(
                        category='TRAINING_BASICS'
                    ).first()
                    
                    if default_trainer_skill:
                        UserSkill.objects.create(
                            user_profile=profile,
                            skill=default_trainer_skill,
                            proficiency_level='INTERMEDIATE',
                            verified=True,
                            verified_by=instance,
                            verification_date=timezone.now()
                        )

            else:
                # Process state changes from pre_save
                state_changes = getattr(instance, '_state_changes', {})
                
                if state_changes.get('role_changed'):
                    UserActivity.objects.create(
                        user=instance,
                        activity_type='ROLE_CHANGE',
                        activity_detail={
                            'old_role': state_changes['old_role'],
                            'new_role': instance.role,
                            'changed_by': getattr(
                                instance, '_change_user', 'system'
                            )
                        }
                    )

                if state_changes.get('status_changed'):
                    activity_type = (
                        'USER_ACTIVATED' if instance.is_active 
                        else 'USER_DEACTIVATED'
                    )
                    
                    UserActivity.objects.create(
                        user=instance,
                        activity_type=activity_type,
                        activity_detail={
                            'old_status': state_changes['old_status'],
                            'reason': instance.deactivation_reason,
                            'changed_by': getattr(
                                instance, '_change_user', 'system'
                            )
                        }
                    )

            # Update last active timestamp
            cache_key = f'user_last_active_{instance.id}'
            cached_time = cache.get(cache_key)
            
            if cached_time:
                current_time = timezone.now()
                if current_time - cached_time > timedelta(minutes=5):
                    instance.last_active = current_time
                    instance.save(update_fields=['last_active'])
                    cache.set(cache_key, current_time, timeout=300)  # 5 minutes

    except Exception as e:
        log_signal_error("post_save", instance, e)
        raise SignalError(f"Error in user_post_save: {str(e)}")

@receiver(pre_save, sender=UserSkill)
def skill_verification_validation(sender, instance, **kwargs):
    """
    Enhanced skill verification validation with comprehensive checks 
    and activity tracking.
    """
    try:
        if instance.pk and not instance._state.adding:  # Only for existing skills
            old_instance = UserSkill.objects.get(pk=instance.pk)
            
            # Track verification changes
            if not old_instance.verified and instance.verified:
                if not instance.verified_by:
                    raise ValidationError("Verifier must be specified")

                # Validate verifier permissions
                if instance.verified_by.role not in [
                    UserRole.ADMIN, 
                    UserRole.TRAINER
                ]:
                    raise ValidationError(
                        "Only admins and trainers can verify skills"
                    )

                # Additional validation for trainers
                if instance.verified_by.role == UserRole.TRAINER:
                    verifier_skill = UserSkill.objects.filter(
                        user_profile=instance.verified_by.profile,
                        skill=instance.skill,
                        verified=True,
                        proficiency_level__in=['ADVANCED', 'EXPERT']
                    ).first()
                    
                    if not verifier_skill:
                        raise ValidationError(
                            "Trainer must have advanced or expert level "
                            "in this skill to verify others"
                        )

                instance.verification_date = timezone.now()

    except Exception as e:
        log_signal_error("pre_save", instance, e)
        raise SignalError(f"Error in skill_verification_validation: {str(e)}")

@receiver(post_save, sender=UserAchievement)
def achievement_awarded(sender, instance, created, **kwargs):
    """
    Enhanced achievement handling with milestone tracking and 
    automated awards.
    """
    if created:
        try:
            with transaction.atomic():
                # Record achievement activity
                UserActivity.objects.create(
                    user=instance.user,
                    activity_type='ACHIEVEMENT_EARNED',
                    activity_detail={
                        'achievement': instance.achievement.name,
                        'points': instance.achievement.points,
                        'awarded_by': (
                            instance.awarded_by.email 
                            if instance.awarded_by 
                            else 'System'
                        )
                    }
                )

                # Check for milestone achievements
                user_achievements = UserAchievement.objects.filter(
                    user=instance.user
                )
                
                achievement_count = user_achievements.count()
                total_points = sum(
                    ua.achievement.points for ua in user_achievements
                )

                # Milestone mappings
                milestones = {
                    'achievements': {
                        5: 'ACHIEVEMENT_COLLECTOR_BRONZE',
                        10: 'ACHIEVEMENT_COLLECTOR_SILVER',
                        20: 'ACHIEVEMENT_COLLECTOR_GOLD'
                    },
                    'points': {
                        100: 'POINTS_MILESTONE_BRONZE',
                        500: 'POINTS_MILESTONE_SILVER',
                        1000: 'POINTS_MILESTONE_GOLD'
                    }
                }

                # Check achievement count milestones
                if achievement_count in milestones['achievements']:
                    milestone_name = milestones['achievements'][
                        achievement_count
                    ]
                    milestone = Achievement.objects.filter(
                        name=milestone_name,
                        is_active=True
                    ).first()
                    
                    if milestone:
                        UserAchievement.objects.create(
                            user=instance.user,
                            achievement=milestone,
                            evidence={
                                'type': 'milestone',
                                'trigger': 'achievement_count',
                                'count': achievement_count
                            }
                        )

                # Check points milestones
                for point_threshold, milestone_name in milestones[
                    'points'
                ].items():
                    if (total_points >= point_threshold and
                        not UserAchievement.objects.filter(
                            user=instance.user,
                            achievement__name=milestone_name
                        ).exists()):
                        
                        milestone = Achievement.objects.filter(
                            name=milestone_name,
                            is_active=True
                        ).first()
                        
                        if milestone:
                            UserAchievement.objects.create(
                                user=instance.user,
                                achievement=milestone,
                                evidence={
                                    'type': 'milestone',
                                    'trigger': 'points',
                                    'total_points': total_points
                                }
                            )

        except Exception as e:
            log_signal_error("post_save", instance, e)
            raise SignalError(f"Error in achievement_awarded: {str(e)}")

@receiver(pre_save, sender=UserProfile)
def handle_profile_image(sender, instance, **kwargs):
    """
    Handle profile image processing and cleanup.
    """
    try:
        if instance.pk and not instance._state.adding:  # Only for existing profiles
            try:
                old_instance = UserProfile.objects.get(pk=instance.pk)
                
                # Handle avatar change
                if old_instance.avatar and (
                    not instance.avatar or 
                    old_instance.avatar != instance.avatar
                ):
                    # Delete old avatar
                    if default_storage.exists(old_instance.avatar.name):
                        default_storage.delete(old_instance.avatar.name)
            except UserProfile.DoesNotExist:
                # Profile doesn't exist yet, skip cleanup
                pass
                    
        # Process new avatar if needed
        if instance.avatar:
            # Implement image processing here if needed
            pass

    except Exception as e:
        log_signal_error("pre_save", instance, e)
        raise SignalError(f"Error in handle_profile_image: {str(e)}")

@receiver(m2m_changed, sender=Skill.prerequisites.through)
def skill_prerequisites_changed(sender, instance, action, pk_set, **kwargs):
    """
    Enhanced prerequisite management with circular dependency prevention 
    and validation.
    """
    try:
        if action == "pre_add":
            def check_circular(skill, prereq_id, checked=None):
                """Recursive check for circular dependencies."""
                if checked is None:
                    checked = set()
                if skill.id in checked:
                    return True
                checked.add(skill.id)
                prereq = Skill.objects.get(id=prereq_id)
                for p in prereq.prerequisites.all():
                    if check_circular(skill, p.id, checked):
                        return True
                return False

            # Validate each new prerequisite
            for prereq_id in pk_set:
                # Check for self-reference
                if instance.id == prereq_id:
                    raise ValidationError(
                        "A skill cannot be its own prerequisite"
                    )
                
                # Check for circular dependency
                if check_circular(instance, prereq_id):
                    raise ValidationError(
                        "Adding this prerequisite would create a "
                        "circular dependency"
                    )
                
                # Validate skill exists
                try:
                    prerequisite = Skill.objects.get(id=prereq_id)
                except Skill.DoesNotExist:
                    raise ValidationError(
                        f"Prerequisite skill {prereq_id} does not exist"
                    )

    except Exception as e:
        log_signal_error("m2m_changed", instance, e)
        raise SignalError(f"Error in skill_prerequisites_changed: {str(e)}")

# Continuing from where we left off in signals.py

@receiver(post_delete, sender=UserProfile)
def clean_up_user_files(sender, instance, **kwargs):
    """
    Enhanced file cleanup with error handling and logging.
    """
    try:
        # Clean up avatar
        if instance.avatar:
            if default_storage.exists(instance.avatar.name):
                default_storage.delete(instance.avatar.name)
                logger.info(
                    f"Deleted avatar for user profile {instance.id}"
                )

        # Clean up any other associated files
        user_files_path = os.path.join(
            settings.MEDIA_ROOT, 
            'user_files', 
            str(instance.user.id)
        )
        if os.path.exists(user_files_path):
            for root, dirs, files in os.walk(user_files_path, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(user_files_path)
            logger.info(
                f"Cleaned up file directory for user {instance.user.id}"
            )

    except Exception as e:
        # Log error but don't raise - this is cleanup
        log_signal_error("post_delete", instance, e)
        logger.warning(
            f"Error cleaning up files for user profile {instance.id}: {str(e)}"
        )

@receiver(pre_save, sender=TrainingPreference)
def validate_training_preferences(sender, instance, **kwargs):
    """
    Validate and normalize training preferences before save.
    """
    try:
        # Validate training days
        valid_days = {
            'MONDAY', 'TUESDAY', 'WEDNESDAY', 
            'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY'
        }
        if instance.preferred_training_days:
            days = instance.preferred_training_days
            if not isinstance(days, list):
                raise ValidationError("Training days must be a list")
            if not all(day in valid_days for day in days):
                raise ValidationError(
                    f"Invalid training day. Must be one of: {valid_days}"
                )

        # Validate time slots
        if instance.preferred_time_slots:
            for slot in instance.preferred_time_slots:
                if not isinstance(slot, dict):
                    raise ValidationError("Time slots must be dictionaries")
                if 'start' not in slot or 'end' not in slot:
                    raise ValidationError(
                        "Time slots must contain 'start' and 'end' times"
                    )
                # Additional time validation could be added here

        # Normalize notification preferences
        if not instance.notification_preferences:
            instance.notification_preferences = {
                'email': True,
                'in_app': True,
                'reminders': {
                    'enabled': True,
                    'advance_notice': '1d'
                }
            }

    except Exception as e:
        log_signal_error("pre_save", instance, e)
        raise SignalError(f"Error in validate_training_preferences: {str(e)}")

@receiver(post_save, sender=UserSkill)
def update_skill_statistics(sender, instance, created, **kwargs):
    """
    Update skill statistics after skill updates.
    """
    try:
        with transaction.atomic():
            skill = instance.skill
            
            # Update cache keys
            cache_keys = [
                f'skill_stats_{skill.id}',
                f'user_skills_{instance.user_profile.user.id}',
                'global_skill_stats'
            ]
            for key in cache_keys:
                cache.delete(key)

            # Calculate new statistics
            total_users = UserSkill.objects.filter(skill=skill).count()
            verified_users = UserSkill.objects.filter(
                skill=skill, 
                verified=True
            ).count()
            
            skill_stats = {
                'total_users': total_users,
                'verified_users': verified_users,
                'verification_rate': (
                    (verified_users / total_users * 100) 
                    if total_users > 0 else 0
                ),
                'proficiency_distribution': {
                    level: UserSkill.objects.filter(
                        skill=skill, 
                        proficiency_level=level
                    ).count()
                    for level, _ in UserSkill.PROFICIENCY_LEVELS
                }
            }

            # Cache the new statistics
            cache.set(
                f'skill_stats_{skill.id}',
                skill_stats,
                timeout=3600  # 1 hour
            )

            # Log significant changes
            if created or instance.verified:
                UserActivity.objects.create(
                    user=instance.user_profile.user,
                    activity_type='SKILL_UPDATE',
                    activity_detail={
                        'skill': skill.name,
                        'action': 'created' if created else 'verified',
                        'proficiency_level': instance.proficiency_level,
                        'verified': instance.verified
                    }
                )

    except Exception as e:
        log_signal_error("post_save", instance, e)
        logger.error(f"Error updating skill statistics: {str(e)}")

def connect_signals():
    """
    Explicitly connect all signals and verify connections.
    Call this in apps.py ready() method.
    """
    try:
        logger.info("Connecting user management signals")
        
        # Store signal connections for verification
        connections = [
            (pre_save, user_pre_save, User),
            (post_save, user_post_save, User),
            (pre_save, skill_verification_validation, UserSkill),
            (post_save, achievement_awarded, UserAchievement),
            (pre_save, handle_profile_image, UserProfile),
            (m2m_changed, skill_prerequisites_changed, Skill.prerequisites.through),
            (post_delete, clean_up_user_files, UserProfile),
            (pre_save, validate_training_preferences, TrainingPreference),
            (post_save, update_skill_statistics, UserSkill),
        ]

        # Connect all signals
        for signal, handler, sender in connections:
            signal.connect(handler, sender=sender)
            
            # Verify connection
            if not signal.has_listeners(sender):
                raise SignalError(
                    f"Failed to connect signal {handler.__name__} "
                    f"for {sender.__name__}"
                )

        logger.info("Successfully connected all user management signals")

    except Exception as e:
        logger.error(f"Error connecting signals: {str(e)}")
        raise SignalError(f"Failed to connect signals: {str(e)}")

# Cleanup function for testing
def disconnect_signals():
    """
    Disconnect all signals - useful for testing.
    """
    try:
        logger.info("Disconnecting user management signals")
        
        # Store signal connections for verification
        connections = [
            (pre_save, user_pre_save, User),
            (post_save, user_post_save, User),
            (pre_save, skill_verification_validation, UserSkill),
            (post_save, achievement_awarded, UserAchievement),
            (pre_save, handle_profile_image, UserProfile),
            (m2m_changed, skill_prerequisites_changed, Skill.prerequisites.through),
            (post_delete, clean_up_user_files, UserProfile),
            (pre_save, validate_training_preferences, TrainingPreference),
            (post_save, update_skill_statistics, UserSkill),
        ]

        # Disconnect all signals
        for signal, handler, sender in connections:
            signal.disconnect(handler, sender=sender)
            
            # Verify disconnection
            if signal.has_listeners(sender):
                logger.warning(
                    f"Signal {handler.__name__} for {sender.__name__} "
                    "may still be connected"
                )

        logger.info("Successfully disconnected all user management signals")

    except Exception as e:
        logger.error(f"Error disconnecting signals: {str(e)}")
        raise SignalError(f"Failed to disconnect signals: {str(e)}")