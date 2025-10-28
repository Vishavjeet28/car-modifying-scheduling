import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from .services import CarModXAIAgent
from .models import ChatSession


class ChatView(View):
    """Main chat interface view."""
    
    def get(self, request):
        """Render the under development message."""
        return render(request, 'ai_agent/under_development.html')


@csrf_exempt
@require_http_methods(["POST"])
def chat_api(request):
    """API endpoint for chat interactions - currently disabled."""
    return JsonResponse({
        'error': 'AI Assistant is currently under development. Please check back soon!',
        'status': 'under_development'
    }, status=503)


@require_http_methods(["GET"])
def chat_history(request, session_id):
    """Get chat history for a session - currently disabled."""
    return JsonResponse({
        'error': 'AI Assistant is currently under development. Please check back soon!',
        'status': 'under_development'
    }, status=503)


@login_required
def my_chat_sessions(request):
    """View user's chat sessions - currently disabled."""
    return render(request, 'ai_agent/under_development.html')