
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from admin_automation.models import InternalLetter, LetterAttachment


class Command(BaseCommand):

    help = 'فارسی‌سازی دسترسی‌های نامه‌ها و پیوست‌های اداری'

    @transaction.atomic
    def handle(self, *args, **kwargs):

        # دسترسی‌های نامه اداری
        letter_permissions = {
            'view_internalletter': 'مشاهده نامه‌ها',
            'view_all_letters': 'مشاهده همه نامه‌ها',
            'create_letter': 'ایجاد نامه',
            'edit_letter': 'ویرایش نامه',
            'delete_letter': 'حذف نامه',
            'assign_letter': 'ارجاع نامه',
            'approve_letter': 'تأیید نامه',
            'reject_letter': 'رد نامه',
        }

        # دسترسی‌های پیوست تکمیلی نامه
        attachment_permissions = {
            'add_letterattachment': 'ایجاد پیوست تکمیلی نامه',
            'change_letterattachment': 'ویرایش پیوست تکمیلی نامه',
            'delete_letterattachment': 'حذف پیوست تکمیلی نامه',
            'view_letterattachment': 'مشاهده پیوست‌های تکمیلی نامه',
        }

        models_permissions = [
            (InternalLetter, letter_permissions),
            (LetterAttachment, attachment_permissions),
        ]

        permissions = {}

        for model, labels in models_permissions:

            content_type = ContentType.objects.get_for_model(model)

            for codename, persian_name in labels.items():

                permission, _ = Permission.objects.update_or_create(
                    content_type=content_type,
                    codename=codename,
                    defaults={
                        'name': persian_name,
                    }
                )

                permissions[codename] = permission

                self.stdout.write(
                    self.style.SUCCESS(
                        f'اصلاح شد: {persian_name}'
                    )
                )

        # انتقال دسترسی‌های قدیمی نامه به دسترسی‌های اختصاصی
        old_permissions = {
            'add_internalletter': 'create_letter',
            'change_internalletter': 'edit_letter',
            'delete_internalletter': 'delete_letter',
        }

        letter_content_type = ContentType.objects.get_for_model(
            InternalLetter
        )

        for old_code, new_code in old_permissions.items():

            old_permission = Permission.objects.filter(
                content_type=letter_content_type,
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
                'تمام دسترسی‌های نامه و پیوست با موفقیت فارسی شدند.'
            )
        )
