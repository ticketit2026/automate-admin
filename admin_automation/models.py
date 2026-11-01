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

        default_permissions = ('view',)

        permissions = [
            ('create_letter', 'ایجاد نامه'),
            ('view_all_letters', 'مشاهده همه نامه‌ها'),
            ('edit_letter', 'ویرایش نامه'),
            ('delete_letter', 'حذف نامه'),
            ('assign_letter', 'ارجاع نامه'),
            ('approve_letter', 'تأیید نامه'),
            ('reject_letter', 'رد نامه'),
        ]

    def __str__(self):
        if self.letter_number:
            return f'{self.letter_number} - {self.title}'
        return self.title
