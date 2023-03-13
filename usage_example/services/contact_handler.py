from itertools import groupby

from django.conf import settings
from django.db import transaction

from apps.amocrm.services.core.talks import AmoCRMTalks
from apps.amocrm.services.core.client import AmoCRMClient
from apps.amocrm.services.core.contacts import AmoCRMContacts
from apps.amocrm.services.core import exceptions as amocrm_exceptions
from apps.amocrm.services.core.communication_channels.channel_data import (
    AmoCRMCommunicationChannelData,
)
from apps.amocrm.services.core.communication_channels.channel_unlinker import (
    AmoCRMCommunicationChannelUnlinker,
)
from apps.amocrm.services.core.communication_channels.channel_data_parser import (
    AmoCRMCommunicationChannelsDataParser,
)

from apps.amocrm.services.amojo.client import AmoJoClient
from apps.amocrm.services.amojo import exceptions as amojo_exceptions
from apps.amocrm.services.amojo.chat_unloader import AmoJoChatUnloader

from apps.amocrm.tokens_managers import AmoCRMTokensManager

from ..models import AmoCRMChatMessage


class ContactHandler:
    """
    Класс для обработки одного контакта.

    Выгружает все старые переписки, закрывает все старые
    беседы и открепляет все чаты, кроме последнего.


    Алгоритм работы:

        1. Получает информацию о контакте с ID связанных сделок.
        2. Если сделки есть, берет любую (первую, например), запрашивает
        страницу этой сделки и парсит с нее данные о каналах связи с контактом.
        3. Группирует каналы связей по источникам и в каждой такое группе
        удаляет все каналы связи, сохраняя переписку из них и закрывая беседы,
        кроме последнего. Здесь порядок каналов связи на странице берем на веру, что он
        отображает их хронологию по времени. Именно поэтому сохраняем переписки из каналов,
        которые имеют более низкий порядковый номер.
    """

    def __init__(self, contact_id: int) -> None:
        """
        Инициализатор класса.

        :param contact_id: ID обрабатываемого контакта.
        """

        self.__contact_id = contact_id

    def run(self) -> None:
        """Запуск обработки контакта"""

        # Инициализируем клиент для работы с amoCRM.
        try:
            amocrm_client = AmoCRMClient(
                base_url=settings.AMO_BASE_URL,
                secret_key=settings.AMO_SECRET_KEY,
                integration_id=settings.AMO_INTEGRATION_ID,
                auth_code=settings.AMO_AUTH_CODE,
                redirect_url=settings.AMO_REDIRECT_URL,
                tokens_manager=AmoCRMTokensManager("amocrm_client"),
            )
        except Exception as e:
            raise amocrm_exceptions.AmoCRMClientInitException() from e

        # Получим информацию по сделкам контакта.
        try:
            leads = AmoCRMContacts(amocrm_client).get_leads_by_contact(
                self.__contact_id
            )
        except Exception as e:
            raise amocrm_exceptions.AmoCRMGetContactException(self.__contact_id) from e

        if len(leads) == 0:
            raise amocrm_exceptions.AmoCRMNoLeadsException()

        # Инициализация клиента для работы с закрытым API Чатов.
        try:
            amojo_client = AmoJoClient(
                base_url=settings.AMOJO_BASE_URL,
                amocrm_client=amocrm_client,
                tokens_manager=AmoCRMTokensManager("amojo_client"),
            )
        except Exception as e:
            raise amojo_exceptions.AmoJoClientInitException() from e

        amocrm_talks = AmoCRMTalks(amocrm_client)
        amocrm_chat_unlinker = AmoCRMCommunicationChannelUnlinker(amocrm_client)

        # Парсим со страницы сделки все данные о каналах связи с контактом.
        channels_data = AmoCRMCommunicationChannelsDataParser(amocrm_client).parse(
            leads[0]["id"], self.__contact_id
        )

        # Сюда будем собирать ошибки при обработке источников.
        process_origins_errors: list[Exception] = []

        # Группируем каналы связи по типу источника (whatsapp, viber, telegram и прочее).
        for origin, grouper_channels in groupby(
            channels_data, key=lambda channel_data: channel_data.origin
        ):
            try:
                # Сортируем сгруппированные каналы связи по порядковому номеру.
                # Порядковый номер обозначает хронологию чатов с контактом.
                sorted_channels_data: list[AmoCRMCommunicationChannelData] = sorted(
                    grouper_channels,
                    key=lambda channel_data: channel_data.serial_number,
                )

                # Сюда будем сохранять ошибки, возникшие в ходе обработки каналов.
                process_channels_errors: list[Exception] = []

                # В каждой группе каналов связи у всех старых каналов (всех, кроме последнего),
                # выгрузим переписку, закроем все беседы и открепим эти каналы.
                # Затем, выгруженную переписку сохраним КУДА-ТО (решение куда пока что еще не принято).
                for channel_data in sorted_channels_data[:-1]:
                    try:
                        with transaction.atomic():
                            # Выгружаем сообщения из чата "пачками", а не все сразу.
                            for messages in AmoJoChatUnloader(
                                amojo_client, channel_data.chat_id
                            ):
                                messages_models = [
                                    AmoCRMChatMessage(**message.__dict__)
                                    for message in messages
                                ]
                                AmoCRMChatMessage.objects.bulk_create(messages_models)

                            # Закрываем беседы канала и отключаем канал от контакта.
                            amocrm_talks.close_talks_by_chat_id(channel_data.chat_id)
                            amocrm_chat_unlinker.unlink_chat(channel_data)
                    except* Exception as e:
                        process_channels_errors.append(e)

                if len(process_channels_errors) > 0:
                    raise ExceptionGroup(
                        f"Ошибки при обработке {len(process_channels_errors)} каналов источника {origin}",
                        process_channels_errors,
                    )
            except* Exception as e:
                process_origins_errors.append(e)

        if len(process_origins_errors) > 0:
            raise ExceptionGroup(
                f"Ошибки при обработке каналов контакта {self.__contact_id}",
                process_origins_errors,
            )
