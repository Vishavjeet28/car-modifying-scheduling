from django.contrib import admin
from .models import ChatSession, ChatMessage, AIAgentConfig


@admin.register(AIAgentConfig)
class AIAgentConfigAdmin(admin.ModelAdmin):
    list_display = ['name', 'model_name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'model_name']


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ['timestamp']


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'user', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['session_id', 'user__username']
    inlines = [ChatMessageInline]


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'sender', 'message_preview', 'timestamp']
    list_filter = ['sender', 'timestamp']
    search_fields = ['message', 'session__session_id']
    
    def message_preview(self, obj):
        return obj.message[:50] + "..." if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message Preview'