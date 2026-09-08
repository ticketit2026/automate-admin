from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE = [
        ('admin', 'مدیر'),
        ('employee', 'کارمند'),
        ('it', 'IT'),
        ('manager', 'مدیر'),
    ]
    role = models.CharField(max_length=10, choices=ROLE, default='employee')
    department = models.CharField(max_length=100, blank=True)