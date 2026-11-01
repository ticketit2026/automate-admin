
from django.db import models
from django.contrib.auth.models import User


class Ticket(models.Model):
    STATUS_CHOICES = [
        ("open", "باز"),
        ("in_progress", "در حال بررسی"),
        ("closed", "بسته شده"),
    ]

    PRIORITY_CHOICES = [
        ("low", "پایین"),
        ("medium", "متوسط"),
        ("high", "بالا"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="open",
    )

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default="medium",
    )

    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tickets",
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_tickets",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
    verbose_name = 'تیکت'
    verbose_name_plural = 'تیکت‌ها'

    # تعریف دستی دسترسی‌ها
    default_permissions = ()

    permissions = [
        ('add_ticket', 'ایجاد تیکت'),
        ('view_ticket', 'مشاهده تیکت'),
        ('view_all_tickets', 'مشاهده همه تیکت‌ها'),
        ('change_ticket', 'ویرایش تیکت'),
        ('delete_ticket', 'حذف تیکت'),
        ('reply_ticket', 'جواب دادن به تیکت'),
        ('assign_ticket', 'ارجاع تیکت'),
    ]
    
    def __str__(self):
        return self.title


class TicketReply(models.Model):
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="replies",
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"پاسخ به تیکت #{self.ticket_id} "
            f"توسط {self.user.username}"
        )
