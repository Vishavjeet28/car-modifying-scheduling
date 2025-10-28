import json
import uuid
from typing import Dict, List, Optional
from django.conf import settings
from .models import ChatSession, ChatMessage, AIAgentConfig


class AIAgentService:
    """
    AI Agent service for handling chat interactions.
    This is a base implementation that can be extended with actual AI providers.
    """
    
    def __init__(self):
        self.config = self._get_active_config()
    
    def _get_active_config(self) -> Optional[AIAgentConfig]:
        """Get the active AI agent configuration."""
        try:
            return AIAgentConfig.objects.filter(is_active=True).first()
        except AIAgentConfig.DoesNotExist:
            return None
    
    def create_session(self, user=None) -> ChatSession:
        """Create a new chat session."""
        session_id = str(uuid.uuid4())
        return ChatSession.objects.create(
            user=user,
            session_id=session_id
        )
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get an existing chat session."""
        try:
            return ChatSession.objects.get(session_id=session_id, is_active=True)
        except ChatSession.DoesNotExist:
            return None
    
    def add_message(self, session: ChatSession, sender: str, message: str) -> ChatMessage:
        """Add a message to the chat session."""
        return ChatMessage.objects.create(
            session=session,
            sender=sender,
            message=message
        )
    
    def get_chat_history(self, session: ChatSession) -> List[Dict]:
        """Get chat history for a session."""
        messages = session.messages.all()
        return [
            {
                'sender': msg.sender,
                'message': msg.message,
                'timestamp': msg.timestamp.isoformat()
            }
            for msg in messages
        ]
    
    def generate_response(self, user_message: str, session: ChatSession) -> str:
        """
        Generate AI response. This is a placeholder implementation.
        Replace with actual AI service integration (OpenAI, Anthropic, etc.)
        """
        # Add user message to session
        self.add_message(session, 'user', user_message)
        
        # Simple rule-based responses for demo
        response = self._get_rule_based_response(user_message)
        
        # Add AI response to session
        self.add_message(session, 'ai', response)
        
        return response
    
    def _get_rule_based_response(self, message: str) -> str:
        """Simple rule-based responses for demonstration."""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['hello', 'hi', 'hey']):
            return "Hello! Welcome to CarModX. How can I help you with our car modification services today?"
        
        elif any(word in message_lower for word in ['service', 'services']):
            return "We offer various car modification services including performance upgrades, audio systems, paint jobs, and custom modifications. Would you like to see our full service catalog?"
        
        elif any(word in message_lower for word in ['book', 'appointment', 'schedule']):
            return "I can help you book an appointment! You can browse our services and select a time slot that works for you. Would you like me to guide you through the booking process?"
        
        elif any(word in message_lower for word in ['price', 'cost', 'pricing']):
            return "Our pricing varies depending on the service and your vehicle type. Each service page shows detailed pricing information. Which specific service are you interested in?"
        
        elif any(word in message_lower for word in ['hours', 'open', 'time']):
            return "Our shop hours vary by service type. Most appointments are available Monday through Saturday. You can check available time slots when booking an appointment."
        
        else:
            return "I'm here to help with information about our car modification services, booking appointments, and answering questions about CarModX. What would you like to know?"


class CarModXAIAgent(AIAgentService):
    """
    Specialized AI agent for CarModX with domain-specific knowledge.
    """
    
    def __init__(self):
        super().__init__()
        self.system_context = self._build_system_context()
    
    def _build_system_context(self) -> str:
        """Build system context with CarModX specific information."""
        return """
        You are an AI assistant for CarModX, a car modification service company.
        
        Services we offer:
        - Performance upgrades (engine tuning, exhaust systems, suspension)
        - Audio systems (speakers, amplifiers, subwoofers)
        - Paint and body work (custom paint jobs, wraps, body kits)
        - Interior modifications (seat upgrades, dashboard customization)
        - Lighting (LED upgrades, custom lighting)
        
        Key information:
        - We serve all vehicle types (cars, trucks, motorcycles)
        - Appointments can be booked online
        - We have certified mechanics and specialists
        - Pricing varies by vehicle type and complexity
        - We provide warranties on our work
        
        Be helpful, professional, and guide customers toward booking appointments or learning about services.
        """