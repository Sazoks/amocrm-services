from typing import Any
from enum import StrEnum

from ..utils.request_status import HTTPStatus

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

    def get_contact_by_id(
        self,
        contact_id: int,
        embedded_entities: list[EmbeddedEntities] | None = None,
    ) -> dict[str, Any]:
        """
        Получение данных о контакте.

        :param contact_id: ID конкретного контакта.
        :param embedded_entities:
            Список связанных сущностей, которые необходимо получить в ответе.

        :return: Данные о контакте в словаре.
        """

        # Данные для запроса.
        request_params: dict[str, Any] = {}

        # Запросим вложенные сущности в ответе, если требуется.
        if embedded_entities is not None and len(embedded_entities) > 0:
            request_params["with"] = ",".join(embedded_entities)

        # Делаем запрос на получение данных.
        response = self.__amocrm_client.request(
            method="get",
            url_postfix=AmoCRMOpenEndpoints.CONTACT_DETAIL.format(contact_id=contact_id),  # type: ignore
            params=request_params,
        )
        if response.status_code != HTTPStatus.HTTP_200_OK:
            raise AmoCRMResponseException(
                message=f"Ошибка получения контакта {contact_id}",
                response=response,
            )

        return response.json()

    def get_leads_by_contact(self, contact_id: int) -> list[dict[str, Any]]:
        """
        Получение сделок контакта.

        :param contact_id: ID контакта, у которого нужно получить сделки.

        :return: Список словарей с данными по сделкам.
        """

        contact_data = self.get_contact_by_id(contact_id, [self.EmbeddedEntities.LEADS])

        return contact_data["_embedded"]["leads"]
