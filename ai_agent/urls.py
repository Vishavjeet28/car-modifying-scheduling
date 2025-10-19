from django.urls import path
from . import views

app_name = 'ai_agent'

urlpatterns = [
    path('chat/', views.ChatView.as_view(), name='chat'),
    path('api/chat/', views.chat_api, name='chat_api'),
    path('api/history/<str:session_id>/', views.chat_history, name='chat_history'),
    path('my-sessions/', views.my_chat_sessions, name='my_sessions'),
]