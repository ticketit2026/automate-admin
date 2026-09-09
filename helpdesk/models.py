from django.db import models
from django.contrib.auth.models import User


class Ticket(models.Model):

    title = models.CharField(max_length=200)

    description = models.TextField()

    status = models.CharField(
        max_length=20,
        default='open'
    )

    priority = models.CharField(
        max_length=10,
        choices=[
            ('low', 'پایین'),
            ('medium', 'متوسط'),
            ('high', 'بالا'),
        ]
    )

    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets'
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_tickets'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.title
