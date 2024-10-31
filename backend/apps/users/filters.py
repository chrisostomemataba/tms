# apps/users/filters.py

import django_filters
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from django_filters import rest_framework as filters
from .models import (
    User, UserProfile, Skill, UserSkill,
    Achievement, UserAchievement, UserActivity,
    UserRole
)

class UserFilter(django_filters.FilterSet):
    """
    Advanced filter for User model with complex filtering options.
    """
    email = django_filters.CharFilter(lookup_expr='icontains')
    full_name = django_filters.CharFilter(method='filter_full_name')
    role = django_filters.ChoiceFilter(choices=UserRole.choices)
    department = django_filters.CharFilter(
        field_name='profile__department',
        lookup_expr='icontains'
    )
    skills = django_filters.ModelMultipleChoiceFilter(
        field_name='profile__skills__skill',
        queryset=Skill.objects.all(),
        conjoined=True  # User must have ALL specified skills
    )
    created_after = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte'
    )
    created_before = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte'
    )
    is_active = django_filters.BooleanFilter()
    last_active_after = django_filters.DateTimeFilter(
        field_name='last_active',
        lookup_expr='gte'
    )
    inactive_duration = django_filters.NumberFilter(method='filter_inactive_duration')
    has_achievements = django_filters.BooleanFilter(
        method='filter_has_achievements'
    )
    min_achievements = django_filters.NumberFilter(
        method='filter_min_achievements'
    )
    verified_skills_count = django_filters.NumberFilter(
        method='filter_verified_skills_count'
    )

    class Meta:
        model = User
        fields = [
            'email', 'role', 'is_active', 'department',
            'skills', 'created_after', 'created_before'
        ]

    def filter_full_name(self, queryset, name, value):
        """Filter by full name (first name + last name)."""
        for term in value.split():
            queryset = queryset.filter(
                Q(first_name__icontains=term) |
                Q(last_name__icontains=term)
            )
        return queryset

    def filter_inactive_duration(self, queryset, name, value):
        """Filter users inactive for specified number of days."""
        cutoff_date = timezone.now() - timedelta(days=value)
        return queryset.filter(last_active__lt=cutoff_date)

    def filter_has_achievements(self, queryset, name, value):
        """Filter users based on whether they have any achievements."""
        if value:
            return queryset.filter(achievements__isnull=False).distinct()
        return queryset.filter(achievements__isnull=True)

    def filter_min_achievements(self, queryset, name, value):
        """Filter users with minimum number of achievements."""
        return queryset.annotate(
            achievement_count=django_filters.Count('achievements')
        ).filter(achievement_count__gte=value)

    def filter_verified_skills_count(self, queryset, name, value):
        """Filter users by number of verified skills."""
        return queryset.annotate(
            verified_skills=django_filters.Count(
                'profile__skills',
                filter=Q(profile__skills__verified=True)
            )
        ).filter(verified_skills__gte=value)

class SkillFilter(django_filters.FilterSet):
    """
    Filter for Skill model with category and prerequisite filtering.
    """
    name = django_filters.CharFilter(lookup_expr='icontains')
    category = django_filters.CharFilter(lookup_expr='iexact')
    description = django_filters.CharFilter(lookup_expr='icontains')
    has_prerequisites = django_filters.BooleanFilter(
        method='filter_has_prerequisites'
    )
    min_users = django_filters.NumberFilter(
        method='filter_min_users'
    )
    verified_ratio = django_filters.NumberFilter(
        method='filter_verified_ratio'
    )

    class Meta:
        model = Skill
        fields = ['name', 'category']

    def filter_has_prerequisites(self, queryset, name, value):
        """Filter skills based on whether they have prerequisites."""
        if value:
            return queryset.filter(prerequisites__isnull=False).distinct()
        return queryset.filter(prerequisites__isnull=True)

    def filter_min_users(self, queryset, name, value):
        """Filter skills by minimum number of users who have it."""
        return queryset.annotate(
            user_count=django_filters.Count('user_skills')
        ).filter(user_count__gte=value)

    def filter_verified_ratio(self, queryset, name, value):
        """Filter skills by verification ratio (percentage)."""
        return queryset.annotate(
            total_users=django_filters.Count('user_skills'),
            verified_users=django_filters.Count(
                'user_skills',
                filter=Q(user_skills__verified=True)
            )
        ).filter(
            verified_users__gt=0
        ).filter(
            verified_users__gte=django_filters.F('total_users') * value / 100
        )

