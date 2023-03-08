from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AmocrmConfig(AppConfig):
    """Конфигурация приложения amoCRM"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.amocrm"
    verbose_name = _('amoCRM')
