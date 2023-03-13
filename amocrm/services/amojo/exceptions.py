class AmoJoClientInitException(Exception):
    """Исключение при инициализации AmoJoClient"""

    def __init__(self) -> None:
        """Инициализатор класса"""

        self.message = "Ошибка при инициализации AmoJoClient"

        super().__init__(self.message)
