"""Template tags for contact message system"""
from django import template
from main.models import ContactMessage

register = template.Library()


@register.simple_tag
def get_unread_contact_count():
    """Get count of unread contact messages"""
    return ContactMessage.objects.filter(is_read=False).count()
