"""
Этот модуль предоставляет классы, реализующие интерфейс `ITokenManaged`.

Эти классы нужны, чтобы не привязывать модуль для работы с amoCRM к 
фреймворку Django, а именно - к моделям Django.

В классах-клиентах для работы с amoCRM необходим некоторый объект, 
который бы всегда предоставлял классам-клиентам актуальные токены доступа 
к API amoCRM, а также давал бы возможность сохранять эти токены.

Интерфейс `ITokenManaged` позволяет нам самим определять правила, по 
которым классы-клиенты будут получать и сохранять токены доступа.
Это может быть файл, другой объект или же база данных.

В этом модуле реализованы два класса, которые сохраняют токены в БД и 
получают токены из БД через Django ORM.
"""

from .services.tokens import Tokens
from .services.interfaces.token_managed import ITokenManaged

from .models import (
    AmoJoToken,
    AmoCRMTokens,
)


class AmoCRMTokensManager(ITokenManaged):
    """Класс для управления токенами для AmoCRMClient"""

    def get_tokens(self) -> Tokens | None:
        """
        Получение токенов доступа.

        :return: Объект с токенами доступа.
        """

        tokens_model = AmoCRMTokens.objects.first()
        if tokens_model is not None:
            return Tokens(tokens_model.access_token, tokens_model.refresh_token)
    
    def save_tokens(self, tokens: Tokens) -> Tokens:
        """
        Сохранение токенов доступа.

        :param tokens: Объект с новыми токенами доступа.
        """

        tokens_model, _ = AmoCRMTokens.objects.update_or_create(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
        )

        return Tokens(tokens_model.access_token, tokens_model.refresh_token)


class AmoJoTokenManager(ITokenManaged):
    """Класс для управления токеном доступа для AmoJoClient"""

    def get_tokens(self) -> Tokens | None:
        """
        Получение токенов доступа.

        :return: Объект с токенами доступа.
        """

        token_model = AmoJoToken.objects.first()
        if token_model is not None:
            return Tokens(token_model.token, None)
    
    def save_tokens(self, tokens: Tokens) -> Tokens:
        """
        Сохранение токенов доступа.

        :param tokens: Объект с новыми токенами доступа.
        """

        token_model, _ = AmoJoToken.objects.update_or_create(token=tokens.access_token)

        return Tokens(token_model.token, None)
