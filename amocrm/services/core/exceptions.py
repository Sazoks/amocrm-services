from requests import Response


class AmoCRMResponseException(Exception):
    """Исключение для запросов к amoCRM"""

    def __init__(self, response: Response, message: str | None = None) -> None:
        """Инициализатор класса"""

        self.response = response

        self.message = (
            f"Причина: {response.status_code}\n" f"Детали: {response.content.decode()}"
        )
        if message is not None:
            self.message = message + "\n" + self.message

        super().__init__(self.message)


class AmoCRMAuthException(AmoCRMResponseException):
    """Исключение при аутентификации в amoCRM"""

    def __init__(self, response: Response) -> None:
        """Инициализатор класса"""

        super().__init__(
            message="Ошибка аутентификации",
            response=response,
        )


class AmoCRMGetTalksException(Exception):
    """Исключение при получении бесед в amoCRM"""

    def __init__(self, chat_id: str | None) -> None:
        """Инициализатор класса"""

        self.chat_id = chat_id
        self.message = "Ошибка получения бесед"
        if chat_id is not None:
            self.message += f" у чата {chat_id}"

        super().__init__(self.message)


class AmoCRMUnlinkChatException(Exception):
    """Исключение при отключении чата в amoCRM"""

    def __init__(self, chat_id: str) -> None:
        """Инициализатор класса"""

        self.chat_id = chat_id
        self.message = f"Ошибка при отключении чата {chat_id}"

        super().__init__(self.message)
