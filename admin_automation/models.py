from django.db import models
from users.models import User

class InternalLetter(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    document_type = models.CharField(max_length=20, choices=[('in', 'وارد'), ('out', 'صادره'), ('internal', 'داخلی')])
    sent_to = models.CharField(max_length=200)
    status = models.CharField(max_length=20, default='draft')
    file = models.FileField(upload_to='letters/', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_letters')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title