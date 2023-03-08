from dataclasses import dataclass


@dataclass
class Tokens:
    """Токены доступа для запросов"""

    access_token: str | None
    refresh_token: str | None
