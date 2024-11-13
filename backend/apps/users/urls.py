# apps/users/urls.py
from django.conf import settings  # Add this at the top with other import

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from . import views

# Create main router
router = DefaultRouter()
router.default_renderer_classes = [JSONRenderer, BrowsableAPIRenderer]

# Auth URLs
auth_urlpatterns = [
    path('auth/register/', views.UserRegistrationView.as_view(), name='register'),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]

# Main routes
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'skills', views.SkillViewSet, basename='skill')
router.register(r'achievements', views.AchievementViewSet, basename='achievement')
router.register(r'activities', views.UserActivityViewSet, basename='activity')

# Create nested routers for related resources
users_router = routers.NestedDefaultRouter(router, r'users', lookup='user')
users_router.register(
    r'profiles',
    views.UserProfileViewSet,
    basename='user-profile'
)
users_router.register(
    r'skills',
    views.UserSkillViewSet,
    basename='user-skill'
)
users_router.register(
    r'activities',
    views.UserActivityViewSet,
    basename='user-activity'
)

# Combine all URLs
urlpatterns = auth_urlpatterns + router.urls + users_router.urls

# Profile management
urlpatterns += [
    path(
        'profile/me/',
        views.CurrentUserProfileView.as_view(),
        name='current-user-profile'
    ),
    path(
        'profile/me/preferences/',
        views.UserPreferencesView.as_view(),
        name='user-preferences'
    ),
    
    # Skill management
    path(
        'skills/<uuid:skill_id>/verify/<uuid:user_id>/',
        views.VerifyUserSkillView.as_view(),
        name='verify-user-skill'
    ),
    path(
        'skills/categories/',
        views.SkillCategoriesView.as_view(),
        name='skill-categories'
    ),
    
    # Achievement management
    path(
        'achievements/award/',
        views.AwardAchievementView.as_view(),
        name='award-achievement'
    ),
    path(
        'achievements/categories/',
        views.AchievementCategoriesView.as_view(),
        name='achievement-categories'
    ),
    
    # Activity tracking
    path(
        'activities/analytics/',
        views.ActivityAnalyticsView.as_view(),
        name='activity-analytics'
    ),
    path(
        'activities/export/',
        views.ExportActivitiesView.as_view(),
        name='export-activities'
    ),
    
    # User management
    path(
        'users/bulk-actions/deactivate/',
        views.BulkDeactivateUsersView.as_view(),
        name='bulk-deactivate-users'
    ),
    path(
        'users/bulk-actions/change-role/',
        views.BulkChangeUserRoleView.as_view(),
        name='bulk-change-user-role'
    ),
    
    # Reports and analytics
    path(
        'reports/user-progress/',
        views.UserProgressReportView.as_view(),
        name='user-progress-report'
    ),
    path(
        'reports/skill-matrix/',
        views.SkillMatrixReportView.as_view(),
        name='skill-matrix-report'
    ),
    path(
        'reports/achievement-statistics/',
        views.AchievementStatisticsView.as_view(),
        name='achievement-statistics'
    ),
    
    # Admin specific endpoints
    path(
        'admin/user-audit/',
        views.UserAuditView.as_view(),
        name='user-audit'
    ),
    path(
        'admin/system-analytics/',
        views.SystemAnalyticsView.as_view(),
        name='system-analytics'
    ),
]

# Add format suffix patterns if needed

# Test/Development endpoints
if settings.DEBUG:
    urlpatterns += [
        path(
            'dev/reset-password/<uuid:user_id>/',
            views.DevResetPasswordView.as_view(),
            name='dev-reset-password'
        ),
        path(
            'dev/generate-test-data/',
            views.DevGenerateTestDataView.as_view(),
            name='dev-generate-test-data'
        ),
        # Authentication endpoints section
    path(
        'auth/token/verify/',
        TokenVerifyView.as_view(),
        name='token_verify'
    ),

    # Add this new path here
    path(
        'users/me/',  
        views.CurrentUserView.as_view(),
        name='current-user'  # This matches the name used in the test
    ),
    ]