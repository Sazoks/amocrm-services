from dataclasses import dataclass


@dataclass
class AmoCRMCommunicationChannelData:
    """Данные о канале связи для контакта"""

    # Порядковый номер канала связи.
    serial_number: int
    # Название канала связи.
    origin: str
    # ID контакта в amoCRM.
    contact_id: int
    # ID связи контакта и чата в БД amoCRM.
    profile_id: int
    # ID чата.
    chat_id: str
