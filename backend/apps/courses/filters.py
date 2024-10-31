# apps/courses/filters.py

import django_filters
from .models import (
   Course, Enrollment, Progress, LiveSession,
   CourseCategory, DifficultyLevel, DeliveryMethod
)

class CourseFilter(django_filters.FilterSet):
   category = django_filters.ChoiceFilter(choices=CourseCategory.choices)
   difficulty_level = django_filters.ChoiceFilter(choices=DifficultyLevel.choices)
   delivery_method = django_filters.ChoiceFilter(choices=DeliveryMethod.choices)
   instructor = django_filters.UUIDFilter(field_name='instructors')
   required_skill = django_filters.UUIDFilter(field_name='required_skills')
   min_duration = django_filters.NumberFilter(field_name='duration_hours', lookup_expr='gte')
   max_duration = django_filters.NumberFilter(field_name='duration_hours', lookup_expr='lte')
   
   class Meta:
       model = Course
       fields = ['category', 'difficulty_level', 'delivery_method', 'is_active']

class EnrollmentFilter(django_filters.FilterSet):
   status = django_filters.ChoiceFilter(choices=Enrollment.status.field.choices)
   enrolled_after = django_filters.DateTimeFilter(field_name='enrolled_at', lookup_expr='gte')
   enrolled_before = django_filters.DateTimeFilter(field_name='enrolled_at', lookup_expr='lte')
   min_completion = django_filters.NumberFilter(field_name='completion_percentage', lookup_expr='gte')
   
   class Meta:
       model = Enrollment
       fields = ['status', 'course', 'user']

class ProgressFilter(django_filters.FilterSet):
   status = django_filters.ChoiceFilter(choices=Progress.status.field.choices)
   min_score = django_filters.NumberFilter(field_name='score', lookup_expr='gte')
   max_attempts = django_filters.NumberFilter(field_name='attempt_count', lookup_expr='lte')
   
   class Meta:
       model = Progress
       fields = ['status', 'lesson', 'assignment']

class LiveSessionFilter(django_filters.FilterSet):
   status = django_filters.ChoiceFilter(choices=LiveSession.status.field.choices)
   instructor = django_filters.UUIDFilter(field_name='instructor')
   start_after = django_filters.DateTimeFilter(field_name='start_time', lookup_expr='gte')
   start_before = django_filters.DateTimeFilter(field_name='start_time', lookup_expr='lte')
   
   class Meta:
       model = LiveSession
       fields = ['status', 'instructor']