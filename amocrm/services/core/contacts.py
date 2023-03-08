from typing import Any
from enum import StrEnum

from .client import AmoCRMClient
from .exceptions import AmoCRMResponseException
from .endpoints import AmoCRMOpenEndpoints


class AmoCRMContacts:
    """Класс для работы с контактами в amoCRM"""

    class EmbeddedEntities(StrEnum):
        """Типы вложенных сущностей"""

        CATALOG_ELEMENTS = "catalog_elements"
        LEADS = "leads"
        CUSTOMERS = "customers"

    def __init__(self, amocrm_client: AmoCRMClient) -> None:
        """
        Инициализатор класса.

        :param amocrm_client: Объект для работы с API amoCRM.
        """

        self.__amocrm_client = amocrm_client

    # TODO: Если я правильно понял, то amoCRM вернет не абсолютно все контакты в аккаунте,
    #   а максимум 250. И это может быть проблемой. Возможно, нужно будет найти решение,
    #   которое позволит получать точно все контакты. Одним или нет запросом - неважно.
    def get(
        self,
        contact_id: int | None = None,
        embedded_entities: list[EmbeddedEntities] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Получение данных о контактах.

        :param contact_id: ID конкретного контакта.
        :param embedded_entities:
            Список связанных сущностей, которые необходимо получить в ответе.

        :return: Список словарей с данными о контактах.

        :raise AmoCRMResponseException: В случае ошибки получения контактов.
        """

        # Данные для запроса.
        request_params: dict[str, Any] = {}

        # Запросим вложенные сущности в ответе, если требуется.
        if embedded_entities is not None and len(embedded_entities) > 0:
            request_params["with"] = ",".join(embedded_entities)

        # Выбираем эндпоинт на основе `contact_id`.
        # Либо запрашиваем один контакт, либо все.
        if contact_id is not None:
            url_postfix = AmoCRMOpenEndpoints.CONTACT_DETAIL.format(contact_id=contact_id)  # type: ignore
        else:
            url_postfix = AmoCRMOpenEndpoints.CONTACTS

        # Делаем запрос на получение данных.
        response = self.__amocrm_client.request(
            method="get",
            url_postfix=url_postfix,
            params=request_params,
        )
        if response.status_code != 200:
            raise AmoCRMResponseException(
                message="Ошибка получения контактов",
                response=response,
            )

        # Если был запрошен один контакт, обернем данные о нем в список.
        if contact_id is not None:
            return [response.json()]

        # Иначе вернем список контактов из тела ответа.
        return response.json()["_embedded"]["contacts"]
