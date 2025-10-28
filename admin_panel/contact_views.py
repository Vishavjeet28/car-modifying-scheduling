from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from main.models import ContactMessage
from admin_panel.decorators import super_user_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, UpdateView
from django.urls import reverse_lazy


@method_decorator(super_user_required, name='dispatch')
class ContactMessageListView(ListView):
    """View for listing all contact messages"""
    model = ContactMessage
    template_name = 'admin_panel/contact/message_list.html'
    context_object_name = 'messages'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = ContactMessage.objects.all()
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(email__icontains=search) |
                Q(subject__icontains=search) |
                Q(message__icontains=search)
            )
        
        # Filter by read status
        status = self.request.GET.get('status')
        if status == 'unread':
            queryset = queryset.filter(is_read=False)
        elif status == 'read':
            queryset = queryset.filter(is_read=True)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_messages'] = ContactMessage.objects.count()
        context['unread_count'] = ContactMessage.objects.filter(is_read=False).count()
        context['read_count'] = ContactMessage.objects.filter(is_read=True).count()
        context['search_query'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status', '')
        return context


@method_decorator(super_user_required, name='dispatch')
class ContactMessageDetailView(DetailView):
    """View for displaying a single contact message"""
    model = ContactMessage
    template_name = 'admin_panel/contact/message_detail.html'
    context_object_name = 'message'
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        # Mark as read when viewed
        if not self.object.is_read:
            self.object.is_read = True
            self.object.save()
        return response


@method_decorator(super_user_required, name='dispatch')
class ContactMessageUpdateView(UpdateView):
    """View for updating contact message (admin notes and status)"""
    model = ContactMessage
    template_name = 'admin_panel/contact/message_update.html'
    fields = ['is_read', 'admin_notes']
    
    def get_success_url(self):
        return reverse_lazy('admin_panel:contact_message_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Contact message updated successfully!')
        return super().form_valid(form)


@super_user_required
def mark_as_read(request, pk):
    """Mark a message as read"""
    message = get_object_or_404(ContactMessage, pk=pk)
    message.is_read = True
    message.save()
    messages.success(request, f'Message from {message.name} marked as read.')
    return redirect('admin_panel:contact_message_detail', pk=pk)


@super_user_required
def mark_as_unread(request, pk):
    """Mark a message as unread"""
    message = get_object_or_404(ContactMessage, pk=pk)
    message.is_read = False
    message.save()
    messages.success(request, f'Message from {message.name} marked as unread.')
    return redirect('admin_panel:contact_message_detail', pk=pk)


@super_user_required
def delete_message(request, pk):
    """Delete a contact message"""
    message = get_object_or_404(ContactMessage, pk=pk)
    name = message.name
    message.delete()
    messages.success(request, f'Message from {name} has been deleted.')
    return redirect('admin_panel:contact_messages')
