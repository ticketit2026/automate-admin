from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from helpdesk.models import Ticket


class Command(BaseCommand):

    help = 'ایجاد و یکسان‌سازی دسترسی‌های تیکت به زبان فارسی'

    def handle(self, *args, **kwargs):

        permissions = {
            'add_ticket': 'ایجاد تیکت',
            'view_ticket': 'مشاهده تیکت',
            'view_all_tickets': 'مشاهده همه تیکت‌ها',
            'change_ticket': 'ویرایش تیکت',
            'delete_ticket': 'حذف تیکت',
            'reply_ticket': 'جواب دادن به تیکت',
            'assign_ticket': 'ارجاع تیکت',
        }

        content_type = ContentType.objects.get_for_model(Ticket)

        for codename, persian_name in permissions.items():

            permission, created = Permission.objects.update_or_create(
                content_type=content_type,
                codename=codename,
                defaults={
                    'name': persian_name,
                }
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'دسترسی ایجاد شد: {persian_name}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'نام دسترسی اصلاح شد: {persian_name}'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                'تمام دسترسی‌های تیکت با موفقیت بررسی شدند.'
            )
        )