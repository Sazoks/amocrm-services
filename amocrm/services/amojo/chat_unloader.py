import json
import requests
from typing import (
    Any,
    Self,
)
from datetime import datetime
from dataclasses import dataclass

from ..core.exceptions import AmoCRMResponseException

from .client import AmoJoClient
from .endpoints import AmoJoClosedEndpoints


class AmoJoChatUnloader:
    """
    Класс для выгрузки сообщений у чата.
    """

    @dataclass
    class ChatMessage:
        """Сообщение чата"""

        sender: str
        receiver: str
        time: datetime
        text: str
        media: str

    def __init__(self, amojo_client: AmoJoClient, chat_id: str) -> None:
        """
        Инициализатор класса.

        :param amojo_client: Объект для работы с API amojo-сервера.
        :param chat_id: ID чата, из которого будем выгружать сообщения.
        """

        self.__amojo_client = amojo_client
        self.__chat_id = chat_id
        self.__amojo_id = amojo_client.amojo_id

        self.__offset = 0
        self.__limit = 100
        self.__delta = self.__limit

    def __iter__(self) -> Self:
        """Получение и инициализация объекта-итератора"""

        self.__offset = 0
        self.__limit = 100

        return self

    def __next__(self) -> list[ChatMessage]:
        """
        Генерация следующих данных.

        Генерирует список следующих сообщений чата.

        :raise AmoCRMResponseException: В случае ошибки выгрузки сообщений.

        :return: Некоторый набор сообщений из чата.
        """

        # Делаем запрос на получение очередной пачки сообщений из чата.
        response = self.__amojo_client.request(
            method="get",
            url_postfix=AmoJoClosedEndpoints.GET_CHAT_MESSAGES.format(
                amojo_id=self.__amojo_id
            ),
            params={
                "stand": "v15",
                "offset": self.__offset,
                "limit": self.__limit,
                "chat_id[]": self.__chat_id,
                "get_tags": True,
                "lang": "ru",
            },
        )
        if response.status_code != 200:
            raise AmoCRMResponseException(
                message=(
                    f"Ошибка при выгрузке сообщений "
                    f"[{self.__offset} - {self.__limit}] из чата {self.__chat_id}"
                ),
                response=response,
            )

        # Парсим сообщения из ответа в объекты.
        messages = self.__get_messages_from_response(response)
        if len(messages) == 0:
            raise StopIteration()

        # Смещаем параметры offset и limit для получения следующих сообщений.
        self.__offset += self.__delta
        self.__limit += self.__delta

        return messages

    def __get_messages_from_response(
        self, response: requests.Response
    ) -> list[ChatMessage]:
        """
        Получение списка сообщений из тела HTTP-ответа.

        :param response: Объект HTTP-ответа, содержащий данные с сообщениями.

        :return: Список объектов `ChatMessages`.
        """

        messages: list[self.ChatMessage] = []

        messages_data: list[dict[str, Any]] = response.json()["message_list"]
        for message_data in messages_data:
            sender = message_data["author"]["full_name"]
            receiver = message_data["recipient"]["full_name"]
            receiver_phone = json.loads(
                message_data["recipient"]["origin_profile"]
            )["phone"]
            time = datetime.fromtimestamp(message_data["created_at"])

            messages.append(
                self.ChatMessage(
                    sender=sender,
                    receiver=f"{receiver} {receiver_phone}",
                    time=time,
                    text=message_data["text"],
                    media=message_data["message"]["media"],
                )
            )

        return messages
