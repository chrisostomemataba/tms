
# apps/users/views.py

from rest_framework import viewsets, status, filters, generics  # Added generics here
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from django.db.models import Q, Count, Sum
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import (
    UserSerializer, UserProfileSerializer, UserRegistrationSerializer,
    UserActivitySerializer, SkillSerializer, UserSkillSerializer,
    TrainingPreferenceSerializer, AchievementSerializer,
    UserAchievementSerializer
)
from .models import (
    UserProfile, UserActivity, Skill, UserSkill,
    TrainingPreference, Achievement, UserAchievement,
    UserRole
)
from .permissions import (
    IsAdminUser, IsOwnerOrAdmin, IsTrainerOrAdmin,
    CanVerifySkills, CanAwardAchievements
)
from .filters import UserFilter, SkillFilter, AchievementFilter
import jwt
from django.conf import settings
from datetime import datetime, timedelta

User = get_user_model()

# apps/users/views.py - Add these new classes

class CurrentUserView(generics.RetrieveUpdateAPIView):
    """View for retrieving/updating the current user."""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class CurrentUserProfileView(generics.RetrieveUpdateAPIView):
    """View for retrieving/updating the current user's profile."""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile

# Add these test-specific views if DEBUG is True
if settings.DEBUG:
    class DevResetPasswordView(APIView):
        permission_classes = [IsAuthenticated, IsAdminUser]
        
        def post(self, request, user_id):
            try:
                user = User.objects.get(id=user_id)
                new_password = request.data.get('password')
                user.set_password(new_password)
                user.save()
                return Response({'status': 'password reset'})
            except User.DoesNotExist:
                return Response(
                    {'error': 'User not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )

    class DevGenerateTestDataView(APIView):
        permission_classes = [IsAuthenticated, IsAdminUser]
        
        def post(self, request):
            try:
                # Generate test data logic here
                return Response({'status': 'test data generated'})
            except Exception as e:
                return Response(
                    {'error': str(e)}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

class CustomPagination(PageNumberPagination):
    """Custom pagination with flexible page size."""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User model with advanced filtering and actions.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = UserFilter
    search_fields = ['email', 'first_name', 'last_name', 'profile__department']
    ordering_fields = ['created_at', 'last_active', 'email']

    def get_permissions(self):
        if self.action in ['create', 'reset_password_request']:
            return [AllowAny()]
        if self.action in ['list', 'bulk_deactivate']:
            return [IsAdminUser()]
        return [IsOwnerOrAdmin()]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'list' and not self.request.user.is_staff:
            return queryset.filter(id=self.request.user.id)
        return queryset

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Get current user's details."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser])
    def bulk_deactivate(self, request):
        """Bulk deactivate users."""
        user_ids = request.data.get('user_ids', [])
        reason = request.data.get('reason', '')
        
        User.objects.filter(id__in=user_ids).update(
            is_active=False,
            deactivated_at=timezone.now(),
            deactivation_reason=reason
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def change_password(self, request, pk=None):
        """Change user password."""
        user = self.get_object()
        if not user.check_password(request.data.get('current_password')):
            return Response(
                {'error': 'Current password is incorrect'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        user.set_password(request.data.get('new_password'))
        user.password_changed_at = timezone.now()
        user.save()
        
        UserActivity.objects.create(
            user=user,
            activity_type='PASSWORD_CHANGE',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        return Response(status=status.HTTP_204_NO_CONTENT)

class UserRegistrationView(APIView):
    """Handle user registration with profile creation."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Record activity
            UserActivity.objects.create(
                user=user,
                activity_type='REGISTRATION',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            # Generate tokens
            tokens = user.generate_tokens()
            
            return Response({
                'user': UserSerializer(user).data,
                'tokens': tokens
            }, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for UserProfile model with nested relationships.
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            return queryset.filter(user=self.request.user)
        return queryset

    @action(detail=True, methods=['post'])
    def upload_avatar(self, request, pk=None):
        """Handle avatar upload."""
        profile = self.get_object()
        if 'avatar' not in request.FILES:
            return Response(
                {'error': 'No avatar file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        profile.avatar = request.FILES['avatar']
        profile.save()
        
        return Response(
            UserProfileSerializer(profile).data,
            status=status.HTTP_200_OK
        )

class SkillViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Skill model with filtering and verification.
    """
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = SkillFilter
    search_fields = ['name', 'category', 'description']

    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [IsTrainerOrAdmin()]
        return [IsAuthenticated()]

class UserSkillViewSet(viewsets.ModelViewSet):
    """
    ViewSet for UserSkill model with verification functionality.
    """
    queryset = UserSkill.objects.all()
    serializer_class = UserSkillSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            return queryset.filter(user_profile__user=self.request.user)
        return queryset

    @action(detail=True, methods=['post'], permission_classes=[CanVerifySkills])
    def verify_skill(self, request, pk=None):
        """Verify a user's skill."""
        skill = self.get_object()
        skill.verify(request.user)
        
        # Record activity
        UserActivity.objects.create(
            user=skill.user_profile.user,
            activity_type='SKILL_VERIFICATION',
            activity_detail={
                'skill': skill.skill.name,
                'verified_by': request.user.email
            }
        )
        
        return Response(
            UserSkillSerializer(skill).data,
            status=status.HTTP_200_OK
        )

class AchievementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Achievement model with awarding functionality.
    """
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = AchievementFilter
    search_fields = ['name', 'category', 'description']

    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    @action(detail=True, methods=['post'], permission_classes=[CanAwardAchievements])
    def award(self, request, pk=None):
        """Award achievement to a user."""
        achievement = self.get_object()
        user_id = request.data.get('user_id')
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if already awarded
        if UserAchievement.objects.filter(
            user=user,
            achievement=achievement
        ).exists():
            return Response(
                {'error': 'Achievement already awarded to this user'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user_achievement = UserAchievement.objects.create(
            user=user,
            achievement=achievement,
            awarded_by=request.user,
            evidence=request.data.get('evidence', {})
        )

        # Record activity
        UserActivity.objects.create(
            user=user,
            activity_type='ACHIEVEMENT',
            activity_detail={
                'achievement': achievement.name,
                'awarded_by': request.user.email
            }
        )

        return Response(
            UserAchievementSerializer(user_achievement).data,
            status=status.HTTP_201_CREATED
        )

class UserActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for UserActivity model with filtering and analytics.
    """
    queryset = UserActivity.objects.all()
    serializer_class = UserActivitySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['created_at', 'activity_type']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            return queryset.filter(user=self.request.user)
        return queryset

    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get activity analytics."""
        queryset = self.get_queryset()
        
        # Get date range from query params
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)

        analytics = {
            'total_activities': queryset.count(),
            'activities_by_type': queryset.values('activity_type')
                .annotate(count=Count('id')),
            'activities_by_day': queryset
                .values('created_at__date')
                .annotate(count=Count('id'))
                .order_by('created_at__date')
        }

        return Response(analytics)
# Add to the end of views.py

class UserPreferencesView(generics.RetrieveUpdateAPIView):
    """Handle user training preferences."""
    serializer_class = TrainingPreferenceSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile.training_preferences

class SkillCategoriesView(APIView):
    """Get available skill categories."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        categories = Skill.objects.values_list('category', flat=True).distinct()
        return Response({'categories': list(categories)})

class VerifyUserSkillView(APIView):
    """Handle skill verification."""
    permission_classes = [IsAuthenticated, CanVerifySkills]

    def post(self, request, skill_id, user_id):
        try:
            skill = UserSkill.objects.get(
                skill_id=skill_id,
                user_profile__user_id=user_id
            )
            skill.verify(request.user)
            return Response(
                UserSkillSerializer(skill).data,
                status=status.HTTP_200_OK
            )
        except UserSkill.DoesNotExist:
            return Response(
                {'error': 'Skill not found'},
                status=status.HTTP_404_NOT_FOUND
            )

class AwardAchievementView(APIView):
    """Award achievements to users."""
    permission_classes = [IsAuthenticated, CanAwardAchievements]

    def post(self, request):
        achievement_id = request.data.get('achievement_id')
        user_id = request.data.get('user_id')
        
        try:
            achievement = Achievement.objects.get(id=achievement_id)
            user = User.objects.get(id=user_id)
            
            user_achievement = UserAchievement.objects.create(
                user=user,
                achievement=achievement,
                awarded_by=request.user,
                evidence=request.data.get('evidence', {})
            )
            
            return Response(
                UserAchievementSerializer(user_achievement).data,
                status=status.HTTP_201_CREATED
            )
        except (Achievement.DoesNotExist, User.DoesNotExist):
            return Response(
                {'error': 'Achievement or user not found'},
                status=status.HTTP_404_NOT_FOUND
            )

class AchievementCategoriesView(APIView):
    """Get available achievement categories."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        categories = Achievement.objects.values_list('category', flat=True).distinct()
        return Response({'categories': list(categories)})

class ActivityAnalyticsView(APIView):
    """Detailed analytics for user activities."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        activities = UserActivity.objects.all()
        
        if not request.user.is_staff:
            activities = activities.filter(user=request.user)

        analytics = {
            'total_activities': activities.count(),
            'by_type': activities.values('activity_type')
                .annotate(count=Count('id')),
            'user_stats': activities.values('user__email')
                .annotate(activity_count=Count('id'))
                .order_by('-activity_count')
        }
        
        return Response(analytics)

class ExportActivitiesView(APIView):
    """Export user activities."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        activities = UserActivity.objects.all().select_related('user')
        
        data = []
        for activity in activities:
            data.append({
                'user': activity.user.email,
                'type': activity.activity_type,
                'timestamp': activity.created_at,
                'details': activity.activity_detail
            })
            
        return Response(data)

class BulkDeactivateUsersView(APIView):
    """Bulk deactivate users."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        user_ids = request.data.get('user_ids', [])
        reason = request.data.get('reason', '')
        
        updated = User.objects.filter(id__in=user_ids).update(
            is_active=False,
            deactivated_at=timezone.now(),
            deactivation_reason=reason
        )
        
        return Response({'deactivated_count': updated})

class BulkChangeUserRoleView(APIView):
    """Bulk change user roles."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        user_ids = request.data.get('user_ids', [])
        new_role = request.data.get('role')
        
        if new_role not in dict(UserRole.choices):
            return Response(
                {'error': 'Invalid role'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        updated = User.objects.filter(id__in=user_ids).update(role=new_role)
        return Response({'updated_count': updated})

class UserProgressReportView(APIView):
    """Generate user progress reports."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        users = User.objects.all()
        
        report = []
        for user in users:
            report.append({
                'user': user.email,
                'skills_count': user.profile.skills.count(),
                'verified_skills': user.profile.skills.filter(verified=True).count(),
                'achievements': user.achievements.count()
            })
            
        return Response(report)

class SkillMatrixReportView(APIView):
    """Generate skill matrix report."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        skills = Skill.objects.all()
        
        matrix = []
        for skill in skills:
            matrix.append({
                'skill': skill.name,
                'total_users': skill.user_skills.count(),
                'verified_users': skill.user_skills.filter(verified=True).count(),
                'by_level': skill.user_skills.values('proficiency_level')
                    .annotate(count=Count('id'))
            })
            
        return Response(matrix)

class AchievementStatisticsView(APIView):
    """Generate achievement statistics."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        achievements = Achievement.objects.all()
        
        stats = []
        for achievement in achievements:
            stats.append({
                'achievement': achievement.name,
                'awarded_count': achievement.userachievement_set.count(),
                'total_points': achievement.points * achievement.userachievement_set.count()
            })
            
        return Response(stats)

class UserAuditView(APIView):
    """User audit trail."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        user_id = request.query_params.get('user_id')
        
        activities = UserActivity.objects.all()
        if user_id:
            activities = activities.filter(user_id=user_id)
            
        audit_trail = activities.values(
            'user__email',
            'activity_type',
            'created_at',
            'activity_detail'
        ).order_by('-created_at')
        
        return Response(list(audit_trail))

class SystemAnalyticsView(APIView):
    """System-wide analytics."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        analytics = {
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'total_skills': Skill.objects.count(),
            'total_achievements': Achievement.objects.count(),
            'user_roles': User.objects.values('role')
                .annotate(count=Count('id')),
            'activities_last_30_days': UserActivity.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=30)
            ).count()
        }
        
        return Response(analytics)