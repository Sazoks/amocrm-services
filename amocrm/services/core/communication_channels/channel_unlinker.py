from ..exceptions import (
    AmoCRMResponseException,
    AmoCRMUnlinkChatException,
)
from ..client import AmoCRMClient
from ..endpoints import AmoCRMAjaxEndpoints
from ...utils.request_status import HTTPStatus

from .channel_data import AmoCRMCommunicationChannelData


class AmoCRMCommunicationChannelUnlinker:
    """
    Класс для корректного открепления канала связи от контакта.

    Перед откреплением чата закрывает в нем все беседы.
    """

    def __init__(self, amocrm_client: AmoCRMClient) -> None:
        """
        Инициализатор класса.

        :param amocrm_client: Объект для работы с API amoCRM.
        """

        self.__amocrm_client = amocrm_client

    def unlink_chat(self, channel_data: AmoCRMCommunicationChannelData) -> None:
        """
        Откерпление канала связи от контакта с закрытием всех бесед.

        :param channel_data: Данные о канале связи контакта.
        """

        # Открепляем канал связи от контакта.
        try:
            response = self.__amocrm_client.request(
                method="post",
                url_postfix=AmoCRMAjaxEndpoints.UNLINK_CONTACTS_CHAT,
                data={
                    "profile_id": channel_data.profile_id,
                    "contact_id": channel_data.contact_id,
                    "is_main": 1,  # За что отвечает этот параметр, я так и не выяснил, однако чаты открепляются только при значении 1.
                },
                headers={"X-Requested-With": "XMLHttpRequest"},
            )
        except Exception as e:
            raise AmoCRMUnlinkChatException(channel_data.chat_id) from e

        if response.status_code != HTTPStatus.HTTP_200_OK:
            raise AmoCRMResponseException(
                message=f"Ошибка при отключении канала связи {channel_data.chat_id}",
                response=response,
            )
