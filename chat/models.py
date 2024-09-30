# Create your models here.
from django.db import models
from django.utils import timezone

class ChatMessage(models.Model):
    sender = models.CharField(max_length=255)
    receiver = models.CharField(max_length=255)
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'From {self.sender} to {self.receiver}: {self.message}'