class UserActivityFilter(django_filters.FilterSet):
    """
    Filter for UserActivity model with time-based and type-based filtering.
    """
    user = django_filters.ModelChoiceFilter(queryset=User.objects.all())
    activity_type = django_filters.MultipleChoiceFilter(
        choices=UserActivity.ACTIVITY_TYPES
    )
    created_after = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte'
    )
    created_before = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte'
    )
    ip_address = django_filters.CharFilter(lookup_expr='exact')
    session_id = django_filters.CharFilter(lookup_expr='exact')
    has_details = django_filters.BooleanFilter(
        method='filter_has_details'
    )

    class Meta:
        model = UserActivity
        fields = [
            'user', 'activity_type', 'created_after',
            'created_before', 'ip_address'
        ]

    def filter_has_details(self, queryset, name, value):
        """Filter activities based on whether they have additional details."""
        if value:
            return queryset.exclude(activity_detail={})
        return queryset.filter(activity_detail={})

class AchievementFilter(django_filters.FilterSet):
    """
    Filter for Achievement model with point-based and category filtering.
    """
    name = django_filters.CharFilter(lookup_expr='icontains')
    category = django_filters.CharFilter(lookup_expr='iexact')
    points_min = django_filters.NumberFilter(
        field_name='points',
        lookup_expr='gte'
    )
    points_max = django_filters.NumberFilter(
        field_name='points',
        lookup_expr='lte'
    )
    is_active = django_filters.BooleanFilter()
    awarded_count = django_filters.NumberFilter(
        method='filter_awarded_count'
    )
    award_rate = django_filters.NumberFilter(
        method='filter_award_rate'
    )

    class Meta:
        model = Achievement
        fields = [
            'name', 'category', 'points_min',
            'points_max', 'is_active'
        ]

    def filter_awarded_count(self, queryset, name, value):
        """Filter achievements by number of times awarded."""
        return queryset.annotate(
            times_awarded=django_filters.Count('userachievement')
        ).filter(times_awarded__gte=value)

    def filter_award_rate(self, queryset, name, value):
        """
        Filter achievements by award rate (percentage of users who have it).
        """
        total_users = User.objects.count()
        if total_users > 0:
            return queryset.annotate(
                awarded_count=django_filters.Count('userachievement')
            ).filter(
                awarded_count__gte=total_users * value / 100
            )
        return queryset.none()

class UserSkillFilter(django_filters.FilterSet):
    """
    Filter for UserSkill model with verification and proficiency filtering.
    """
    user_profile = django_filters.ModelChoiceFilter(
        queryset=UserProfile.objects.all()
    )
    skill = django_filters.ModelChoiceFilter(
        queryset=Skill.objects.all()
    )
    proficiency_level = django_filters.ChoiceFilter(
        choices=UserSkill.PROFICIENCY_LEVELS
    )
    verified = django_filters.BooleanFilter()
    verified_by = django_filters.ModelChoiceFilter(
        queryset=User.objects.all()
    )
    verification_date_after = django_filters.DateTimeFilter(
        field_name='verification_date',
        lookup_expr='gte'
    )
    has_evidence = django_filters.BooleanFilter(
        method='filter_has_evidence'
    )

    class Meta:
        model = UserSkill
        fields = [
            'user_profile', 'skill', 'proficiency_level',
            'verified', 'verified_by'
        ]

    def filter_has_evidence(self, queryset, name, value):
        """Filter skills based on whether they have evidence."""
        if value:
            return queryset.exclude(evidence=[])
        return queryset.filter(evidence=[])