# apps/users/tests/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView
from apps.users import views

# Create router for test endpoints
router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')

# Test URL patterns
urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/', TokenObtainPairView.as_view(), name='token-obtain'),
    path('auth/register/', views.UserRegistrationView.as_view(), name='user-registration'),
    path(
        'profile/me/',
        views.CurrentUserProfileView.as_view(),
        name='current-user-profile'
    ),
]