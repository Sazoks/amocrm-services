from enum import StrEnum


class AmoCRMOpenEndpoints(StrEnum):
    """Открытое API"""

    CONTACTS = "/api/v4/contacts"
    CONTACT_DETAIL = "/api/v4/contacts/{contact_id}"
    CLOSE_TALK = "/api/v4/talks/{talk_id}/close"
    ACCOUNT_PARAMS = "/api/v4/account"


class AmoCRMAjaxEndpoints(StrEnum):
    """Эндпоинты для AJAX запросов"""

    UNLINK_CONTACTS_CHAT = "/ajax/v2/profiles/unlink"
    TALKS = "/ajax/v2/talks"


class AmoCRMResources(StrEnum):
    """
    URL ресурсов amoCRM.

    Обычный URL адреса сервиса amoCRM, которые пользователь
    видит в браузере.
    """

    LEAD_DETAIL = "/leads/detail/{lead_id}"


class AmoCRMAuthEndpoints(StrEnum):
    """Эндпоинты аутентификации в amoCRM"""

    OAUTH2_ACCESS_TOKEN = "/oauth2/access_token"
