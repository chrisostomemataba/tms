# apps/courses/tests/test_models.py

from django.test import TestCase, TransactionTestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta

from ..models import (
    Course, Module, Lesson, Assignment, Enrollment,
    Progress, LiveSession, SessionAttendance,
    CourseCategory, DifficultyLevel, DeliveryMethod
)
from apps.users.models import UserRole, Skill

User = get_user_model()

class CourseModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(
            email='admin@example.com',
            password='testpass123',
            role=UserRole.ADMIN
        )
        cls.instructor = User.objects.create_user(
            email='instructor@example.com',
            password='testpass123',
            role=UserRole.TRAINER
        )
        cls.skill = Skill.objects.create(
            name='Python',
            category='Programming',
            level_criteria={
                'BEGINNER': 'Basic',
                'INTERMEDIATE': 'Advanced',
                'ADVANCED': 'Expert',
                'EXPERT': 'Master'
            }
        )
        cls.course_data = {
            'title': 'Test Course',
            'code': 'TST101',
            'description': 'Test Description',
            'category': CourseCategory.TECHNICAL,
            'difficulty_level': DifficultyLevel.INTERMEDIATE,
            'delivery_method': DeliveryMethod.SELF_PACED,
            'duration_hours': 10,
            'created_by': cls.admin
        }

def test_course_creation(self):
    course_data = self.course_data.copy()
    course_data['delivery_method'] = DeliveryMethod.SELF_PACED  # Change to SELF_PACED
    course = Course.objects.create(**course_data)
    self.assertEqual(course.title, self.course_data['title'])
    self.assertTrue(course.is_active)
    self.assertEqual(course.created_by, self.admin)

    def test_course_validation(self):
        # Test instructor requirement
        course_data = self.course_data.copy()
        course_data['delivery_method'] = DeliveryMethod.INSTRUCTOR_LED
        
        course = Course.objects.create(**course_data)
        with self.assertRaises(ValidationError):
            course.clean()

    def test_course_relationships(self):
        course = Course.objects.create(**self.course_data)
        course.instructors.add(self.instructor)
        course.required_skills.add(self.skill)
        
        self.assertIn(self.instructor, course.instructors.all())
        self.assertIn(self.skill, course.required_skills.all())

class ModuleTest(TestCase):
    def setUp(self):
        self.course = Course.objects.create(
            title='Test Course',
            code='TST101',
            category=CourseCategory.TECHNICAL,
            difficulty_level=DifficultyLevel.INTERMEDIATE,
            delivery_method=DeliveryMethod.SELF_PACED,
            duration_hours=10
        )

    def test_module_creation(self):
        module = Module.objects.create(
            course=self.course,
            title='Test Module',
            description='Test Description',
            order=1,
            duration_hours=5
        )
        self.assertEqual(module.course, self.course)
        self.assertEqual(module.order, 1)

    def test_module_ordering(self):
        Module.objects.create(
            course=self.course,
            title='Module 1',
            order=1,
            duration_hours=2
        )
        Module.objects.create(
            course=self.course,
            title='Module 2',
            order=2,
            duration_hours=3
        )
        
        modules = Module.objects.filter(course=self.course)
        self.assertEqual(modules[0].title, 'Module 1')
        self.assertEqual(modules[1].title, 'Module 2')

class LessonTest(TestCase):
    def setUp(self):
        self.course = Course.objects.create(
            title='Test Course',
            code='TST101',
            category=CourseCategory.TECHNICAL,
            duration_hours=10
        )
        self.module = Module.objects.create(
            course=self.course,
            title='Test Module',
            order=1,
            duration_hours=5
        )

    def test_lesson_creation(self):
        lesson = Lesson.objects.create(
            module=self.module,
            title='Test Lesson',
            description='Test Description',
            content_type='VIDEO',
            content={'url': 'test.com/video'},
            order=1,
            duration_minutes=30
        )
        self.assertEqual(lesson.module, self.module)
        self.assertEqual(lesson.content_type, 'VIDEO')

    def test_content_validation(self):
        with self.assertRaises(ValidationError):
            Lesson.objects.create(
                module=self.module,
                title='Invalid Lesson',
                content_type='VIDEO',
                content={},  # Missing required fields
                order=1,
                duration_minutes=30
            )

class EnrollmentTest(TransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='student@example.com',
            password='testpass123'
        )
        self.course = Course.objects.create(
            title='Test Course',
            code='TST101',
            category=CourseCategory.TECHNICAL,
            duration_hours=10
        )

    def test_enrollment_lifecycle(self):
        enrollment = Enrollment.objects.create(
            user=self.user,
            course=self.course
        )
        
        # Test initial state
        self.assertEqual(enrollment.status, 'PENDING')
        self.assertIsNone(enrollment.started_at)
        
        # Test progress
        enrollment.status = 'IN_PROGRESS'
        enrollment.save()
        self.assertIsNotNone(enrollment.started_at)
        
        # Test completion
        enrollment.status = 'COMPLETED'
        enrollment.save()
        self.assertIsNotNone(enrollment.completed_at)

    def test_progress_tracking(self):
        enrollment = Enrollment.objects.create(
            user=self.user,
            course=self.course,
            status='IN_PROGRESS'
        )
        
        module = Module.objects.create(
            course=self.course,
            title='Test Module',
            order=1,
            duration_hours=5
        )
        
        lesson = Lesson.objects.create(
            module=module,
            title='Test Lesson',
            content_type='VIDEO',
            content={'url': 'test.com'},
            order=1,
            duration_minutes=30
        )
        
        # Create progress record
        Progress.objects.create(
            enrollment=enrollment,
            lesson=lesson,
            status='COMPLETED',
            score=85
        )
        
        self.assertGreater(enrollment.completion_percentage, 0)

class LiveSessionTest(TestCase):
    def setUp(self):
        self.instructor = User.objects.create_user(
            email='instructor@example.com',
            password='testpass123',
            role=UserRole.TRAINER
        )
        self.course = Course.objects.create(
            title='Test Course',
            code='TST101',
            category=CourseCategory.TECHNICAL,
            delivery_method=DeliveryMethod.INSTRUCTOR_LED,
            duration_hours=10
        )
        self.course.instructors.add(self.instructor)

    def test_session_scheduling(self):
        start_time = timezone.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=2)
        
        session = LiveSession.objects.create(
            course=self.course,
            title='Test Session',
            instructor=self.instructor,
            start_time=start_time,
            end_time=end_time
        )
        
        self.assertEqual(session.status, 'SCHEDULED')
        self.assertEqual(session.instructor, self.instructor)

    def test_attendance_tracking(self):
        start_time = timezone.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=2)
        
        session = LiveSession.objects.create(
            course=self.course,
            title='Test Session',
            instructor=self.instructor,
            start_time=start_time,
            end_time=end_time
        )
        
        student = User.objects.create_user(
            email='student@example.com',
            password='testpass123'
        )
        
        attendance = SessionAttendance.objects.create(
            session=session,
            user=student,
            status='REGISTERED'
        )
        
        # Test attendance update
        attendance.status = 'ATTENDED'
        attendance.join_time = timezone.now()
        attendance.save()
        
        self.assertEqual(attendance.status, 'ATTENDED')
        self.assertIsNotNone(attendance.join_time)