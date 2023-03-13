from django.db import models
from django.utils.translation import gettext_lazy as _


class AmoCRMTokens(models.Model):
    """Токены доступа amoCRM"""

    manager_name = models.CharField(
        primary_key=True,
        max_length=100,
        verbose_name=_("Имя менеджера токенов"),
    )
    access_token = models.TextField(
        verbose_name=_("Токен доступа"),
    )
    refresh_token = models.TextField(
        verbose_name=_("Токен обновления"),
    )

    class Meta:
        verbose_name = _("Токены доступа amoCRM")
        verbose_name_plural = _("Токены доступа amoCRM")

    def __str__(self) -> str:
        return self.manager_name[:15]
