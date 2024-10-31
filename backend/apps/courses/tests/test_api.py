# apps/courses/tests/test_api.py

class CourseAPITest(APITestCase):
   def setUp(self):
       self.admin = User.objects.create_user(
           email='admin@example.com',
           password='testpass123',
           role='ADMIN'
       )
       self.course_data = {
           'title': 'API Test Course',
           'code': 'API101',
           'description': 'API Test Description',
           'category': CourseCategory.TECHNICAL,
           'difficulty_level': DifficultyLevel.BEGINNER,
           'delivery_method': DeliveryMethod.SELF_PACED,
           'duration_hours': 5
       }

   def test_course_crud(self):
       self.client.force_authenticate(user=self.admin)
       
       # Create
       url = reverse('course-list')
       response = self.client.post(url, self.course_data)
       self.assertEqual(response.status_code, status.HTTP_201_CREATED)
       course_id = response.data['id']
       
       # Read
       url = reverse('course-detail', kwargs={'pk': course_id})
       response = self.client.get(url)
       self.assertEqual(response.status_code, status.HTTP_200_OK)
       
       # Update
       update_data = {'title': 'Updated Course'}
       response = self.client.patch(url, update_data)
       self.assertEqual(response.status_code, status.HTTP_200_OK)
       self.assertEqual(response.data['title'], 'Updated Course')
       
       # Delete
       response = self.client.delete(url)
       self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

class ModuleAPITest(APITestCase):
   def setUp(self):
       self.instructor = User.objects.create_user(
           email='instructor@example.com',
           password='testpass123',
           role='TRAINER'
       )
       self.course = Course.objects.create(
           title='Test Course',
           code='TST101',
           category=CourseCategory.TECHNICAL,
           duration_hours=10
       )

   def test_module_operations(self):
       self.client.force_authenticate(user=self.instructor)
       
       # Create module
       url = reverse('course-module-list', kwargs={'course_pk': self.course.pk})
       data = {
           'title': 'Test Module',
           'description': 'Test Description',
           'order': 1,
           'duration_hours': 2
       }
       response = self.client.post(url, data)
       self.assertEqual(response.status_code, status.HTTP_201_CREATED)