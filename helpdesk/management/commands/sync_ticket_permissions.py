"""یکسان‌سازی نام و کد دسترسی‌های تیکت؛ اجرا با:
python manage.py shell < sync_ticket_permissions.py
"""
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from helpdesk.models import Ticket, TicketReply


@transaction.atomic
def sync_permissions():
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

    # دسترسی‌های قدیمی را به معادل جدیدشان منتقل می‌کنیم تا
    # مجوزهای گروه‌ها و کاربران از بین نروند.
    old_permissions = [
        (reply_ct, "add_ticketreply", "reply_ticket"),
        (reply_ct, "view_ticketreply", "view_ticket"),
        (reply_ct, "change_ticketreply", "change_ticket"),
        (reply_ct, "delete_ticketreply", "delete_ticket"),
        (ticket_ct, "change_ticket_status", "change_ticket"),
    ]

    for old_content_type, old_codename, new_codename in old_permissions:
        old_permission = Permission.objects.filter(
            content_type=old_content_type,
            codename=old_codename,
        ).first()

        if old_permission is None:
            continue

        new_permission = permissions[new_codename]

        for group in old_permission.group_set.all():
            group.permissions.add(new_permission)

        for user in old_permission.user_set.all():
            user.user_permissions.add(new_permission)

        old_permission.delete()

    print("دسترسی‌های تیکت با موفقیت فارسی و یکپارچه شدند:")
    for name in labels.values():
        print(f"- {name}")


sync_permissions()
