from bs4 import (
    Tag,
    ResultSet,
    BeautifulSoup,
)

from ..client import AmoCRMClient
from ..endpoints import AmoCRMResources

from .channel_data import AmoCRMCommunicationChannelData


class AmoCRMCommunicationChannelsDataParser:
    """
    Класс для парсинга данных о каналах связи для контакта
    со страницы сделки.

    Получает HTML-страницу сделки у контакта и парсит с нее данные
    о каналах связи с контактом.
    """

    def __init__(self, amocrm_client: AmoCRMClient) -> None:
        """
        Инициализатор класса.

        :param amocrm_client: Объект для работы с API amoCRM.
        """

        self.__amocrm_client = amocrm_client

    def parse(
        self, lead_id: int, contact_id: int
    ) -> list[AmoCRMCommunicationChannelData]:
        """
        Парсинг данных о канале связи для контакта.

        :param lead_id:
            ID сделки, по которому будет запрошена страница
            с необходимыми данными.
        :param contact_id:
            ID контакта, у которого нужно брать информацию по чатам.
            На странице сделки может быть несколько контактов.

        :return: Список данных о каналах связи с контактом.
        """

        # Запрашиваем HTML-страницу сделки.
        response = self.__amocrm_client.request(
            method="get",
            url_postfix=AmoCRMResources.LEAD_DETAIL.format(lead_id=lead_id),  # type: ignore
        )

        # Начинаем парсинг. Создадим парсер.
        html_parser = BeautifulSoup(response.content.decode(), "html.parser")

        # Результирующий список.
        channels_data_list: list[AmoCRMCommunicationChannelData] = []

        # Получаем все элементы с каналов связи на странице.
        channel_buttons: ResultSet[Tag] = html_parser.find_all(
            attrs={
                "class": "profile_messengers-item",
                "data-entity": contact_id,
            }
        )

        # Из каждого элемента парсим нужные данные.
        for i, channel_button in enumerate(channel_buttons):
            send_message_button: Tag = channel_button.find(
                attrs={"data-type": "send_message"}
            )
            chat_id: str = send_message_button["data-chat-id"]
            origin: str = send_message_button["data-origin"]

            profile_id: int = int(
                channel_button.find(attrs={"data-type": "unlink_profile"})["data-value"]
            )

            channels_data_list.append(
                AmoCRMCommunicationChannelData(
                    serial_number=i,
                    origin=origin,
                    chat_id=chat_id,
                    profile_id=profile_id,
                    contact_id=contact_id,
                )
            )

        return channels_data_list
