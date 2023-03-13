from typing import Any
from enum import StrEnum

from ..tokens import Tokens
from ..tokens.interfaces.token_managed import ITokenManaged

from ..utils.request_status import HTTPStatus
from ..utils.base_api_client import BaseAPIClient

from .endpoints import AmoCRMAuthEndpoints
from .exceptions import AmoCRMAuthException


class AmoCRMClient(BaseAPIClient):
    """Класс для работы с API amoCRM"""

    class GrantType(StrEnum):
        """Перечисление типов доступов при авторизации"""

        AUTH_CODE = "authorization_code"
        REFRESH = "refresh_token"

    def __init__(
        self,
        base_url: str,
        secret_key: str,
        integration_id: str,
        auth_code: str,
        redirect_url: str,
        tokens_manager: ITokenManaged,
    ) -> None:
        """
        Инициализатор класса.

        :param base_url: Базовый url, куда будут отправляться запросы.
        :param secret_key: Секретный ключ интеграции.
        :param integration_id: ID интеграции, к которой мы делаем запросы.
        :param auth_code:
            Авторизационный код для получения первых access и refresh токенов.
        :param redirect_url:
            URL-для перенаправления после авторизации, должен совпадать со
            значением в amoCRM.
        :param tokens_manager:
            Объект для управления токенами. Отвечает за их получение и сохранение
            согласно логике класса, реализующего данный интерфейс.
        """

        super().__init__(base_url)

        self.__secret_key = secret_key
        self.__integration_id = integration_id
        self.__auth_code = auth_code
        self.__redirect_url = redirect_url

        self.__tokens_manager = tokens_manager
        self.__tokens = self.__tokens_manager.get_tokens()
        if self.__tokens is None:
            self._authorization()

    @property
    def tokens(self) -> Tokens | None:
        return self.__tokens

    def _authorization(self) -> None:
        """Обновление токенов доступа"""

        # Пытаемся обновить токены доступа через refresh-токен.
        try:
            self._auth_with(self.GrantType.REFRESH)
        except Exception as refresh_error:
            # Либо пытаемся это сделать через авторизационный код.
            try:
                self._auth_with(self.GrantType.AUTH_CODE)
            except Exception as auth_code_error:
                raise auth_code_error from refresh_error

    def _auth_with(self, grant_type: GrantType) -> None:
        """
        Метод для обновления токенов доступа либо через авторизационный
        код, либо через refresh-токен.

        :param grant_type:
            Тип получения новых токенов: либо через auth_code, либо
            через refresh_token.

        :raise TypeError: В случае, если передан неверный тип `grant_type`.
        """

        # Выбираем нужный тип аутентификации в amoCRM.
        match grant_type:
            case self.GrantType.REFRESH:
                if self.__tokens is None:
                    raise ValueError(
                        f"Попытка обновить токены через {grant_type}, "
                        f"когда токенов обновленя нет."
                    )
                token_field, token = grant_type.value, self.__tokens.refresh_token
            case self.GrantType.AUTH_CODE:
                token_field, token = "code", self.__auth_code
            case _:
                raise TypeError(f"Неправильный тип доступа: {grant_type}")

        # Подготавливаем данные для запроса.
        data = {
            "client_id": self.__integration_id,
            "client_secret": self.__secret_key,
            "redirect_uri": self.__redirect_url,
            "grant_type": grant_type,
            token_field: token,
        }

        # Делаем запрос на аутентификацию.
        response = self._request(
            method="post",
            url_postfix=AmoCRMAuthEndpoints.OAUTH2_ACCESS_TOKEN,
            data=data,
        )
        # Если не удалось аутентифицироваться, выбрасываем исключение.
        if response.status_code != HTTPStatus.HTTP_200_OK:
            raise AmoCRMAuthException(response)

        # Если все хорошо, сохраняем токены через менеджер.
        json_data: dict[str, str] = response.json()
        new_tokens = Tokens(
            access_token=json_data["access_token"],
            refresh_token=json_data["refresh_token"],
        )
        self.__tokens = self.__tokens_manager.save_tokens(new_tokens)

    def _get_request_headers(self) -> dict[str, Any]:
        """
        Получение заголовков для запроса.

        Позволяет добавлять к каждому запросу доп. заголовки.
        """

        headers = {}
        if self.__tokens is not None:
            headers["Authorization"] = f"Bearer {self.__tokens.access_token}"

        return headers
