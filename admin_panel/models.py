from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone


class AdminLog(models.Model):
    """
    Model to track all admin actions for audit trail
    """
    admin_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='admin_logs'
    )
    action = models.CharField(max_length=100)
    content_type = models.ForeignKey(
        ContentType, 
        on_delete=models.CASCADE,
        null=True, 
        blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    object_repr = models.CharField(max_length=200, blank=True)
    change_message = models.TextField(blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    extra_data = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Admin Log Entry'
        verbose_name_plural = 'Admin Log Entries'
    
    def __str__(self):
        return f"{self.admin_user.username} - {self.action} - {self.timestamp}"


class SystemSettings(models.Model):
    """
    Model for storing system-wide configuration settings
    """
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='system_settings_updates'
    )
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['key']
        verbose_name = 'System Setting'
        verbose_name_plural = 'System Settings'
    
    def __str__(self):
        return f"{self.key}: {self.value[:50]}..."
