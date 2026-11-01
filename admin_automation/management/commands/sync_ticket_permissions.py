
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from admin_automation.models import InternalLetter


class Command(BaseCommand):
    help = 'یکپارچه‌سازی دسترسی‌های نامه‌های اداری به زبان فارسی'

    @transaction.atomic
    def handle(self, *args, **kwargs):

        content_type = ContentType.objects.get_for_model(
            InternalLetter
        )

        labels = {
            'view_internalletter': 'مشاهده نامه‌ها',
            'view_all_letters': 'مشاهده همه نامه‌ها',
            'create_letter': 'ایجاد نامه',
            'edit_letter': 'ویرایش نامه',
            'delete_letter': 'حذف نامه',
            'assign_letter': 'ارجاع نامه',
            'approve_letter': 'تأیید نامه',
            'reject_letter': 'رد نامه',
        }

        permissions = {}

        # ایجاد دسترسی‌ها یا اصلاح نام فارسی آن‌ها
        for codename, persian_name in labels.items():

            permission, _ = Permission.objects.update_or_create(
                content_type=content_type,
                codename=codename,
                defaults={
                    'name': persian_name,
                }
            )

            permissions[codename] = permission

        # انتقال دسترسی‌های قدیمی Django به دسترسی‌های جدید
        old_permissions = {
            'add_internalletter': 'create_letter',
            'change_internalletter': 'edit_letter',
            'delete_internalletter': 'delete_letter',
        }

        for old_code, new_code in old_permissions.items():

            old_permission = Permission.objects.filter(
                content_type=content_type,
                codename=old_code,
            ).first()

            if old_permission is None:
                continue

            new_permission = permissions[new_code]

            # انتقال دسترسی گروه‌ها
            for group in old_permission.group_set.all():
                group.permissions.add(new_permission)

            # انتقال دسترسی مستقیم کاربران
            for user in old_permission.user_set.all():
                user.user_permissions.add(new_permission)

            # حذف دسترسی قدیمی پس از انتقال
            old_permission.delete()

        self.stdout.write(
            self.style.SUCCESS(
                'دسترسی‌های نامه‌های اداری با موفقیت فارسی و یکپارچه شدند.'
            )
        )

        for name in labels.values():
            self.stdout.write(f'- {name}')
