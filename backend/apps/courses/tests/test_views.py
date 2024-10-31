# apps/courses/tests/test_views.py

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from ..models import (
   Course, Module, Lesson, Assignment, Enrollment,
   Progress, LiveSession, CourseCategory, DifficultyLevel, 
   DeliveryMethod
)

User = get_user_model()

class CourseViewSetTest(APITestCase):
   def setUp(self):
       self.admin = User.objects.create_user(
           email='admin@example.com',
           password='testpass123',
           role='ADMIN'
       )
       self.instructor = User.objects.create_user(
           email='instructor@example.com',
           password='testpass123',
           role='TRAINER'
       )
       self.student = User.objects.create_user(
           email='student@example.com',
           password='testpass123'
       )
       self.course_data = {
           'title': 'Test Course',
           'code': 'TST101',
           'description': 'Test Description',
           'category': CourseCategory.TECHNICAL,
           'difficulty_level': DifficultyLevel.INTERMEDIATE,
           'delivery_method': DeliveryMethod.SELF_PACED,
           'duration_hours': 10
       }

   def test_course_list(self):
       self.client.force_authenticate(user=self.student)
       Course.objects.create(**self.course_data)
       url = reverse('course-list')
       response = self.client.get(url)
       self.assertEqual(response.status_code, status.HTTP_200_OK)
       self.assertEqual(len(response.data['results']), 1)

   def test_course_create(self):
       self.client.force_authenticate(user=self.admin)
       url = reverse('course-list')
       response = self.client.post(url, self.course_data)
       self.assertEqual(response.status_code, status.HTTP_201_CREATED)

   def test_course_enroll(self):
       self.client.force_authenticate(user=self.student)
       course = Course.objects.create(**self.course_data)
       url = reverse('course-enroll', kwargs={'pk': course.pk})
       response = self.client.post(url)
       self.assertEqual(response.status_code, status.HTTP_201_CREATED)

class EnrollmentViewSetTest(APITestCase):
   def setUp(self):
       self.student = User.objects.create_user(
           email='student@example.com',
           password='testpass123'
       )
       self.course = Course.objects.create(
           title='Test Course',
           code='TST101',
           category=CourseCategory.TECHNICAL,
           difficulty_level=DifficultyLevel.INTERMEDIATE,
           duration_hours=10
       )

   def test_enrollment_list(self):
       self.client.force_authenticate(user=self.student)
       Enrollment.objects.create(user=self.student, course=self.course)
       url = reverse('enrollment-list')
       response = self.client.get(url)
       self.assertEqual(response.status_code, status.HTTP_200_OK)
       self.assertEqual(len(response.data['results']), 1)

   def test_enrollment_progress(self):
       self.client.force_authenticate(user=self.student)
       enrollment = Enrollment.objects.create(
           user=self.student, 
           course=self.course,
           status='IN_PROGRESS'
       )
       url = reverse('enrollment-progress', kwargs={'pk': enrollment.pk})
       response = self.client.get(url)
       self.assertEqual(response.status_code, status.HTTP_200_OK)

