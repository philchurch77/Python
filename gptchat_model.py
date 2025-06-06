from django.db import models
from django.contrib.auth.models import User

from django.db import models

class ChatTurn(models.Model):
    session_id = models.CharField(max_length=100)
    role = models.CharField(max_length=10, choices=[("user", "User"), ("assistant", "Assistant")])
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.timestamp} | {self.role}: {self.content[:50]}"

class TrainingSummary(models.Model):
    title = models.CharField(max_length=255)
    school_or_trust = models.CharField(max_length=255)
    staff_involved = models.TextField()
    summary_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.created_at.strftime('%Y-%m-%d')})"

