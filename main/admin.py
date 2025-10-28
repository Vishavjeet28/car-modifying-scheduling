from django.contrib import admin
from .models import ContactMessage


# Contact messages are managed through the custom admin panel only
# To access contact messages, log in as a super user and go to:
# Admin Panel → Communication → Contact Messages
#
# This ensures that contact messages are only accessible to super admins
# and super employees, not through the standard Django admin interface.
#
# Uncomment the code below if you need to manage messages through Django admin:

# @admin.register(ContactMessage)
# class ContactMessageAdmin(admin.ModelAdmin):
#     """Admin interface for contact messages"""
#     list_display = ['name', 'email', 'subject', 'created_at', 'is_read']
#     list_filter = ['is_read', 'created_at']
#     search_fields = ['name', 'email', 'subject', 'message']
#     readonly_fields = ['name', 'email', 'phone', 'subject', 'message', 'created_at']
#     ordering = ['-created_at']
#     
#     fieldsets = (
#         ('Contact Information', {
#             'fields': ('name', 'email', 'phone')
#         }),
#         ('Message Details', {
#             'fields': ('subject', 'message', 'created_at')
#         }),
#         ('Status & Notes', {
#             'fields': ('is_read', 'admin_notes')
#         }),
#     )
#     
#     actions = ['mark_as_read', 'mark_as_unread']
#     
#     def mark_as_read(self, request, queryset):
#         """Mark selected messages as read"""
#         updated = queryset.update(is_read=True)
#         self.message_user(request, f'{updated} message(s) marked as read.')
#     mark_as_read.short_description = "Mark selected messages as read"
#     
#     def mark_as_unread(self, request, queryset):
#         """Mark selected messages as unread"""
#         updated = queryset.update(is_read=False)
#         self.message_user(request, f'{updated} message(s) marked as unread.')
#     mark_as_unread.short_description = "Mark selected messages as unread"
