# apps/courses/views.py

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Avg
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import (
    Course, Module, Lesson, Assignment, Enrollment,
    Progress, LiveSession, SessionAttendance
)
from .serializers import (
    CourseSerializer, ModuleSerializer, LessonSerializer,
    AssignmentSerializer, EnrollmentSerializer, ProgressSerializer,
    LiveSessionSerializer, SessionAttendanceSerializer
)
from .permissions import (
    IsInstructorOrAdmin, CanEnrollCourse, CanManageCourse,
    CanAccessCourseContent
)
from .filters import (
    CourseFilter, EnrollmentFilter, ProgressFilter,
    LiveSessionFilter
)
from apps.users.models import UserActivity

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = CourseFilter
    search_fields = ['title', 'code', 'description']
    ordering_fields = ['created_at', 'title']

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
        return queryset.annotate(enrollment_count=Count('enrollments'))

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsInstructorOrAdmin()]
        return super().get_permissions()

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        course = self.get_object()
        course.published_at = timezone.now()
        course.save()
        return Response({'status': 'published'})

    @action(detail=True, methods=['post'])
    def enroll(self, request, pk=None):
        course = self.get_object()
        user = request.user
        
        if course.max_participants and \
           course.enrollments.count() >= course.max_participants:
            return Response(
                {'error': 'Course is full'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        enrollment = Enrollment.objects.create(
            user=user,
            course=course,
            status='APPROVED' if course.auto_enrollment else 'PENDING'
        )
        
        return Response(
            EnrollmentSerializer(enrollment).data,
            status=status.HTTP_201_CREATED
        )

class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticated, CanManageCourse]

    def get_queryset(self):
        return super().get_queryset().filter(
            course_id=self.kwargs['course_pk']
        ).annotate(
            lesson_count=Count('lessons')
        )

class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, CanManageCourse]

    def get_queryset(self):
        return super().get_queryset().filter(
            module_id=self.kwargs['module_pk'],
            module__course_id=self.kwargs['course_pk']
        )

class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [IsAuthenticated, CanManageCourse]

    def get_queryset(self):
        return super().get_queryset().filter(
            course_id=self.kwargs['course_pk']
        )

class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = EnrollmentFilter
    ordering_fields = ['enrolled_at', 'completion_percentage']

    def get_queryset(self):
        if self.request.user.is_staff:
            return super().get_queryset()
        return super().get_queryset().filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        enrollment = self.get_object()
        enrollment.status = 'IN_PROGRESS'
        enrollment.started_at = timezone.now()
        enrollment.save()
        return Response({'status': 'started'})

class ProgressViewSet(viewsets.ModelViewSet):
    queryset = Progress.objects.all()
    serializer_class = ProgressSerializer
    permission_classes = [IsAuthenticated, CanAccessCourseContent]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ProgressFilter
    ordering_fields = ['created_at', 'last_interaction']

    def get_queryset(self):
        return super().get_queryset().filter(
            enrollment_id=self.kwargs['enrollment_pk']
        )

    def perform_create(self, serializer):
        enrollment = get_object_or_404(
            Enrollment,
            id=self.kwargs['enrollment_pk']
        )
        serializer.save(enrollment=enrollment)

class LiveSessionViewSet(viewsets.ModelViewSet):
    queryset = LiveSession.objects.all()
    serializer_class = LiveSessionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = LiveSessionFilter
    ordering_fields = ['start_time']

    def get_queryset(self):
        return super().get_queryset().filter(
            course_id=self.kwargs['course_pk']
        ).annotate(
            attendance_count=Count('attendance_records')
        )

class SessionAttendanceViewSet(viewsets.ModelViewSet):
    queryset = SessionAttendance.objects.all()
    serializer_class = SessionAttendanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return super().get_queryset().filter(
                session_id=self.kwargs['session_pk']
            )
        return super().get_queryset().filter(
            session_id=self.kwargs['session_pk'],
            user=self.request.user
        )

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        attendance = self.get_object()
        attendance.status = 'ATTENDED'
        attendance.join_time = timezone.now()
        attendance.save()
        return Response({'status': 'joined'})

    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        attendance = self.get_object()
        attendance.leave_time = timezone.now()
        attendance.save()
        return Response({'status': 'left'})