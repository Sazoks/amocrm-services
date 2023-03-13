from abc import (
    ABC,
    abstractmethod,
)

from ..tokens import Tokens


class ITokenManaged(ABC):
    """Интерфейс для управления токенами"""

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Получение уникального имени менеджера токенов.

        :return: Имя в виде строки.
        """

        raise NotImplementedError()

    @abstractmethod
    def get_tokens(self) -> Tokens | None:
        """
        Получение токенов доступа.

        :return: Объект с токенами доступа.
        """

        raise NotImplementedError()

    @abstractmethod
    def save_tokens(self, tokens: Tokens) -> Tokens:
        """
        Сохранение токенов доступа.

        :param tokens: Объект с новыми токенами доступа.
        """

        raise NotImplementedError()
