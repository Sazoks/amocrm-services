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
"""

from .services.tokens import Tokens
from .services.tokens.interfaces.token_managed import ITokenManaged

from .models import AmoCRMTokens


class AmoCRMTokensManager(ITokenManaged):
    """Класс для управления токенами для AmoCRM"""

    def __init__(self, name: str) -> None:
        """
        Инициализатор класса.

        :param name: Уникальное название менеджера.
        """

        self.__name = name

    @property
    def name(self) -> str:
        return self.__name

    def get_tokens(self) -> Tokens | None:  # type: ignore[return]
        """
        Получение токенов доступа из БД.

        :return: Объект с токенами доступа.
        """

        tokens_model = AmoCRMTokens.objects.filter(manager_name=self.name).first()
        if tokens_model is not None:
            return Tokens(tokens_model.access_token, tokens_model.refresh_token)

    def save_tokens(self, tokens: Tokens) -> Tokens:
        """
        Сохранение токенов доступа в БД.

        :param tokens: Объект с новыми токенами доступа.
        """

        tokens_model, _ = AmoCRMTokens.objects.update_or_create(
            manager_name=self.name,
            defaults={
                "access_token": tokens.access_token,
                "refresh_token": tokens.refresh_token,
            },
        )

        return Tokens(tokens_model.access_token, tokens_model.refresh_token)
