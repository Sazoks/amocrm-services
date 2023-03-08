from enum import StrEnum


class AmoJoClosedEndpoints(StrEnum):
    """Перечисление с закрытм API amojo сервиса"""

    GET_CHAT_MESSAGES = "/messages/{amojo_id}/merge"
