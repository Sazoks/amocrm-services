import requests
from typing import Any
from enum import IntEnum


class BaseAPIClient:
    """
    Базовый класс для API клиентов.

    Определяет базовую логику работы с внешним API.
    """

    _REQUESTS_THAT_HAVE_BODY = ("post", "put", "putch")

    class RequestStatus(IntEnum):
        """Коды ответа при запросе"""

        HTTP_401_UNAUTHORIZED = 401

    def __init__(self, base_url: str) -> None:
        """
        Инициализатор класса.

        :param base_url: Базовый URL внешнего сервиса.
        """

        self._base_url = base_url

    @property
    def base_url(self) -> str:
        return self._base_url

    def request(
        self,
        method: str,
        url_postfix: str,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
    ) -> requests.Response:
        """
        Метод отправки запроса на указанный эндпоинт.

        В случае неавторизованного запроса производит авторизацию и
        повторяет запрос.

        :param method: HTTP-метод запроса.
        :param url_postfix: Маршрут эндпоинта.
        :param data: Данные для тела запроса.
        :param params: GET-параметры запроса.
        :param headers: Дополнительные заголовки запроса.

        :return: Объект ответа `requests.Response`.
        """

        # Делаем запрос.
        response = self._request(method, url_postfix, data, params, headers)

        # Если запрос был неавторизированным, производим авторизационный запрос
        # и повторяем исходный запрос.
        if self._is_unauthorized_request(response):
            self._authorization()
            response = self._request(method, url_postfix, data, params, headers)

        return response

    def _request(
        self,
        method: str,
        url_postfix: str,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
    ) -> requests.Response:
        """
        Базовый метод отправки запроса на указанный эндпоинт.

        :param method: HTTP-метод запроса.
        :param url_postfix: Маршрут эндпоинта.
        :param data: Данные для тела запроса.
        :param params: GET-параметры запроса.
        :param headers: Дополнительные заголовки запроса.

        :return: Объект ответа `requests.Response`.
        """

        # Если есть доп. GET-параметры, добавляем их к URL.
        get_params: dict[str, Any] = self._get_request_params()
        get_params.update(params or {})

        # Если есть данные для тела запроса и если метод поддерживает эти данные,
        # добавим их в тело запроса.
        body_data: dict[str, Any] = {}
        if data is not None:
            if not self._has_request_body(method):
                raise ValueError(
                    f"HTTP метод {method.upper()} не поддерживает данные "
                    f"для тела запроса."
                )
            body_data.update(self._get_request_data())
            body_data.update(data)

        # Добавляем доп. заголовки, если они есть.
        request_headers: dict[str, Any] = self._get_request_headers()
        request_headers.update(headers or {})

        # Получаем полный URL-адрес до эндпоинта во внешнем сервисе.
        full_url = self._get_full_url(url_postfix)

        return requests.request(
            method=method,
            url=full_url,
            params=get_params,
            json=body_data,
            headers=request_headers,
        )

    def _get_request_params(self) -> dict[str, Any]:
        """
        Получение GET-параметров для запроса.

        Позволяет добавлять к каждому запроса доп. GET-параметры.
        """

        return {}

    def _get_request_data(self) -> dict[str, Any]:
        """
        Получение данных для тела запроса.

        Позволяет добавлять к каждому запросу, который имеет тело, доп. данные.
        """

        return {}

    def _get_request_headers(self) -> dict[str, Any]:
        """
        Получение заголовков для запроса.

        Позволяет добавлять к каждому запросу доп. заголовки.
        """

        return {}

    def _is_unauthorized_request(self, response: requests.Response) -> bool:
        """
        Метод, позволяющие определить, являлся ли запрос неавторизованным на
        основе полученного ответа.

        :param response: Объект синхронного ответа `requests.Response`.
        """

        return response.status_code == self.RequestStatus.HTTP_401_UNAUTHORIZED

    def _authorization(self) -> None:
        """Метод для проведения авторизации во внешнем сервисе"""
        pass

    @classmethod
    def _has_request_body(cls, method: str) -> bool:
        """
        Проверка, имеет ли запрос с методом `method` тело для данных.

        :param method: HTTP метод.

        :return: True, если запрос с методом `method` имеет тело, иначе False.
        """

        return method.lower() in cls._REQUESTS_THAT_HAVE_BODY

    def _get_full_url(self, url_postfix: str) -> str:
        """
        Создание полного URL-адреса для запроса с проверками.

        :param url_postfix: Эндпоинт в API Mango.
        :return: Полный URL-адрес для запроса.
        """

        # Убираем лишние слешы, если они есть.
        if url_postfix.startswith("/"):
            url_postfix = url_postfix[1:]

        base_url = self.__base_url
        if base_url.endswith("/"):
            base_url = base_url[:-1]

        return base_url + "/" + url_postfix
