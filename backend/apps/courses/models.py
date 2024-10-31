# apps/courses/models.py

from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
from simple_history.models import HistoricalRecords
from apps.users.models import UserRole, Skill, UserActivity
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)
User = get_user_model()

class CourseCategory(models.TextChoices):
    """Course category choices."""
    TECHNICAL = 'TECHNICAL', _('Technical')
    SOFT_SKILLS = 'SOFT_SKILLS', _('Soft Skills')
    MANAGEMENT = 'MANAGEMENT', _('Management')
    COMPLIANCE = 'COMPLIANCE', _('Compliance')
    ONBOARDING = 'ONBOARDING', _('Onboarding')
    PROFESSIONAL = 'PROFESSIONAL', _('Professional Development')

class DifficultyLevel(models.TextChoices):
    """Course difficulty levels."""
    BEGINNER = 'BEGINNER', _('Beginner')
    INTERMEDIATE = 'INTERMEDIATE', _('Intermediate')
    ADVANCED = 'ADVANCED', _('Advanced')
    EXPERT = 'EXPERT', _('Expert')

class DeliveryMethod(models.TextChoices):
    """Course delivery methods."""
    SELF_PACED = 'SELF_PACED', _('Self-paced')
    INSTRUCTOR_LED = 'INSTRUCTOR_LED', _('Instructor-led')
    BLENDED = 'BLENDED', _('Blended')
    LIVE_ONLINE = 'LIVE_ONLINE', _('Live Online')
    WORKSHOP = 'WORKSHOP', _('Workshop')

