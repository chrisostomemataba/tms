from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    verbose_name = 'Users'

    def ready(self):
        try:
            from . import signals
            signals.connect_signals()
            logger.info("User app ready: signals connected")
        except Exception as e:
            logger.error(f"Error in UsersConfig.ready: {str(e)}")