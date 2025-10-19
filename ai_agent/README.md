# AI Agent for CarModX

This module adds an AI-powered chatbot assistant to the CarModX car modification service platform.

## Features

- **Interactive Chat Interface**: Clean, responsive chat UI for customer interactions
- **Session Management**: Persistent chat sessions for logged-in users
- **Rule-Based Responses**: Smart responses about services, booking, and general inquiries
- **Admin Interface**: Manage AI configurations and view chat logs
- **Extensible Architecture**: Ready for integration with real AI services

## Current Implementation

The AI agent currently uses rule-based responses but is designed to easily integrate with:
- OpenAI GPT models
- Anthropic Claude
- Google Gemini
- Other AI APIs

## Usage

### For Customers
1. Navigate to the "AI Assistant" link in the main navigation
2. Start chatting with questions about:
   - Available services
   - Booking appointments
   - Pricing information
   - General inquiries

### For Admins
1. Access Django admin panel
2. Go to "AI Agent" section to:
   - Configure AI settings
   - View chat sessions
   - Monitor conversations

## API Endpoints

- `GET /ai-agent/chat/` - Chat interface
- `POST /ai-agent/api/chat/` - Send message and get response
- `GET /ai-agent/api/history/<session_id>/` - Get chat history
- `GET /ai-agent/my-sessions/` - View user's chat sessions

## Integration with Real AI Services

To integrate with OpenAI GPT:

1. Install OpenAI package:
   ```bash
   pip install openai
   ```

2. Add your API key to settings:
   ```python
   OPENAI_API_KEY = 'your-api-key-here'
   ```

3. Update the `generate_response` method in `services.py`:
   ```python
   import openai
   
   def generate_response(self, user_message: str, session: ChatSession) -> str:
       client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
       
       response = client.chat.completions.create(
           model="gpt-3.5-turbo",
           messages=[
               {"role": "system", "content": self.system_context},
               {"role": "user", "content": user_message}
           ]
       )
       
       return response.choices[0].message.content
   ```

## Models

### ChatSession
- Manages individual chat sessions
- Links to users (optional for anonymous chats)
- Tracks session activity

### ChatMessage
- Stores individual messages
- Tracks sender (user/ai)
- Maintains conversation order

### AIAgentConfig
- Configures AI behavior
- Stores API keys and model settings
- Manages system prompts

## Customization

### Adding New Response Rules
Edit the `_get_rule_based_response` method in `services.py` to add new conversation patterns.

### Styling the Chat Interface
Modify `ai_agent/templates/ai_agent/chat.html` to customize the chat appearance.

### System Prompts
Update AI behavior through the Django admin interface or by modifying the default system prompt in the management command.

## Security Considerations

- API keys should be stored in environment variables
- Chat sessions are isolated per user
- Input validation prevents malicious content
- Rate limiting should be implemented for production use

## Future Enhancements

- Voice chat integration
- Multi-language support
- Advanced analytics
- Integration with booking system
- Proactive chat suggestions
- File upload support for vehicle images