class Course(models.Model):
    """
    Main course model representing a training course.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    title = models.CharField(
        max_length=200,
        help_text="Course title"
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique course code"
    )
    description = models.TextField(
        help_text="Detailed course description"
    )
    category = models.CharField(
        max_length=50,
        choices=CourseCategory.choices,
        help_text="Course category"
    )
    difficulty_level = models.CharField(
        max_length=20,
        choices=DifficultyLevel.choices,
        help_text="Course difficulty level"
    )
    delivery_method = models.CharField(
        max_length=20,
        choices=DeliveryMethod.choices,
        help_text="Course delivery method"
    )
    
    # Course metadata
    duration_hours = models.PositiveIntegerField(
        help_text="Expected duration in hours"
    )
    max_participants = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum number of participants (null for unlimited)"
    )
    prerequisites = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='dependent_courses',
        help_text="Prerequisite courses"
    )
    required_skills = models.ManyToManyField(
        Skill,
        blank=True,
        related_name='required_for_courses',
        help_text="Required skills for this course"
    )
    
    # Course configuration
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the course is currently active"
    )
    is_certificate_provided = models.BooleanField(
        default=True,
        help_text="Whether a certificate is provided upon completion"
    )
    auto_enrollment = models.BooleanField(
        default=False,
        help_text="Whether users can enroll themselves"
    )
    completion_criteria = models.JSONField(
        default=dict,
        help_text="Criteria for course completion"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the course was published"
    )
    
    # Relations
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='courses_created',
        help_text="User who created the course"
    )
    instructors = models.ManyToManyField(
        User,
        blank=True,
        related_name='courses_teaching',
        help_text="Course instructors"
    )
    
    # Tracking
    history = HistoricalRecords()
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'difficulty_level']),
            models.Index(fields=['is_active', 'published_at']),
            models.Index(fields=['code']),
        ]
        permissions = [
            ("can_publish_course", "Can publish course"),
            ("can_assign_instructors", "Can assign instructors"),
        ]

    def __str__(self):
        return f"{self.code}: {self.title}"

    def clean(self):
        """Validate course data."""
        if self.published_at and not self.is_active:
            raise ValidationError(
                "Published courses cannot be inactive"
            )
            
        if self.delivery_method == DeliveryMethod.INSTRUCTOR_LED and \
           not self.instructors.exists():
            raise ValidationError(
                "Instructor-led courses must have at least one instructor"
            )

    def save(self, *args, **kwargs):
        """Enhanced save with validation and tracking."""
        self.clean()
        is_new = not self.pk
        
        with transaction.atomic():
            super().save(*args, **kwargs)
            
            if is_new:
                UserActivity.objects.create(
                    user=self.created_by,
                    activity_type='COURSE_CREATION',
                    activity_detail={
                        'course_id': str(self.id),
                        'course_code': self.code,
                        'title': self.title
                    }
                )

    def get_progress_overview(self):
        """Get course progress statistics."""
        enrollments = self.enrollments.all()
        return {
            'total_enrolled': enrollments.count(),
            'completed': enrollments.filter(
                status='COMPLETED'
            ).count(),
            'in_progress': enrollments.filter(
                status='IN_PROGRESS'
            ).count(),
            'completion_rate': (
                enrollments.filter(status='COMPLETED').count() /
                enrollments.count() * 100
                if enrollments.exists() else 0
            )
        }

class Module(models.Model):
    """
    Course module/section containing lessons.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='modules'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    order = models.PositiveIntegerField(
        help_text="Order within the course"
    )
    duration_hours = models.PositiveIntegerField(
        help_text="Expected duration in hours"
    )
    is_required = models.BooleanField(
        default=True,
        help_text="Whether this module is required for course completion"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    history = HistoricalRecords()
    
    class Meta:
        ordering = ['course', 'order']
        unique_together = ['course', 'order']
        indexes = [
            models.Index(fields=['course', 'order']),
        ]

    def __str__(self):
        return f"{self.course.code} - Module {self.order}: {self.title}"

    def clean(self):
        """Validate module data."""
        if self.duration_hours > self.course.duration_hours:
            raise ValidationError(
                "Module duration cannot exceed course duration"
            )

class ContentType(models.TextChoices):
    """Types of lesson content."""
    VIDEO = 'VIDEO', _('Video')
    DOCUMENT = 'DOCUMENT', _('Document')
    PRESENTATION = 'PRESENTATION', _('Presentation')
    INTERACTIVE = 'INTERACTIVE', _('Interactive Content')
    EXTERNAL = 'EXTERNAL', _('External Resource')
    LIVE_SESSION = 'LIVE_SESSION', _('Live Session')

class Lesson(models.Model):
   """
   Individual lesson within a module.
   """
   id = models.UUIDField(
       primary_key=True,
       default=uuid.uuid4,
       editable=False
   )
   module = models.ForeignKey(
       Module,
       on_delete=models.CASCADE,
       related_name='lessons'
   )
   title = models.CharField(max_length=200)
   description = models.TextField()
   content_type = models.CharField(
       max_length=20,
       choices=ContentType.choices
   )
   content = models.JSONField(
       help_text="Lesson content and metadata"
   )
   order = models.PositiveIntegerField(
       help_text="Order within the module"
   )
   duration_minutes = models.PositiveIntegerField(
       help_text="Expected duration in minutes"
   )
   is_required = models.BooleanField(
       default=True,
       help_text="Whether this lesson is required for module completion"
   )
   
   created_at = models.DateTimeField(auto_now_add=True)
   updated_at = models.DateTimeField(auto_now=True)
   
   history = HistoricalRecords()
   
   class Meta:
       ordering = ['module', 'order']
       unique_together = ['module', 'order']
       indexes = [
           models.Index(fields=['module', 'order']),
           models.Index(fields=['content_type']),
       ]

   def __str__(self):
       return f"{self.module.course.code} - Module {self.module.order} - Lesson {self.order}: {self.title}"

   def clean(self):
       """Validate lesson content based on content_type."""
       super().clean()
       
       required_fields = {
           'VIDEO': ['url', 'duration'],
           'DOCUMENT': ['url', 'file_type'],
           'PRESENTATION': ['url', 'slide_count'],
           'INTERACTIVE': ['type', 'config'],
           'EXTERNAL': ['url', 'platform'],
           'LIVE_SESSION': ['session_id']
       }
       
       if self.content_type in required_fields:
           missing = [
               field for field in required_fields[self.content_type]
               if field not in self.content
           ]
           if missing:
               raise ValidationError(
                   f"Missing required fields for {self.content_type}: {missing}"
               )

       # Additional content-specific validation
       if self.content_type == 'VIDEO':
           if 'duration' in self.content and not isinstance(self.content['duration'], (int, float)):
               raise ValidationError("Video duration must be a number")
               
       elif self.content_type == 'PRESENTATION':
           if 'slide_count' in self.content and not isinstance(self.content['slide_count'], int):
               raise ValidationError("Slide count must be an integer")

       elif self.content_type == 'INTERACTIVE':
           valid_types = ['quiz', 'exercise', 'simulation']
           if 'type' in self.content and self.content['type'] not in valid_types:
               raise ValidationError(f"Interactive content type must be one of: {valid_types}")

   def save(self, *args, **kwargs):
       """Save with validation and tracking."""
       self.clean()  # Validate before saving
       
       is_new = not self.pk
       with transaction.atomic():
           super().save(*args, **kwargs)
           
           if is_new:
               # Track lesson creation
               UserActivity.objects.create(
                   user=self.module.course.created_by,
                   activity_type='LESSON_CREATION',
                   activity_detail={
                       'course_code': self.module.course.code,
                       'module_title': self.module.title,
                       'lesson_title': self.title,
                       'content_type': self.content_type
                   }
               )

   def get_progress_stats(self):
       """Get lesson progress statistics."""
       progress_records = self.progress_records.all()
       return {
           'total_attempts': progress_records.count(),
           'completed_count': progress_records.filter(
               status='COMPLETED'
           ).count(),
           'average_score': progress_records.filter(
               score__isnull=False
           ).aggregate(Avg('score'))['score__avg'],
           'average_time': progress_records.filter(
               time_spent__isnull=False
           ).aggregate(Avg('time_spent'))['time_spent__avg']
       }

   def duplicate(self, new_module=None, new_order=None):
       """Create a copy of this lesson."""
       lesson = Lesson.objects.get(pk=self.pk)
       lesson.pk = None  # Create new primary key
       
       if new_module:
           lesson.module = new_module
       if new_order:
           lesson.order = new_order
           
       lesson.save()
       return lesson

   def update_content(self, content_updates):
       """Safely update lesson content."""
       if not isinstance(content_updates, dict):
           raise ValueError("Content updates must be a dictionary")
           
       # Merge updates with existing content
       updated_content = {**self.content, **content_updates}
       
       # Validate before updating
       old_content = self.content
       self.content = updated_content
       try:
           self.clean()
       except ValidationError as e:
           self.content = old_content  # Restore old content
           raise e
           
       self.save()

class Assignment(models.Model):
    """
    Course assignments and assessments.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    instructions = models.TextField()
    due_days = models.PositiveIntegerField(
        help_text="Days to complete after assignment"
    )
    passing_score = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Minimum score to pass (percentage)"
    )
    max_attempts = models.PositiveIntegerField(
        default=1,
        help_text="Maximum number of attempts allowed"
    )
    weight = models.PositiveIntegerField(
        default=100,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Weight in course grade (percentage)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    history = HistoricalRecords()
    
    class Meta:
        ordering = ['course', 'created_at']
        indexes = [
            models.Index(fields=['course', 'created_at']),
        ]

    def __str__(self):
        return f"{self.course.code} - {self.title}"

class EnrollmentStatus(models.TextChoices):
    """Enrollment status choices."""
    PENDING = 'PENDING', _('Pending')
    APPROVED = 'APPROVED', _('Approved')
    IN_PROGRESS = 'IN_PROGRESS', _('In Progress')
    COMPLETED = 'COMPLETED', _('Completed')
    WITHDRAWN = 'WITHDRAWN', _('Withdrawn')
    FAILED = 'FAILED', _('Failed')

class Enrollment(models.Model):
    """
    Course enrollment and progress tracking.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    status = models.CharField(
        max_length=20,
        choices=EnrollmentStatus.choices,
        default=EnrollmentStatus.PENDING
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(
        null=True,
        blank=True
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )
    due_date = models.DateTimeField(
        null=True,
        blank=True
    )
    completion_percentage = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    grade = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    certificate_issued = models.BooleanField(default=False)
    certificate_issued_at = models.DateTimeField(
        null=True,
        blank=True
    )
    
    history = HistoricalRecords()
    
    class Meta:
        unique_together = ['user', 'course']
        ordering = ['-enrolled_at']
        indexes = [
            models.Index(fields=['user', 'course']),
            models.Index(fields=['status', 'enrolled_at']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.course.code} ({self.status})"

    def save(self, *args, **kwargs):
        """Enhanced save with status tracking."""
        is_new = not self.pk
        old_status = None
        
        if not is_new:
            old_status = Enrollment.objects.get(pk=self.pk).status
        
        # Update timestamps based on status
        if self.status == EnrollmentStatus.IN_PROGRESS and not self.started_at:
            self.started_at = timezone.now()
        elif self.status == EnrollmentStatus.COMPLETED and not self.completed_at:
            self.completed_at = timezone.now()
        
        with transaction.atomic():
            super().save(*args, **kwargs)
            
            # Track status changes
            if old_status and old_status != self.status:
                   UserActivity.objects.create(
                       user=self.user,
                       activity_type='ENROLLMENT_STATUS_CHANGE',
                       activity_detail={
                           'course_code': self.course.code,
                           'old_status': old_status,
                           'new_status': self.status,
                           'completion_percentage': self.completion_percentage
                       }
                   )
                   
                   # Handle completion
                   if self.status == EnrollmentStatus.COMPLETED:
                       # Record completion activity
                       UserActivity.objects.create(
                           user=self.user,
                           activity_type='COURSE_COMPLETION',
                           activity_detail={
                               'course_code': self.course.code,
                               'grade': self.grade,
                               'completion_time': (
                                   self.completed_at - self.started_at
                               ).days if self.started_at else None
                           }
                       )
                       
                       # Issue certificate if applicable
                       if (self.course.is_certificate_provided and 
                           not self.certificate_issued):
                           self.certificate_issued = True
                           self.certificate_issued_at = timezone.now()
                           self.save(update_fields=[
                               'certificate_issued',
                               'certificate_issued_at'
                           ])

class Progress(models.Model):
   """
   Detailed progress tracking for lessons and assignments.
   """
   id = models.UUIDField(
       primary_key=True,
       default=uuid.uuid4,
       editable=False
   )
   enrollment = models.ForeignKey(
       Enrollment,
       on_delete=models.CASCADE,
       related_name='progress_records'
   )
   lesson = models.ForeignKey(
       Lesson,
       on_delete=models.CASCADE,
       null=True,
       blank=True,
       related_name='progress_records'
   )
   assignment = models.ForeignKey(
       Assignment,
       on_delete=models.CASCADE,
       null=True,
       blank=True,
       related_name='progress_records'
   )
   status = models.CharField(
       max_length=20,
       choices=[
           ('NOT_STARTED', 'Not Started'),
           ('IN_PROGRESS', 'In Progress'),
           ('COMPLETED', 'Completed'),
           ('FAILED', 'Failed')
       ],
       default='NOT_STARTED'
   )
   progress_data = models.JSONField(
       default=dict,
       help_text="Detailed progress/interaction data"
   )
   score = models.PositiveIntegerField(
       null=True,
       blank=True,
       validators=[MinValueValidator(0), MaxValueValidator(100)]
   )
   attempt_count = models.PositiveIntegerField(default=0)
   time_spent = models.DurationField(
       default=timedelta,
       help_text="Total time spent"
   )
   last_interaction = models.DateTimeField(
       null=True,
       blank=True
   )
   completed_at = models.DateTimeField(
       null=True,
       blank=True
   )
   
   created_at = models.DateTimeField(auto_now_add=True)
   updated_at = models.DateTimeField(auto_now=True)
   
   history = HistoricalRecords()
   
   class Meta:
       ordering = ['enrollment', 'created_at']
       indexes = [
           models.Index(fields=['enrollment', 'status']),
           models.Index(fields=['lesson', 'status']),
           models.Index(fields=['assignment', 'status']),
       ]
       constraints = [
           models.CheckConstraint(
               check=(
                   models.Q(lesson__isnull=False, assignment__isnull=True) |
                   models.Q(lesson__isnull=True, assignment__isnull=False)
               ),
               name='either_lesson_or_assignment'
           )
       ]

   def __str__(self):
       target = self.lesson or self.assignment
       return f"{self.enrollment.user.email} - {target} ({self.status})"

   def save(self, *args, **kwargs):
       """Enhanced save with progress tracking."""
       # Update last interaction
       self.last_interaction = timezone.now()
       
       # Update completion timestamp if completed
       if self.status == 'COMPLETED' and not self.completed_at:
           self.completed_at = timezone.now()
       
       is_new = not self.pk
       with transaction.atomic():
           super().save(*args, **kwargs)
           
           if not is_new and self.status == 'COMPLETED':
               # Record completion activity
               activity_type = (
                   'LESSON_COMPLETION' if self.lesson 
                   else 'ASSIGNMENT_COMPLETION'
               )
               target = self.lesson or self.assignment
               
               UserActivity.objects.create(
                   user=self.enrollment.user,
                   activity_type=activity_type,
                   activity_detail={
                       'course_code': self.enrollment.course.code,
                       'title': target.title,
                       'score': self.score,
                       'attempt_count': self.attempt_count,
                       'time_spent': str(self.time_spent)
                   }
               )
               
               # Update enrollment progress
               self.update_enrollment_progress()

   def update_enrollment_progress(self):
       """Update overall enrollment progress."""
       enrollment = self.enrollment
       course = enrollment.course
       
       # Calculate progress percentage
       total_required = 0
       completed_required = 0
       
       # Count required lessons
       required_lessons = Lesson.objects.filter(
           module__course=course,
           is_required=True
       )
       total_required += required_lessons.count()
       completed_required += Progress.objects.filter(
           enrollment=enrollment,
           lesson__in=required_lessons,
           status='COMPLETED'
       ).count()
       
       # Count required assignments
       required_assignments = Assignment.objects.filter(
           course=course
       )
       total_required += required_assignments.count()
       completed_required += Progress.objects.filter(
           enrollment=enrollment,
           assignment__in=required_assignments,
           status='COMPLETED'
       ).count()
       
       # Calculate percentage
       if total_required > 0:
           progress = (completed_required / total_required) * 100
           enrollment.completion_percentage = min(int(progress), 100)
           
           # Check if course is completed
           if (enrollment.completion_percentage == 100 and
               enrollment.status != EnrollmentStatus.COMPLETED):
               enrollment.status = EnrollmentStatus.COMPLETED
           
           enrollment.save(update_fields=['completion_percentage', 'status'])

class LiveSession(models.Model):
   """
   Live training sessions for instructor-led courses.
   """
   id = models.UUIDField(
       primary_key=True,
       default=uuid.uuid4,
       editable=False
   )
   course = models.ForeignKey(
       Course,
       on_delete=models.CASCADE,
       related_name='live_sessions'
   )
   title = models.CharField(max_length=200)
   description = models.TextField()
   instructor = models.ForeignKey(
       User,
       on_delete=models.SET_NULL,
       null=True,
       related_name='teaching_sessions'
   )
   start_time = models.DateTimeField()
   end_time = models.DateTimeField()
   max_participants = models.PositiveIntegerField(
       null=True,
       blank=True
   )
   meeting_url = models.URLField(
       blank=True,
       help_text="URL for virtual session"
   )
   location = models.CharField(
       max_length=200,
       blank=True,
       help_text="Physical location if applicable"
   )
   materials = models.JSONField(
       default=list,
       help_text="Session materials and resources"
   )
   status = models.CharField(
       max_length=20,
       choices=[
           ('SCHEDULED', 'Scheduled'),
           ('IN_PROGRESS', 'In Progress'),
           ('COMPLETED', 'Completed'),
           ('CANCELLED', 'Cancelled')
       ],
       default='SCHEDULED'
   )
   
   created_at = models.DateTimeField(auto_now_add=True)
   updated_at = models.DateTimeField(auto_now=True)
   
   history = HistoricalRecords()
   
   class Meta:
       ordering = ['start_time']
       indexes = [
           models.Index(fields=['course', 'start_time']),
           models.Index(fields=['instructor', 'status']),
       ]

   def __str__(self):
       return f"{self.course.code} - {self.title} ({self.start_time})"

   def clean(self):
       """Validate session data."""
       if self.end_time <= self.start_time:
           raise ValidationError(
               "End time must be after start time"
           )
       
       if self.course.delivery_method not in [
           DeliveryMethod.INSTRUCTOR_LED,
           DeliveryMethod.BLENDED,
           DeliveryMethod.LIVE_ONLINE
       ]:
           raise ValidationError(
               "Live sessions are only for instructor-led courses"
           )

class SessionAttendance(models.Model):
   """
   Track attendance for live sessions.
   """
   id = models.UUIDField(
       primary_key=True,
       default=uuid.uuid4,
       editable=False
   )
   session = models.ForeignKey(
       LiveSession,
       on_delete=models.CASCADE,
       related_name='attendance_records'
   )
   user = models.ForeignKey(
       User,
       on_delete=models.CASCADE,
       related_name='session_attendance'
   )
   status = models.CharField(
       max_length=20,
       choices=[
           ('REGISTERED', 'Registered'),
           ('ATTENDED', 'Attended'),
           ('ABSENT', 'Absent'),
           ('EXCUSED', 'Excused')
       ],
       default='REGISTERED'
   )
   join_time = models.DateTimeField(null=True, blank=True)
   leave_time = models.DateTimeField(null=True, blank=True)
   attendance_duration = models.DurationField(
       null=True,
       blank=True,
       help_text="Total time attended"
   )
   feedback = models.TextField(blank=True)
   
   created_at = models.DateTimeField(auto_now_add=True)
   updated_at = models.DateTimeField(auto_now=True)
   
   class Meta:
       unique_together = ['session', 'user']
       ordering = ['session', 'user']
       indexes = [
           models.Index(fields=['session', 'status']),
           models.Index(fields=['user', 'status']),
       ]

   def __str__(self):
       return f"{self.user.email} - {self.session.title} ({self.status})"

   def save(self, *args, **kwargs):
       """Enhanced save with attendance tracking."""
       # Calculate attendance duration if applicable
       if self.join_time and self.leave_time:
           self.attendance_duration = self.leave_time - self.join_time
       
       with transaction.atomic():
           super().save(*args, **kwargs)
           
           # Record activity
           UserActivity.objects.create(
               user=self.user,
               activity_type='SESSION_ATTENDANCE',
               activity_detail={
                   'session_title': self.session.title,
                   'course_code': self.session.course.code,
                   'status': self.status,
                   'duration': str(self.attendance_duration) if self.attendance_duration else None
               }
           )