from django.db import models
from django.contrib.auth.models import User


class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video_id = models.CharField(max_length=20, blank=True, null=True)
    title = models.CharField(max_length=35, blank=True, null=True)
    transcript_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    SESSION_SENDER = [
        ('user', 'User'),
        ('bot', 'Bot'),
    ]

    chat_session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=10, choices=SESSION_SENDER)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
