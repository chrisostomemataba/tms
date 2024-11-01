# Generated by Django 4.2.7 on 2024-10-26 12:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import phonenumber_field.modelfields
import simple_history.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="first name"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="last name"
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        help_text="Unique identifier for the user",
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        max_length=254, unique=True, verbose_name="email address"
                    ),
                ),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("ADMIN", "Admin"),
                            ("TRAINER", "Trainer"),
                            ("PARTICIPANT", "Participant"),
                        ],
                        default="PARTICIPANT",
                        max_length=20,
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "last_active",
                    models.DateTimeField(
                        blank=True,
                        default=django.utils.timezone.now,
                        help_text="Last time user was active",
                        null=True,
                    ),
                ),
                (
                    "deactivated_at",
                    models.DateTimeField(
                        blank=True, help_text="When user was deactivated", null=True
                    ),
                ),
                (
                    "deactivation_reason",
                    models.TextField(blank=True, help_text="Reason for deactivation"),
                ),
                (
                    "failed_login_attempts",
                    models.PositiveIntegerField(
                        default=0, help_text="Number of failed login attempts"
                    ),
                ),
                (
                    "last_failed_login",
                    models.DateTimeField(
                        blank=True,
                        help_text="Time of last failed login attempt",
                        null=True,
                    ),
                ),
                (
                    "password_changed_at",
                    models.DateTimeField(
                        blank=True,
                        help_text="When password was last changed",
                        null=True,
                    ),
                ),
            ],
            options={
                "verbose_name": "user",
                "verbose_name_plural": "users",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Achievement",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Name of the achievement", max_length=100
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        help_text="Detailed description of the achievement"
                    ),
                ),
                (
                    "category",
                    models.CharField(
                        help_text="Category of the achievement", max_length=50
                    ),
                ),
                (
                    "badge_image",
                    models.ImageField(
                        help_text="Badge image for the achievement",
                        upload_to="achievements/",
                    ),
                ),
                (
                    "points",
                    models.IntegerField(
                        default=0, help_text="Points awarded for this achievement"
                    ),
                ),
                (
                    "criteria",
                    models.JSONField(help_text="Criteria for earning achievement"),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True, help_text="Whether this achievement can be earned"
                    ),
                ),
            ],
            options={
                "ordering": ["category", "points"],
            },
        ),
        migrations.CreateModel(
            name="Skill",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Name of the skill", max_length=100, unique=True
                    ),
                ),
                (
                    "category",
                    models.CharField(help_text="Category of the skill", max_length=50),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True, help_text="Detailed description of the skill"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "level_criteria",
                    models.JSONField(
                        default=dict, help_text="Criteria for each proficiency level"
                    ),
                ),
                (
                    "prerequisites",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Skills that must be completed before this one",
                        related_name="dependent_skills",
                        to="users.skill",
                    ),
                ),
            ],
            options={
                "ordering": ["category", "name"],
            },
        ),
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "phone_number",
                    phonenumber_field.modelfields.PhoneNumberField(
                        blank=True,
                        help_text="Contact phone number",
                        max_length=128,
                        null=True,
                        region=None,
                    ),
                ),
                (
                    "department",
                    models.CharField(
                        blank=True, help_text="Department or division", max_length=100
                    ),
                ),
                (
                    "position",
                    models.CharField(
                        blank=True, help_text="Job position or title", max_length=100
                    ),
                ),
                (
                    "bio",
                    models.TextField(
                        blank=True, help_text="User biography or description"
                    ),
                ),
                (
                    "avatar",
                    models.ImageField(
                        blank=True,
                        help_text="Profile picture",
                        null=True,
                        upload_to="avatars/",
                    ),
                ),
                (
                    "years_of_experience",
                    models.PositiveIntegerField(
                        default=0, help_text="Years of professional experience"
                    ),
                ),
                (
                    "education",
                    models.JSONField(
                        default=list, help_text="List of educational qualifications"
                    ),
                ),
                (
                    "certifications",
                    models.JSONField(
                        default=list, help_text="List of professional certifications"
                    ),
                ),
                (
                    "linkedin_profile",
                    models.URLField(blank=True, help_text="LinkedIn profile URL"),
                ),
                (
                    "github_profile",
                    models.URLField(blank=True, help_text="GitHub profile URL"),
                ),
                (
                    "portfolio_website",
                    models.URLField(blank=True, help_text="Personal portfolio website"),
                ),
                (
                    "ui_preferences",
                    models.JSONField(
                        default=dict, help_text="User interface preferences"
                    ),
                ),
                (
                    "notification_settings",
                    models.JSONField(
                        default=dict, help_text="Notification preferences"
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="UserSkill",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "proficiency_level",
                    models.CharField(
                        choices=[
                            ("BEGINNER", "Beginner"),
                            ("INTERMEDIATE", "Intermediate"),
                            ("ADVANCED", "Advanced"),
                            ("EXPERT", "Expert"),
                        ],
                        help_text="User's proficiency level in this skill",
                        max_length=20,
                    ),
                ),
                (
                    "verified",
                    models.BooleanField(
                        default=False, help_text="Whether this skill has been verified"
                    ),
                ),
                (
                    "verification_date",
                    models.DateTimeField(
                        blank=True, help_text="When this skill was verified", null=True
                    ),
                ),
                (
                    "evidence",
                    models.JSONField(
                        default=list, help_text="Evidence supporting skill level"
                    ),
                ),
                (
                    "skill",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user_skills",
                        to="users.skill",
                    ),
                ),
                (
                    "user_profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="skills",
                        to="users.userprofile",
                    ),
                ),
                (
                    "verified_by",
                    models.ForeignKey(
                        blank=True,
                        help_text="User who verified this skill",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="verified_skills",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["skill__category", "skill__name"],
            },
        ),
        migrations.CreateModel(
            name="UserActivity",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "activity_type",
                    models.CharField(
                        choices=[
                            ("LOGIN", "User Login"),
                            ("LOGOUT", "User Logout"),
                            ("ENROLL", "Course Enrollment"),
                            ("COMPLETE", "Course Completion"),
                            ("CERTIFICATE", "Certificate Generated"),
                            ("ASSESSMENT", "Assessment Taken"),
                            ("SKILL_UPDATE", "Skill Updated"),
                            ("ACHIEVEMENT_EARNED", "Achievement Earned"),
                            ("PROFILE_UPDATE", "Profile Updated"),
                            ("PASSWORD_CHANGE", "Password Changed"),
                            ("ROLE_CHANGE", "Role Changed"),
                            ("USER_CREATION", "User Created"),
                            ("SKILL_VERIFICATION", "Skill Verified"),
                        ],
                        help_text="Type of activity",
                        max_length=20,
                    ),
                ),
                (
                    "activity_detail",
                    models.JSONField(
                        default=dict, help_text="Additional details about the activity"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, help_text="When the activity occurred"
                    ),
                ),
                (
                    "ip_address",
                    models.GenericIPAddressField(
                        blank=True, help_text="IP address of the user", null=True
                    ),
                ),
                (
                    "user_agent",
                    models.TextField(blank=True, help_text="User agent string"),
                ),
                (
                    "session_id",
                    models.CharField(
                        blank=True, help_text="Session identifier", max_length=100
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="activities",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "User activities",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="UserAchievement",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "earned_at",
                    models.DateTimeField(
                        auto_now_add=True, help_text="When the achievement was earned"
                    ),
                ),
                (
                    "evidence",
                    models.JSONField(
                        default=dict, help_text="Supporting evidence for achievement"
                    ),
                ),
                (
                    "achievement",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="users.achievement",
                    ),
                ),
                (
                    "awarded_by",
                    models.ForeignKey(
                        help_text="User who awarded this achievement",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="awarded_achievements",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="achievements",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-earned_at"],
            },
        ),
        migrations.CreateModel(
            name="TrainingPreference",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "preferred_learning_style",
                    models.CharField(
                        choices=[
                            ("VISUAL", "Visual"),
                            ("AUDITORY", "Auditory"),
                            ("KINESTHETIC", "Kinesthetic"),
                            ("READING", "Reading/Writing"),
                        ],
                        default="VISUAL",
                        help_text="Preferred style of learning",
                        max_length=20,
                    ),
                ),
                (
                    "preferred_training_days",
                    models.JSONField(
                        default=list, help_text="List of preferred days for training"
                    ),
                ),
                (
                    "preferred_time_slots",
                    models.JSONField(
                        default=list, help_text="List of preferred time slots"
                    ),
                ),
                (
                    "preferred_group_size",
                    models.CharField(
                        choices=[
                            ("INDIVIDUAL", "Individual"),
                            ("SMALL", "Small Group (2-5)"),
                            ("MEDIUM", "Medium Group (6-15)"),
                            ("LARGE", "Large Group (15+)"),
                        ],
                        default="SMALL",
                        help_text="Preferred training group size",
                        max_length=20,
                    ),
                ),
                (
                    "language_preferences",
                    models.JSONField(
                        default=list, help_text="Preferred languages for training"
                    ),
                ),
                (
                    "notification_preferences",
                    models.JSONField(
                        default=dict,
                        help_text="Notification settings for different events",
                    ),
                ),
                (
                    "accessibility_requirements",
                    models.JSONField(
                        default=dict, help_text="Specific accessibility needs"
                    ),
                ),
                (
                    "user_profile",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="training_preferences",
                        to="users.userprofile",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="HistoricalUserProfile",
            fields=[
                (
                    "id",
                    models.UUIDField(db_index=True, default=uuid.uuid4, editable=False),
                ),
                (
                    "phone_number",
                    phonenumber_field.modelfields.PhoneNumberField(
                        blank=True,
                        help_text="Contact phone number",
                        max_length=128,
                        null=True,
                        region=None,
                    ),
                ),
                (
                    "department",
                    models.CharField(
                        blank=True, help_text="Department or division", max_length=100
                    ),
                ),
                (
                    "position",
                    models.CharField(
                        blank=True, help_text="Job position or title", max_length=100
                    ),
                ),
                (
                    "bio",
                    models.TextField(
                        blank=True, help_text="User biography or description"
                    ),
                ),
                (
                    "avatar",
                    models.TextField(
                        blank=True,
                        help_text="Profile picture",
                        max_length=100,
                        null=True,
                    ),
                ),
                (
                    "years_of_experience",
                    models.PositiveIntegerField(
                        default=0, help_text="Years of professional experience"
                    ),
                ),
                (
                    "education",
                    models.JSONField(
                        default=list, help_text="List of educational qualifications"
                    ),
                ),
                (
                    "certifications",
                    models.JSONField(
                        default=list, help_text="List of professional certifications"
                    ),
                ),
                (
                    "linkedin_profile",
                    models.URLField(blank=True, help_text="LinkedIn profile URL"),
                ),
                (
                    "github_profile",
                    models.URLField(blank=True, help_text="GitHub profile URL"),
                ),
                (
                    "portfolio_website",
                    models.URLField(blank=True, help_text="Personal portfolio website"),
                ),
                (
                    "ui_preferences",
                    models.JSONField(
                        default=dict, help_text="User interface preferences"
                    ),
                ),
                (
                    "notification_settings",
                    models.JSONField(
                        default=dict, help_text="Notification preferences"
                    ),
                ),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
                        max_length=1,
                    ),
                ),
                (
                    "history_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "historical user profile",
                "verbose_name_plural": "historical user profiles",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="HistoricalUser",
            fields=[
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="first name"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="last name"
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                (
                    "id",
                    models.UUIDField(
                        db_index=True,
                        default=uuid.uuid4,
                        editable=False,
                        help_text="Unique identifier for the user",
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        db_index=True, max_length=254, verbose_name="email address"
                    ),
                ),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("ADMIN", "Admin"),
                            ("TRAINER", "Trainer"),
                            ("PARTICIPANT", "Participant"),
                        ],
                        default="PARTICIPANT",
                        max_length=20,
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(blank=True, editable=False)),
                ("updated_at", models.DateTimeField(blank=True, editable=False)),
                (
                    "last_active",
                    models.DateTimeField(
                        blank=True,
                        default=django.utils.timezone.now,
                        help_text="Last time user was active",
                        null=True,
                    ),
                ),
                (
                    "deactivated_at",
                    models.DateTimeField(
                        blank=True, help_text="When user was deactivated", null=True
                    ),
                ),
                (
                    "deactivation_reason",
                    models.TextField(blank=True, help_text="Reason for deactivation"),
                ),
                (
                    "failed_login_attempts",
                    models.PositiveIntegerField(
                        default=0, help_text="Number of failed login attempts"
                    ),
                ),
                (
                    "last_failed_login",
                    models.DateTimeField(
                        blank=True,
                        help_text="Time of last failed login attempt",
                        null=True,
                    ),
                ),
                (
                    "password_changed_at",
                    models.DateTimeField(
                        blank=True,
                        help_text="When password was last changed",
                        null=True,
                    ),
                ),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
                        max_length=1,
                    ),
                ),
                (
                    "history_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "historical user",
                "verbose_name_plural": "historical users",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.AddIndex(
            model_name="achievement",
            index=models.Index(
                fields=["category", "points"], name="users_achie_categor_151c1c_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="achievement",
            index=models.Index(
                fields=["is_active"], name="users_achie_is_acti_7e12c5_idx"
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="groups",
            field=models.ManyToManyField(
                blank=True,
                help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                related_name="user_set",
                related_query_name="user",
                to="auth.group",
                verbose_name="groups",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="user_permissions",
            field=models.ManyToManyField(
                blank=True,
                help_text="Specific permissions for this user.",
                related_name="user_set",
                related_query_name="user",
                to="auth.permission",
                verbose_name="user permissions",
            ),
        ),
        migrations.AddIndex(
            model_name="userskill",
            index=models.Index(
                fields=["user_profile", "skill"], name="users_users_user_pr_e58ebd_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="userskill",
            index=models.Index(
                fields=["verified"], name="users_users_verifie_2ba3f2_idx"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="userskill",
            unique_together={("user_profile", "skill")},
        ),
        migrations.AddIndex(
            model_name="userprofile",
            index=models.Index(fields=["user"], name="users_userp_user_id_d181df_idx"),
        ),
        migrations.AddIndex(
            model_name="useractivity",
            index=models.Index(
                fields=["user", "-created_at"], name="users_usera_user_id_250303_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="useractivity",
            index=models.Index(
                fields=["activity_type", "-created_at"],
                name="users_usera_activit_257cae_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="useractivity",
            index=models.Index(
                fields=["created_at"], name="users_usera_created_828ca1_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="userachievement",
            index=models.Index(
                fields=["user", "achievement"], name="users_usera_user_id_3c8d10_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="userachievement",
            index=models.Index(
                fields=["-earned_at"], name="users_usera_earned__b71dfd_idx"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="userachievement",
            unique_together={("user", "achievement")},
        ),
        migrations.AddIndex(
            model_name="skill",
            index=models.Index(
                fields=["category", "name"], name="users_skill_categor_709b17_idx"
            ),
        ),
    ]
