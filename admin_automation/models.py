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
        ('pending', 'در انتظار بررسی'),
        ('approved', 'تأیید شده'),
        ('rejected', 'رد شده'),
    ]

    title = models.CharField(
        max_length=200,
        verbose_name='عنوان نامه'
    )

    # شماره نامه
    # nullable گذاشته شده تا نامه‌های قدیمی بدون شماره
    # هنگام migration دچار مشکل نشوند.
    letter_number = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        verbose_name='شماره نامه'
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
        choices=STATUS_CHOICES,
        default='draft',
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

    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_letters_by_me',
        verbose_name='ارجاع توسط'
    )

    assigned_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='تاریخ ارجاع'
    )

    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_letters',
        verbose_name='تأیید توسط'
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='تاریخ تأیید'
    )

    rejected_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rejected_letters',
        verbose_name='رد توسط'
    )

    rejected_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='تاریخ رد'
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
            (
                'view_all_letters',
                'مشاهده همه نامه‌ها'
            ),
            (
                'create_letter',
                'ایجاد نامه'
            ),
            (
                'edit_letter',
                'ویرایش نامه'
            ),
            (
                'delete_letter',
                'حذف نامه'
            ),
            (
                'assign_letter',
                'ارجاع نامه'
            ),
            (
                'approve_letter',
                'تأیید نامه'
            ),
            (
                'reject_letter',
                'رد نامه'
            ),
        ]

    def __str__(self):
        if self.letter_number:
            return f'{self.letter_number} - {self.title}'

        return self.title
