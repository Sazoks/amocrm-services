"""
Пример использования подсистемы в асинхронной задаче.
"""

import logging
import traceback
from celery import shared_task

from apps.amocrm.services.core.exceptions import AmoCRMNoLeadsException

from .models import AmoCRMContact
from .services.contact_handler import ContactHandler


logger = logging.getLogger(__name__)


@shared_task
def delete_contacts_chats_task(contact_id: int) -> None:
    """
    Задача на удаление лишних чатов у контакта.

    :param contact_id: ID обрабатываемого контакта.
    """

    logger.info(f"Началась обработка контакта {contact_id}")

    # Начнем обработку контакта.
    # В случае возникновения какой-либо ошибки, кроме `AmoCRMNoLeadsException`,
    # поменяем статус контакта на `необработанный`.
    # Если контакт обработался успешно, удалим его из БД.
    try:
        ContactHandler(contact_id).run()
    except* AmoCRMNoLeadsException:
        AmoCRMContact.objects.filter(contact_id=contact_id).delete()
        logger.info(f"Контакт {contact_id} обрабатывать не нужно, сделок нет")
    except* Exception:
        AmoCRMContact.objects.filter(contact_id=contact_id).update(
            status=AmoCRMContact.Status.UNPROCESSED
        )
        logger.error(traceback.format_exc())
    else:
        AmoCRMContact.objects.filter(contact_id=contact_id).delete()
        logger.info(f"Контакт {contact_id} успешно обработан")
