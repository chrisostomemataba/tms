# apps/courses/permissions.py

from rest_framework import permissions
from .models import Course, Enrollment

class IsInstructorOrAdmin(permissions.BasePermission):
   """Permission to check if user is instructor or admin."""
   
   def has_permission(self, request, view):
       return request.user.is_staff or request.user.role in ['ADMIN', 'TRAINER']

class CanManageCourse(permissions.BasePermission):
   """Permission to manage course content."""
   
   def has_object_permission(self, request, view, obj):
       course = obj.course if hasattr(obj, 'course') else obj
       return (
           request.user.is_staff or
           request.user in course.instructors.all() or
           request.user == course.created_by
       )

class CanEnrollCourse(permissions.BasePermission):
   """Permission to enroll in courses."""
   
   def has_permission(self, request, view):
       return request.user.is_authenticated

   def has_object_permission(self, request, view, obj):
       if not obj.is_active:
           return False
       if obj.max_participants and \
          obj.enrollments.count() >= obj.max_participants:
           return False
       return True

class CanAccessCourseContent(permissions.BasePermission):
   """Permission to access course content."""
   
   def has_object_permission(self, request, view, obj):
       enrollment = obj.enrollment if hasattr(obj, 'enrollment') else obj
       return (
           request.user.is_staff or
           request.user == enrollment.user or
           request.user in enrollment.course.instructors.all()
       )