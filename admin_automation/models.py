from django.db import models
from django.contrib.auth.models import User


class InternalLetter(models.Model):

    DOCUMENT_TYPE_CHOICES = [
        ('in', 'نامه وارده'),
        ('out', 'نامه صادره'),
        ('internal', 'نامه داخلی'),
    ]

    STATUS_CHOICES = [
        ('draft', 'پیش‌نویس'),
        ('sent', 'ارسال شده'),
        ('received', 'دریافت شده'),
    ]

    title = models.CharField(
        max_length=200,
        verbose_name='عنوان نامه'
    )

    content = models.TextField(
        verbose_name='متن نامه'
    )

    document_type = models.CharField(
        max_length=20,
        choices=DOCUMENT_TYPE_CHOICES,
        verbose_name='نوع نامه'
    )

    sent_to = models.CharField(
        max_length=200,
        verbose_name='گیرنده'
    )

    status = models.CharField(
        max_length=20,
        default='draft',
        choices=STATUS_CHOICES,
        verbose_name='وضعیت'
    )

    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_letters',
        verbose_name='ارجاع به'
    )

    file = models.FileField(
        upload_to='letters/',
        null=True,
        blank=True,
        verbose_name='فایل پیوست'
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_letters',
        verbose_name='ایجادکننده'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='آخرین ویرایش'
    )

    class Meta:

        verbose_name = 'نامه اداری'
        verbose_name_plural = 'نامه‌های اداری'

        ordering = ['-created_at']

        permissions = [
            ('view_all_letters', 'مشاهده همه نامه‌ها'),
            ('create_letter', 'ایجاد نامه'),
            ('edit_letter', 'ویرایش نامه'),
            ('delete_letter', 'حذف نامه'),
            ('send_letter', 'ارسال نامه'),
            ('assign_letter', 'ارجاع نامه'),
        ]

    def __str__(self):
        return self.title
