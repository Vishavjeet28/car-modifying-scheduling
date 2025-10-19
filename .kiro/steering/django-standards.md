---
inclusion: always
---

# Django Development Standards for CarModX

## Project Context
CarModX is a Django-based car modification service platform with the following apps:
- `accounts` - User management with custom User model (Customer/Employee/Admin roles)
- `services` - Service catalog and management
- `appointments` - Booking and scheduling system
- `admin_panel` - Administrative interface
- `ai_agent` - AI assistant (currently under development)

## Code Standards

### Models
- Use descriptive model names (e.g., `ServiceCategory`, `AppointmentHistory`)
- Always include `__str__` methods for admin interface clarity
- Use `related_name` for reverse relationships
- Add `help_text` for complex fields
- Use `choices` for status fields with constants

### Views
- Prefer class-based views for CRUD operations
- Use function-based views for simple actions
- Always include proper permission checks
- Use `@login_required` or `LoginRequiredMixin` where appropriate
- Handle form validation properly with error messages

### Templates
- Extend `base.html` for consistent layout
- Use Bootstrap 5 classes for styling
- Include proper CSRF tokens in forms
- Use template tags for reusable components
- Follow responsive design principles

### URLs
- Use meaningful URL patterns with names
- Group related URLs in app-specific `urls.py`
- Use namespaces for app URLs
- Follow RESTful conventions where possible

### Security
- Never expose sensitive data in templates
- Use Django's built-in authentication system
- Validate all user inputs
- Use HTTPS in production settings
- Implement proper permission checks

### Database
- Use migrations for all schema changes
- Include data migrations when needed
- Use appropriate field types and constraints
- Index frequently queried fields
- Use select_related/prefetch_related for optimization

## Testing
- Write tests for all models, views, and forms
- Use Django's TestCase for database-dependent tests
- Mock external services and APIs
- Test both success and failure scenarios
- Maintain good test coverage

## File Organization
- Keep apps focused and cohesive
- Use consistent naming conventions
- Organize static files by app
- Keep templates in app-specific directories
- Use management commands for data operations