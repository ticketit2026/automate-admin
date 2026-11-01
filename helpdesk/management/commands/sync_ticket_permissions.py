
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from helpdesk.models import Ticket, TicketReply


class Command(BaseCommand):
    help = "یکپارچه‌سازی دسترسی‌های تیکت"

    @transaction.atomic
    def handle(self, *args, **kwargs):

        ticket_ct = ContentType.objects.get_for_model(Ticket)
        reply_ct = ContentType.objects.get_for_model(TicketReply)

        labels = {
            "add_ticket": "ایجاد تیکت",
            "view_ticket": "مشاهده تیکت",
            "view_all_tickets": "مشاهده همه تیکت‌ها",
            "change_ticket": "ویرایش",
            "delete_ticket": "حذف",
            "reply_ticket": "جواب دادن به تیکت",
            "assign_ticket": "ارجاع",
        }

        permissions = {}

        for codename, name in labels.items():
            permission, _ = Permission.objects.update_or_create(
                content_type=ticket_ct,
                codename=codename,
                defaults={"name": name},
            )
            permissions[codename] = permission

        old_permissions = [
            (reply_ct, "add_ticketreply", "reply_ticket"),
            (reply_ct, "view_ticketreply", "view_ticket"),
            (reply_ct, "change_ticketreply", "change_ticket"),
            (reply_ct, "delete_ticketreply", "delete_ticket"),
            (ticket_ct, "change_ticket_status", "change_ticket"),
        ]

        for content_type, old_code, new_code in old_permissions:
            old_permission = Permission.objects.filter(
                content_type=content_type,
                codename=old_code,
            ).first()

            if old_permission is None:
                continue

            new_permission = permissions[new_code]

            for group in old_permission.group_set.all():
                group.permissions.add(new_permission)

            for user in old_permission.user_set.all():
                user.user_permissions.add(new_permission)

            old_permission.delete()

        self.stdout.write(
            self.style.SUCCESS(
                "دسترسی‌های تیکت با موفقیت یکپارچه شدند."
            )
        )
