from solo.models import SingletonModel

from django.db import models
from django.utils.translation import gettext_lazy as _


class AmoCRMTokens(SingletonModel):
    """Токены доступа amoCRM"""
    
    access_token = models.TextField(
        verbose_name=_('Токен доступа'),
    )
    refresh_token = models.TextField(
        verbose_name=_('Токен обновления'),
    )

    class Meta:
        verbose_name = _('Токены доступа amoCRM')
        verbose_name_plural = _('Токены доступа amoCRM')

    def __str__(self) -> str:
        return self.access_token[:15]
    

class AmoJoToken(SingletonModel):
    """Токен доступа amoJo"""

    token = models.TextField(
        verbose_name=_('Токен'),
    )

    class Meta:
        verbose_name = _('Токен доступа amoJo')
        verbose_name_plural = _('Токены доступа amoJo')

    def __str__(self) -> str:
        return self.token[:15]
