from typing import Any

from ..core import endpoints
from ..core import exceptions
from ..core.client import AmoCRMClient

from ..utils.request_status import HTTPStatus
from ..utils.base_api_client import BaseAPIClient

from ..tokens import Tokens
from ..tokens.interfaces.token_managed import ITokenManaged


class AmoJoClient(BaseAPIClient):
    """
    Класс для взаимодествия с amojo-сервером amoCRM.

    Позволяет делать запросы к любому API amojo-сервера.
    """

    def __init__(
        self,
        base_url: str,
        amocrm_client: AmoCRMClient,
        tokens_manager: ITokenManaged,
        amojo_id: str | None = None,
    ) -> None:
        """
        Инициализатор класса.

        :param base_url: Базовый URL-адрес amojo-сервера.
        :param amocrm_client: Объект для работы с основным API amoCRM.
        :param tokens_manager:
            Объект для управления токенами. Отвечает за их получение и сохранение
            согласно логике класса, реализующего данный интерфейс.
        :param amojo_id:
            ID аккаунта amoCRM на сервере API Чатов. Если None, то
            парамер будет запрошен через объект `amocrm_client`.
        """

        super().__init__(base_url)

        self.__amocrm_client = amocrm_client
        self.__amojo_id = amojo_id or self.__get_amojo_id()

        self.__tokens_manager = tokens_manager
        self.__tokens = self.__tokens_manager.get_tokens()
        if self.__tokens is None:
            self._authorization()

    def __get_amojo_id(self) -> str:
        """Получение `amojo_id` параметра от amoCRM"""

        response = self.__amocrm_client.request(
            method="get",
            url_postfix=endpoints.AmoCRMOpenEndpoints.ACCOUNT_PARAMS,
            params={"with": "amojo_id"},
        )
        if response.status_code != HTTPStatus.HTTP_200_OK:
            raise exceptions.AmoCRMResponseException(response)

        return response.json()["amojo_id"]

    @property
    def amojo_id(self) -> str:
        return self.__amojo_id

    def _authorization(self) -> None:
        """Обновление токена авторизации"""

        # Получим токены для сервера API Чатов.
        response = self.__amocrm_client.request(
            method="post",
            url_postfix=endpoints.AmoCRMAjaxEndpoints.GET_AMOJO_TOKENS,
            data={
                "request[chats][session][action]": "create",
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "X-Requested-With": "XMLHttpRequest",
            },
        )
        if response.status_code != HTTPStatus.HTTP_200_OK:
            raise exceptions.AmoCRMAuthException(response)

        response_data: dict[str, Any] = response.json()
        new_tokens = Tokens(
            response_data["response"]["chats"]["session"]["access_token"],
            response_data["response"]["chats"]["session"]["refresh_token"],
        )
        self.__tokens = self.__tokens_manager.save_tokens(new_tokens)

    def _get_request_headers(self) -> dict[str, Any]:
        """
        Получение заголовков для запроса.

        Позволяет добавлять к каждому запросу доп. заголовки.
        """

        headers = {}
        if self.__tokens is not None:
            headers["X-Auth-Token"] = self.__tokens.access_token

        return headers
