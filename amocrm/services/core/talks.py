from typing import (
    Any,
    Final,
)

from .exceptions import (
    AmoCRMGetTalksException,
    AmoCRMResponseException,
)
from .endpoints import (
    AmoCRMOpenEndpoints,
    AmoCRMAjaxEndpoints,
)
from .client import AmoCRMClient

from ..utils.request_status import HTTPStatus


class AmoCRMTalks:
    """Класс для работы с беседами amoCRM"""

    def __init__(self, amocrm_client: AmoCRMClient) -> None:
        """
        Инициализатор класса.

        :param amocrm_client: Объект для работы с API amoCRM.
        """

        self.__amocrm_client = amocrm_client

    def get_talks_by_chat_id(self, chat_id: str) -> list[dict[str, Any]]:
        """
        Получение списка данных о беседах у конкретного чата.

        :param chat_id: ID чата.
        :return: Список словарей с данными по беседам.
        """

        try:
            response = self.__amocrm_client.request(
                method="get",
                url_postfix=AmoCRMAjaxEndpoints.TALKS,
                params={"chats_ids[]": chat_id},
            )
        except Exception as e:
            raise AmoCRMGetTalksException(chat_id) from e

        if response.status_code != 200:
            raise AmoCRMResponseException(
                message=f"Ошибка при получении бесед чата {chat_id}",
                response=response,
            )

        return response.json()[chat_id]

    def close_talks_by_chat_id(self, chat_id: str) -> None:
        """
        Закрытие бесед у чата.

        :param chat_id: ID чата.
        """

        # Получаем список всех бесед для чата.
        talks = self.get_talks_by_chat_id(chat_id)

        # Сюда будем собирать ошибки закрытия бесед у чата.
        close_talk_errors: list[Exception] = []

        # Закрываем все незакрытые беседы у контакта в этом чате.
        CLOSED_TALK: Final[int] = 1
        for talk in talks:
            if talk["status"] == CLOSED_TALK:
                continue

            # Делаем запрос на закрытие беседы. Если при запросе была ошибка, или же если
            # сервер вернул не 200 ответ, то сохраним ошибку при обработке этой беседы в
            # список.
            try:
                response = self.__amocrm_client.request(
                    method="post",
                    url_postfix=AmoCRMOpenEndpoints.CLOSE_TALK.format(talk_id=talk["talk_id"]),  # type: ignore
                    data={"force_close": True},
                )
            except Exception as e:
                close_talk_errors.append(e)
            else:
                if (
                    response.status_code != HTTPStatus.HTTP_202_ACCEPTED
                    and response.status_code != HTTPStatus.HTTP_422_UNPROCESSABLE_ENTITY
                ):
                    close_talk_errors.append(AmoCRMResponseException(response))

        if len(close_talk_errors) > 0:
            raise ExceptionGroup(
                f"Ошибки при закрытии бесед чата {chat_id}",
                close_talk_errors,
            )
