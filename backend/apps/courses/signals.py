# apps/courses/signals.py

from django.db.models.signals import post_save, pre_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import transaction
from django.core.cache import cache

from .models import (
   Course, Module, Lesson, Assignment, Enrollment,
   Progress, LiveSession, SessionAttendance
)
from apps.users.models import UserActivity, Achievement, UserAchievement

import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Course)
def handle_course_post_save(sender, instance, created, **kwargs):
   """Handle course creation/updates."""
   try:
       if created:
           UserActivity.objects.create(
               user=instance.created_by,
               activity_type='COURSE_CREATION',
               activity_detail={
                   'course_id': str(instance.id),
                   'title': instance.title,
                   'category': instance.category
               }
           )
           
           # Clear course cache
           cache_keys = [
               f'course_details_{instance.id}',
               'active_courses',
               f'instructor_courses_{instance.created_by.id}'
           ]
           cache.delete_many(cache_keys)

   except Exception as e:
       logger.error(f"Error in course post_save signal: {str(e)}")

@receiver(post_save, sender=Enrollment)
def handle_enrollment_post_save(sender, instance, created, **kwargs):
   """Handle enrollment status changes."""
   try:
       if created:
           # Record enrollment activity
           UserActivity.objects.create(
               user=instance.user,
               activity_type='COURSE_ENROLLMENT',
               activity_detail={
                   'course_id': str(instance.course.id),
                   'course_title': instance.course.title,
                   'status': instance.status
               }
           )
       
       # Handle completion
       if instance.status == 'COMPLETED':
           with transaction.atomic():
               # Check course completion achievements
               completed_courses = Enrollment.objects.filter(
                   user=instance.user,
                   status='COMPLETED'
               ).count()
               
               achievement_thresholds = {
                   1: 'FIRST_COURSE_COMPLETION',
                   5: 'INTERMEDIATE_LEARNER',
                   10: 'ADVANCED_LEARNER',
                   25: 'EXPERT_LEARNER'
               }
               
               if completed_courses in achievement_thresholds:
                   achievement = Achievement.objects.get(
                       name=achievement_thresholds[completed_courses]
                   )
                   UserAchievement.objects.create(
                       user=instance.user,
                       achievement=achievement,
                       evidence={
                           'course_count': completed_courses,
                           'latest_course': instance.course.title
                       }
                   )
               
               # Issue certificate if applicable
               if instance.course.is_certificate_provided:
                   instance.certificate_issued = True
                   instance.certificate_issued_at = timezone.now()
                   instance.save(update_fields=[
                       'certificate_issued',
                       'certificate_issued_at'
                   ])

   except Exception as e:
       logger.error(f"Error in enrollment post_save signal: {str(e)}")

@receiver(post_save, sender=Progress)
def handle_progress_post_save(sender, instance, created, **kwargs):
   """Handle progress updates."""
   try:
       if instance.status == 'COMPLETED':
           # Record completion activity
           activity_type = (
               'LESSON_COMPLETION' if instance.lesson 
               else 'ASSIGNMENT_COMPLETION'
           )
           target = instance.lesson or instance.assignment
           
           UserActivity.objects.create(
               user=instance.enrollment.user,
               activity_type=activity_type,
               activity_detail={
                   'course': instance.enrollment.course.title,
                   'item_title': target.title,
                   'score': instance.score
               }
           )
           
           # Update enrollment progress
           instance.update_enrollment_progress()

   except Exception as e:
       logger.error(f"Error in progress post_save signal: {str(e)}")

@receiver(post_save, sender=SessionAttendance)
def handle_attendance_post_save(sender, instance, created, **kwargs):
   """Handle session attendance updates."""
   try:
       if instance.status == 'ATTENDED':
           UserActivity.objects.create(
               user=instance.user,
               activity_type='SESSION_ATTENDANCE',
               activity_detail={
                   'session_title': instance.session.title,
                   'course': instance.session.course.title,
                   'duration': str(instance.attendance_duration) if instance.attendance_duration else None
               }
           )
           
           # Check attendance achievements
           attended_sessions = SessionAttendance.objects.filter(
               user=instance.user,
               status='ATTENDED'
           ).count()
           
           if attended_sessions in [5, 10, 25]:
               achievement = Achievement.objects.get(
                   name=f'ATTENDED_{attended_sessions}_SESSIONS'
               )
               UserAchievement.objects.create(
                   user=instance.user,
                   achievement=achievement,
                   evidence={
                       'session_count': attended_sessions,
                       'latest_session': instance.session.title
                   }
               )

   except Exception as e:
       logger.error(f"Error in attendance post_save signal: {str(e)}")

def connect_signals():
   """Connect all signals."""
   logger.info("Connecting course management signals")
   
   # List all signal connections
   signals = [
       (post_save, handle_course_post_save, Course),
       (post_save, handle_enrollment_post_save, Enrollment),
       (post_save, handle_progress_post_save, Progress),
       (post_save, handle_attendance_post_save, SessionAttendance),
   ]
   
   # Connect signals
   for signal, handler, sender in signals:
       signal.connect(handler, sender=sender)
   
   logger.info("Successfully connected course management signals")

def disconnect_signals():
   """Disconnect all signals for testing."""
   signals = [
       (post_save, handle_course_post_save, Course),
       (post_save, handle_enrollment_post_save, Enrollment),
       (post_save, handle_progress_post_save, Progress),
       (post_save, handle_attendance_post_save, SessionAttendance),
   ]
   
   for signal, handler, sender in signals:
       signal.disconnect(handler, sender=sender)