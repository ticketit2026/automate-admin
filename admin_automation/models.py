from django.db import models
from django.contrib.auth.models import User


class InternalLetter(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='عنوان نامه'
    )

    content = models.TextField(
        verbose_name='متن نامه'
    )

    document_type = models.CharField(
        max_length=20,
        choices=[
            ('in', 'وارد'),
            ('out', 'صادره'),
            ('internal', 'داخلی')
        ],
        verbose_name='نوع نامه'
    )

    sent_to = models.CharField(
        max_length=200,
        verbose_name='گیرنده'
    )

    status = models.CharField(
        max_length=20,
        default='draft',
        choices=[
            ('draft', 'پیش‌نویس'),
            ('sent', 'ارسال شده'),
            ('received', 'دریافت شده'),
        ],
        verbose_name='وضعیت'
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
        verbose_name = 'نامه داخلی'
        verbose_name_plural = 'نامه‌های داخلی'
        ordering = ['-created_at']

    def __str__(self):
        return self.title