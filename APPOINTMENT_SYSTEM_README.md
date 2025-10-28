# CarModX Appointment Scheduling System

## Overview

This implementation provides a 2-hour gap appointment scheduling system for the CarModX car modification service platform. The system enforces a 5-car limit per time slot and prevents duplicate bookings.

## Features

### ✅ Core Requirements Implemented

1. **Operating Hours**: 9:00 AM to 7:00 PM
2. **Time Slots**: 2-hour gaps with 5 predefined slots:
   - 9:00 AM
   - 11:00 AM  
   - 1:00 PM
   - 3:00 PM
   - 5:00 PM

3. **Slot Capacity**: Maximum 5 bookings per time slot
4. **Booking Limits**: 
   - No more than 5 cars per slot
   - One appointment per customer per date
5. **Dynamic Availability**: Real-time slot availability calculation
6. **Status Management**: Three status values (booked, cancelled, completed)

### ✅ Frontend Features

1. **Dropdown Selection**: Time slots displayed in dropdown menu
2. **Dynamic Loading**: Available slots fetched via AJAX when date is selected
3. **Real-time Updates**: Slot availability updates based on current bookings
4. **Responsive Design**: Bootstrap 5 styling for mobile compatibility

### ✅ Backend Logic

1. **Server-side Validation**: Prevents overbooking and duplicate appointments
2. **Django ORM**: Efficient database queries with proper relationships
3. **API Endpoint**: `/api/available-slots/` for AJAX requests
4. **Management Command**: Daily cleanup of old cancelled appointments

## File Structure

```
appointments/
├── models.py              # Simplified Appointment model
├── views.py               # Booking views and API endpoints
├── forms.py               # Booking and search forms
├── urls.py                # URL routing
├── admin.py               # Django admin interface
├── management/
│   └── commands/
│       └── reset_daily_slots.py  # Daily maintenance command
└── templates/appointments/
    ├── book_appointment.html      # Main booking form
    ├── my_appointments.html       # Customer appointment list
    ├── appointment_detail.html    # Appointment details
    ├── appointment_list.html      # Staff appointment list
    ├── cancel_appointment.html    # Cancellation form
    └── update_status.html         # Status update form
```

## Model Structure

### Appointment Model
```python
class Appointment(models.Model):
    # Core fields
    customer = ForeignKey(User)
    selected_service = ForeignKey(Service)
    slot_date = DateField()
    slot_time = CharField(choices=TIME_SLOT_CHOICES)
    status = CharField(choices=STATUS_CHOICES)
    
    # Vehicle details
    vehicle_make = CharField(max_length=50)
    vehicle_model = CharField(max_length=50)
    vehicle_year = PositiveIntegerField()
    vehicle_license = CharField(max_length=20)
    
    # Additional
    special_requirements = TextField(blank=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    
    # Constraints
    class Meta:
        unique_together = [('customer', 'slot_date')]
```

## Key Methods

### Slot Availability
```python
@classmethod
def get_available_slots(cls, selected_date):
    """Returns available time slots for a given date"""
    
@classmethod  
def get_slot_capacity(cls, selected_date, slot_time):
    """Returns remaining capacity for a specific slot"""
```

### Validation
```python
def clean(self):
    """Validates appointment constraints"""
    # Prevents past date bookings
    # Checks slot capacity (max 5)
    # Prevents duplicate customer bookings on same date
```

## URL Patterns

```python
urlpatterns = [
    path('book/', views.book_appointment_view, name='book_appointment'),
    path('my-appointments/', views.my_appointments_view, name='my_appointments'),
    path('list/', views.appointment_list_view, name='appointment_list'),
    path('<int:appointment_id>/', views.appointment_detail_view, name='appointment_detail'),
    path('<int:appointment_id>/cancel/', views.cancel_appointment_view, name='cancel_appointment'),
    path('<int:appointment_id>/update-status/', views.update_appointment_status_view, name='update_status'),
    path('api/available-slots/', views.get_available_slots_api, name='available_slots_api'),
]
```

## API Endpoints

### Get Available Slots
```
GET /appointments/api/available-slots/?date=2025-10-15

Response:
{
    "slots": [
        {"time": "09:00", "display": "9:00 AM", "remaining": 5},
        {"time": "11:00", "display": "11:00 AM", "remaining": 3},
        {"time": "13:00", "display": "1:00 PM", "remaining": 5},
        {"time": "15:00", "display": "3:00 PM", "remaining": 1},
        {"time": "17:00", "display": "5:00 PM", "remaining": 5}
    ],
    "date": "2025-10-15"
}
```

## Usage Examples

### Customer Booking Flow
1. Customer visits `/appointments/book/`
2. Selects service and fills vehicle details
3. Chooses date - AJAX loads available time slots
4. Selects time slot from dropdown
5. Submits form - server validates and creates appointment

### Staff Management
1. Staff can view all appointments at `/appointments/list/`
2. Search and filter by customer, service, date, status
3. Update appointment status via `/appointments/<id>/update-status/`
4. View detailed appointment information

### Customer Self-Service
1. Customers view their appointments at `/appointments/my-appointments/`
2. Can cancel future appointments
3. View appointment details and service information

## Validation Rules

1. **Date Validation**: No past dates, max 30 days in advance
2. **Slot Capacity**: Maximum 5 bookings per time slot
3. **Duplicate Prevention**: One appointment per customer per date
4. **Status Constraints**: Only 'booked' appointments can be cancelled

## Testing

Run the test script to verify system functionality:
```bash
python test_appointment_system.py
```

The test covers:
- Slot availability calculation
- Appointment booking
- Capacity limits
- Duplicate booking prevention
- Full slot handling

## Scalability Features

1. **Efficient Queries**: Uses select_related for optimized database access
2. **Pagination**: Large appointment lists are paginated
3. **AJAX Loading**: Reduces page reloads for better UX
4. **Indexed Fields**: Database indexes on frequently queried fields
5. **Management Commands**: Automated cleanup of old data

## Future Enhancements

1. **Email Notifications**: Send booking confirmations and reminders
2. **SMS Integration**: Text message notifications
3. **AI Recommendations**: Suggest optimal time slots based on service type
4. **Calendar Integration**: Export appointments to calendar apps
5. **Multi-location Support**: Handle multiple service locations
6. **Advanced Scheduling**: Handle services requiring multiple time slots

## Installation & Setup

1. Ensure appointments app is in INSTALLED_APPS
2. Run migrations: `python manage.py migrate appointments`
3. Create superuser and add services via admin
4. Access booking form at `/appointments/book/`

## Dependencies

- Django 4.2+
- Bootstrap 5 (for styling)
- JavaScript (for AJAX functionality)
- Django Crispy Forms (optional, for better form rendering)

---

This implementation provides a robust, scalable appointment scheduling system that meets all specified requirements while maintaining clean, maintainable code following Django best practices.