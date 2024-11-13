from django.contrib import admin
from .models import User, UserProfile, UserSkill, UserActivity, TrainingPreference, Achievement, UserAchievement

# Register your models here.
admin.site.register(User)
admin.site.register(UserProfile)
admin.site.register(UserSkill)
admin.site.register(UserActivity)
admin.site.register(TrainingPreference)
admin.site.register(Achievement)
admin.site.register(UserAchievement)