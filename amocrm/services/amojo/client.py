import json
from typing import Any

from seleniumwire import webdriver
from seleniumwire.request import Request

from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions

from ..utils.base_api_client import BaseAPIClient
from ..utils.js_local_storage import LocalStorage

from ..tokens import Tokens
from ..interfaces.token_managed import ITokenManaged


class AmoJoClient(BaseAPIClient):
    """
    Класс для взаимодествия с amojo-сервером amoCRM.

    Позволяет делать запросы к любому API amojo-сервера.

    Т.к. доступа к открытому API у нас нет, обновление токена доступа
    проивзодится путем открытия веб-странице в Chrome браузере в
    headless-режиме и парсинга localStorage.
    """

    def __init__(
        self,
        amojo_id: str,
        base_url: str,
        amocrm_base_url: str,
        amocrm_access_token: str,
        tokens_manager: ITokenManaged,
    ) -> None:
        """
        Инициализатор класса.

        :param amojo_id: ID аккаунта amoCRM на amojo-сервере.
        :param base_url: Базовый URL-адрес amojo-сервера.
        param amocrm_base_url: Базовый URL-адрес amocrm-сервера.
        :param amocrm_access_token: Токен доступа для запросов к API amoCRM.
        :param tokens_manager: 
            Объект для управления токенами. Отвечает за их получение и сохранение 
            согласно логике класса, реализующего данный интерфейс.
        """

        super().__init__(base_url)

        self.__amojo_id = amojo_id
        self.__amocrm_base_url = amocrm_base_url
        self.__amocrm_access_token = amocrm_access_token

        self.__tokens_manager = tokens_manager
        self.__tokens = self.__tokens_manager.get_tokens()
        if self.__tokens is None:
            self._authorization()

    @property
    def amojo_id(self) -> str:
        return self.__amojo_id

    def _authorization(self) -> None:
        """
        Обновление токена авторизации путем его парсинга из
        локального хранилища клиента.

        Локальное хранилища выгружается с главной страницы amoCRM
        """

        # Парсим токен amojo из локального хранилища.
        local_storage_data = self.__get_local_storage_data()
        amojo_access_token = json.loads(
            local_storage_data["amojo_token"]
        )["token"]

        # Обновляем токен в менеджере токенов.
        new_tokens = Tokens(
            access_token=amojo_access_token,
            refresh_token=None,
        )
        self.__tokens = self.__tokens_manager.save_tokens(new_tokens)

    def __get_local_storage_data(self) -> dict[str, str]:
        """
        Получение данных из локального хранилища клиента.

        :return: Данные в виде словаря.
        """

        def interceptor(request: Request) -> None:
            """Перехватчик запроса selenium'a"""

            # Добавляем в заголовки access_token.
            request.headers["Authorization"] = f"Bearer {self.__amocrm_access_token}"

        options = ChromeOptions()
        options.add_argument("--headless=new")

        # Загружаем страницу через selenium и получаем данные из localStorage.
        with webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=options,
        ) as driver:
            driver.request_interceptor = interceptor
            driver.get(self.__amocrm_base_url)
            local_storage = LocalStorage(driver)

        return local_storage.items()

    def _get_request_headers(self) -> dict[str, Any]:
        """
        Получение заголовков для запроса.

        Позволяет добавлять к каждому запросу доп. заголовки.
        """

        return {
            "X-Auth-Token": self.__tokens.access_token,
        }
