from datetime import datetime
from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver
from .models import History, Data_Table, Deleted


@receiver(pre_save, sender=Data_Table)
def remember_old_values(sender, instance, **kwargs):
    """
    Перед сохранением запоминаем текущие (старые) значения объекта в базе,
    чтобы потом записать их в историю.
    """
    if instance.pk:
        try:
            old_instance = Data_Table.objects.get(pk=instance.pk)
            # Сохраняем старые значения в сам объект, чтобы post_save их увидел
            instance._old_address = old_instance.address
            instance._old_party = old_instance.party
            instance._old_comment = old_instance.comment
            instance._old_title = old_instance.title
            instance._old_article = old_instance.article
        except Data_Table.DoesNotExist:
            pass


@receiver(post_save, sender=Data_Table)
def create_history_entry(sender, instance, created, **kwargs):
    if created:
        # Новая запись: пишем текущие значения
        History.objects.create(
            data_table=instance,
            article=instance.article,
            party=instance.party,
            title=instance.title,
            comment=instance.comment,
            address=instance.address,
            date=instance.date or datetime.now()
        )
    else:
        # Обновление: пишем СТАРЫЕ значения (если они изменились)
        old_address = getattr(instance, '_old_address', None)
        old_party = getattr(instance, '_old_party', None)
        old_comment = getattr(instance, '_old_comment', None)
        old_title = getattr(instance, '_old_title', None)
        old_article = getattr(instance, '_old_article', None)

        # Создаем запись только если реально что-то изменилось
        if (old_address != instance.address or
            old_party != instance.party or
            old_comment != instance.comment or
            old_title != instance.title or
            old_article != instance.article):
            
            # Формируем пометку для истории (по желанию)
            changes = []
            if old_address != instance.address:
                changes.append(f"Адрес: {old_address} → {instance.address}")
            
            change_marker = f" [Изменено: {', '.join(changes)}]" if changes else ""

            History.objects.create(
                data_table=instance,
                article=old_article,
                party=old_party,
                title=old_title,
                # В примечание пишем старое примечание + маркер
                comment=(old_comment or '') + change_marker, 
                address=old_address, # <--- ЗАПИСЫВАЕМ СТАРЫЙ АДРЕС
                date=datetime.now()
            )


@receiver(pre_delete, sender=Data_Table)
def log_deleted(sender, instance, using, **kwargs):
    Deleted.objects.create(
        article=instance.article,
        party=instance.party,
        title=instance.title,
        comment=instance.comment,
        address=instance.address,
    )