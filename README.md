# CarModX - Car Modification Store Web App

A comprehensive Django-based web application for car modification services, allowing customers to view services, book appointments, and enabling employees to manage appointments through an internal dashboard.

## Features

### Customer Features
- **Service Catalog**: Browse and search car modification services
- **Appointment Booking**: Book appointments with date/time selection
- **User Authentication**: Register and login system
- **Dashboard**: View upcoming appointments and booking history
- **Service Details**: Detailed information about each service

### Employee Features
- **Employee Dashboard**: View assigned appointments
- **Appointment Management**: Confirm, update, and complete appointments
- **Schedule Management**: View daily and upcoming appointments

### Admin Features
- **Admin Panel**: Full Django admin interface
- **User Management**: Manage customers and employees
- **Service Management**: Add, edit, and manage services
- **Appointment Oversight**: View and manage all appointments
- **Analytics**: System usage and appointment statistics

## Technology Stack

- **Backend**: Django 4.2.7
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: Django Templates with Bootstrap 5
- **Styling**: Custom CSS with Bootstrap components
- **Forms**: Django Crispy Forms with Bootstrap 5
- **Authentication**: Django's built-in authentication system

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd carmodx
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run migrations**
   ```bash
   python manage.py migrate
   ```

4. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

5. **Populate sample data (optional)**
   ```bash
   python populate_data.py
   ```

6. **Run development server**
   ```bash
   python manage.py runserver
   ```

## Default Credentials

- **Admin User**: 
  - Username: `admin`
  - Password: `admin123`
  - Role: Admin

- **Sample Employees**:
  - Username: `john_mechanic` / Password: `employee123`
  - Username: `sarah_painter` / Password: `employee123`
  - Username: `mike_audio` / Password: `employee123`

## Project Structure

```
carmodx/
├── accounts/           # User management and authentication
├── services/           # Service catalog and management
├── appointments/       # Appointment booking and management
├── templates/          # HTML templates
├── static/            # CSS, JS, and images
├── carmodx/           # Main project settings
└── manage.py          # Django management script
```

## Models

### User Model (Custom)
- Extended Django User model with role-based access
- Roles: Customer, Employee, Admin
- Additional fields: phone_number, address, role

### Service Models
- **ServiceCategory**: Organize services by type
- **Service**: Individual services with pricing and duration
- **ServicePrice**: Dynamic pricing based on vehicle type/complexity

### Appointment Models
- **Appointment**: Main booking model with vehicle and service details
- **TimeSlot**: Available time slots for appointments
- **AppointmentHistory**: Track changes to appointments

### Employee Model
- Employee profiles linked to User accounts
- Specialization and hire date tracking

## Key Features Implementation

### Role-Based Access Control
- Different dashboards for customers, employees, and admins
- Permission-based view access
- Custom authentication and redirects

### Appointment System
- Time slot management with availability tracking
- Multi-step booking process
- Status tracking (pending, confirmed, in-progress, completed, cancelled)

### Service Management
- Category-based organization
- Dynamic pricing options
- Image support for services

### Responsive Design
- Mobile-friendly Bootstrap 5 interface
- Custom CSS for enhanced styling
- Modern UI/UX design

## API Endpoints

### Authentication
- `/accounts/login/` - User login
- `/accounts/register/` - User registration
- `/accounts/logout/` - User logout

### Services
- `/services/` - Service catalog
- `/services/<id>/` - Service details
- `/services/<id>/book/` - Book service

### Appointments
- `/appointments/select-time-slot/` - Time slot selection
- `/appointments/<id>/` - Appointment details
- `/appointments/<id>/update/` - Update appointment

### Admin
- `/admin/` - Django admin interface

## Future Enhancements

### Phase 2
- Email/SMS notifications for bookings
- Online payments integration (Razorpay/Stripe)
- Advanced search and filtering

### Phase 3
- Mobile app with REST API
- Customer reviews and ratings
- Service gallery
- Google Calendar integration

## Development

### Running Tests
```bash
python manage.py test
```

### Creating Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Static Files
```bash
python manage.py collectstatic
```

## Deployment

### Production Settings
- Update `DEBUG = False` in settings.py
- Configure production database (PostgreSQL recommended)
- Set up static file serving
- Configure email settings for notifications

### Environment Variables
- `SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode (True/False)
- `DATABASE_URL`: Database connection string
- `EMAIL_HOST`: SMTP server for emails

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please contact the development team or create an issue in the repository.
# car-modifying-scheduling
