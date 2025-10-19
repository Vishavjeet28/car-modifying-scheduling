from django.db import models
from django.conf import settings


class ChatSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Chat Session {self.session_id}"


class ChatMessage(models.Model):
    SENDER_CHOICES = [
        ('user', 'User'),
        ('ai', 'AI Agent'),
    ]
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender}: {self.message[:50]}..."


class AIAgentConfig(models.Model):
    name = models.CharField(max_length=100, unique=True)
    api_key = models.CharField(max_length=255, blank=True)
    model_name = models.CharField(max_length=100, default='gpt-3.5-turbo')
    system_prompt = models.TextField(default="You are a helpful assistant for CarModX car modification services.")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name