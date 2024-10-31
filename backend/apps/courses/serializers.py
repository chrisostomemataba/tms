# apps/courses/serializers.py

from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction

from .models import (
    Course, Module, Lesson, Assignment, Enrollment,
    Progress, LiveSession, SessionAttendance,
    CourseCategory, DifficultyLevel, DeliveryMethod,
    EnrollmentStatus
)
from apps.users.serializers import UserSerializer, SkillSerializer

User = get_user_model()

class ModuleSerializer(serializers.ModelSerializer):
    """Serializer for Course Modules."""
    
    lesson_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Module
        fields = [
            'id', 'course', 'title', 'description', 'order',
            'duration_hours', 'is_required', 'lesson_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        """Validate module data."""
        if data.get('duration_hours', 0) > data['course'].duration_hours:
            raise ValidationError(
                "Module duration cannot exceed course duration"
            )
        return data

class LessonSerializer(serializers.ModelSerializer):
    """Serializer for Lessons."""
    
    class Meta:
        model = Lesson
        fields = [
            'id', 'module', 'title', 'description', 'content_type',
            'content', 'order', 'duration_minutes', 'is_required',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_content(self, value):
        """Validate content based on content_type."""
        content_type = self.initial_data.get('content_type')
        required_fields = {
            'VIDEO': ['url', 'duration'],
            'DOCUMENT': ['url', 'file_type'],
            'PRESENTATION': ['url', 'slide_count'],
            'INTERACTIVE': ['type', 'config'],
            'EXTERNAL': ['url', 'platform'],
            'LIVE_SESSION': ['session_id']
        }
        
        if content_type and content_type in required_fields:
            missing = [
                field for field in required_fields[content_type]
                if field not in value
            ]
            if missing:
                raise ValidationError(
                    f"Missing required fields for {content_type}: {missing}"
                )
        return value

class AssignmentSerializer(serializers.ModelSerializer):
    """Serializer for Course Assignments."""
    
    class Meta:
        model = Assignment
        fields = [
            'id', 'course', 'title', 'description', 'instructions',
            'due_days', 'passing_score', 'max_attempts', 'weight',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class EnrollmentSerializer(serializers.ModelSerializer):
    """Serializer for Course Enrollments."""
    
    user_details = UserSerializer(source='user', read_only=True)
    progress_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = Enrollment
        fields = [
            'id', 'user', 'user_details', 'course', 'status',
            'enrolled_at', 'started_at', 'completed_at', 'due_date',
            'completion_percentage', 'grade', 'certificate_issued',
            'certificate_issued_at', 'progress_summary'
        ]
        read_only_fields = [
            'id', 'enrolled_at', 'started_at', 'completed_at',
            'completion_percentage', 'grade', 'certificate_issued',
            'certificate_issued_at'
        ]

    def get_progress_summary(self, obj):
        """Get enrollment progress summary."""
        progress_records = obj.progress_records.all()
        return {
            'total_lessons': progress_records.filter(
                lesson__isnull=False
            ).count(),
            'completed_lessons': progress_records.filter(
                lesson__isnull=False,
                status='COMPLETED'
            ).count(),
            'total_assignments': progress_records.filter(
                assignment__isnull=False
            ).count(),
            'completed_assignments': progress_records.filter(
                assignment__isnull=False,
                status='COMPLETED'
            ).count(),
            'average_score': progress_records.filter(
                score__isnull=False
            ).aggregate(Avg('score'))['score__avg']
        }

class ProgressSerializer(serializers.ModelSerializer):
    """Serializer for Progress tracking."""
    
    class Meta:
        model = Progress
        fields = [
            'id', 'enrollment', 'lesson', 'assignment', 'status',
            'progress_data', 'score', 'attempt_count', 'time_spent',
            'last_interaction', 'completed_at', 'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'completed_at',
            'last_interaction'
        ]

    def validate(self, data):
        """Validate progress data."""
        if not data.get('lesson') and not data.get('assignment'):
            raise ValidationError(
                "Either lesson or assignment must be specified"
            )
        if data.get('lesson') and data.get('assignment'):
            raise ValidationError(
                "Cannot track progress for both lesson and assignment"
            )
        return data

class LiveSessionSerializer(serializers.ModelSerializer):
    """Serializer for Live Sessions."""
    
    instructor_details = UserSerializer(
        source='instructor',
        read_only=True
    )
    attendance_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = LiveSession
        fields = [
            'id', 'course', 'title', 'description', 'instructor',
            'instructor_details', 'start_time', 'end_time',
            'max_participants', 'meeting_url', 'location',
            'materials', 'status', 'attendance_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        """Validate session data."""
        if data.get('end_time') <= data.get('start_time'):
            raise ValidationError(
                "End time must be after start time"
            )
        
        course = data.get('course')
        if course and course.delivery_method not in [
            DeliveryMethod.INSTRUCTOR_LED,
            DeliveryMethod.BLENDED,
            DeliveryMethod.LIVE_ONLINE
        ]:
            raise ValidationError(
                "Live sessions are only for instructor-led courses"
            )
        return data

class SessionAttendanceSerializer(serializers.ModelSerializer):
    """Serializer for Session Attendance."""
    
    user_details = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = SessionAttendance
        fields = [
            'id', 'session', 'user', 'user_details', 'status',
            'join_time', 'leave_time', 'attendance_duration',
            'feedback', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'attendance_duration', 'created_at', 'updated_at'
        ]

class CourseSerializer(serializers.ModelSerializer):
    """Serializer for Courses with nested relationships."""
    
    created_by_details = UserSerializer(
        source='created_by',
        read_only=True
    )
    instructors_details = UserSerializer(
        source='instructors',
        many=True,
        read_only=True
    )
    required_skills_details = SkillSerializer(
        source='required_skills',
        many=True,
        read_only=True
    )
    modules = ModuleSerializer(many=True, read_only=True)
    enrollment_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'code', 'description', 'category',
            'difficulty_level', 'delivery_method', 'duration_hours',
            'max_participants', 'prerequisites', 'required_skills',
            'required_skills_details', 'is_active', 'is_certificate_provided',
            'auto_enrollment', 'completion_criteria', 'created_at',
            'updated_at', 'published_at', 'created_by', 'created_by_details',
            'instructors', 'instructors_details', 'modules',
            'enrollment_count'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'created_by'
        ]

    def create(self, validated_data):
        """Create course with nested relationships."""
        instructors_data = validated_data.pop('instructors', [])
        required_skills_data = validated_data.pop('required_skills', [])
        prerequisites_data = validated_data.pop('prerequisites', [])
        
        with transaction.atomic():
            # Set the creator
            validated_data['created_by'] = self.context['request'].user
            
            # Create the course
            course = Course.objects.create(**validated_data)
            
            # Add relationships
            if instructors_data:
                course.instructors.set(instructors_data)
            if required_skills_data:
                course.required_skills.set(required_skills_data)
            if prerequisites_data:
                course.prerequisites.set(prerequisites_data)
            
            return course

    def update(self, instance, validated_data):
        """Update course with nested relationships."""
        instructors_data = validated_data.pop('instructors', None)
        required_skills_data = validated_data.pop('required_skills', None)
        prerequisites_data = validated_data.pop('prerequisites', None)
        
        with transaction.atomic():
            # Update the course
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            
            # Update relationships if provided
            if instructors_data is not None:
                instance.instructors.set(instructors_data)
            if required_skills_data is not None:
                instance.required_skills.set(required_skills_data)
            if prerequisites_data is not None:
                instance.prerequisites.set(prerequisites_data)
            
            return instance

    def validate(self, data):
        """Validate course data."""
        if data.get('published_at') and not data.get('is_active', True):
            raise ValidationError(
                "Published courses cannot be inactive"
            )
            
        if (data.get('delivery_method') == DeliveryMethod.INSTRUCTOR_LED and
            not data.get('instructors', [])):
            raise ValidationError(
                "Instructor-led courses must have at least one instructor"
            )
        return data