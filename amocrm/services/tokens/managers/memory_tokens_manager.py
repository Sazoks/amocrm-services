from ..tokens import Tokens
from ..interfaces.token_managed import ITokenManaged


class MemoryTokensManager(ITokenManaged):
    """Менеджер токенов, хранящий их в ОЗУ компьютера"""

    def __init__(self) -> None:
        """Инициализатор класса"""

        self.__tokens: Tokens | None = None

    @property
    def name(self) -> str:
        return self.__class__.__name__

    def get_tokens(self) -> Tokens | None:
        return self.__tokens

    def save_tokens(self, tokens: Tokens) -> Tokens:
        self.__tokens = tokens
        return self.__tokens
