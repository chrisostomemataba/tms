# apps/courses/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from . import views

# Main router
router = DefaultRouter()
router.register(r'courses', views.CourseViewSet, basename='course')
router.register(r'enrollments', views.EnrollmentViewSet, basename='enrollment')

# Nested routers
courses_router = routers.NestedDefaultRouter(router, r'courses', lookup='course')
courses_router.register(r'modules', views.ModuleViewSet, basename='course-module')
courses_router.register(r'assignments', views.AssignmentViewSet, basename='course-assignment')
courses_router.register(r'live-sessions', views.LiveSessionViewSet, basename='course-session')

# Module nested router
modules_router = routers.NestedDefaultRouter(courses_router, r'modules', lookup='module')
modules_router.register(r'lessons', views.LessonViewSet, basename='module-lesson')

# Live session nested router 
sessions_router = routers.NestedDefaultRouter(courses_router, r'live-sessions', lookup='session')
sessions_router.register(r'attendance', views.SessionAttendanceViewSet, basename='session-attendance')

# Enrollment progress router
enrollments_router = routers.NestedDefaultRouter(router, r'enrollments', lookup='enrollment')
enrollments_router.register(r'progress', views.ProgressViewSet, basename='enrollment-progress')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(courses_router.urls)),
    path('', include(modules_router.urls)),
    path('', include(sessions_router.urls)),
    path('', include(enrollments_router.urls)),
]