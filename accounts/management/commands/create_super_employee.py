from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Employee, User
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a super employee for testing the management system'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username for the super employee')
        parser.add_argument('--password', type=str, help='Password for the super employee')
        parser.add_argument('--email', type=str, help='Email for the super employee')

    def handle(self, *args, **options):
        username = options.get('username') or 'superemployee'
        password = options.get('password') or 'manager123'
        email = options.get('email') or 'superemployee@carmodx.com'

        # Check if user already exists
        try:
            user = User.objects.get(username=username)
            self.stdout.write(
                self.style.WARNING(f'User {username} already exists. Updating to super employee...')
            )
        except User.DoesNotExist:
            # Create new user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name='Super',
                last_name='Employee',
                role='employee'
            )
            self.stdout.write(
                self.style.SUCCESS(f'Created new user: {username}')
            )

        # Check if employee profile exists
        try:
            employee = user.employee_profile
            employee.employee_type = 'super'
            employee.specialization = 'Management & Supervision'
            employee.current_status = 'available'
            employee.save()
            self.stdout.write(
                self.style.SUCCESS(f'Updated employee profile to super employee')
            )
        except Employee.DoesNotExist:
            # Create employee profile
            employee = Employee.objects.create(
                user=user,
                employee_id=f"SUPER{user.id:03d}",
                employee_type='super',
                specialization='Management & Supervision',
                hire_date=timezone.now().date(),
                is_active=True,
                current_status='available'
            )
            self.stdout.write(
                self.style.SUCCESS(f'Created super employee profile: {employee.employee_id}')
            )

        # Create some regular employees if they don't exist
        regular_employees_data = [
            {
                'username': 'employee1',
                'password': 'emp123',
                'email': 'emp1@carmodx.com',
                'first_name': 'John',
                'last_name': 'Mechanic',
                'specialization': 'Engine Repair'
            },
            {
                'username': 'employee2', 
                'password': 'emp123',
                'email': 'emp2@carmodx.com',
                'first_name': 'Jane',
                'last_name': 'Technician',
                'specialization': 'Body Work'
            },
            {
                'username': 'employee3',
                'password': 'emp123', 
                'email': 'emp3@carmodx.com',
                'first_name': 'Mike',
                'last_name': 'Painter',
                'specialization': 'Paint & Detailing'
            }
        ]

        for emp_data in regular_employees_data:
            try:
                emp_user = User.objects.get(username=emp_data['username'])
                self.stdout.write(f"Regular employee {emp_data['username']} already exists")
            except User.DoesNotExist:
                # Create regular employee
                emp_user = User.objects.create_user(
                    username=emp_data['username'],
                    email=emp_data['email'],
                    password=emp_data['password'],
                    first_name=emp_data['first_name'],
                    last_name=emp_data['last_name'],
                    role='employee'
                )

                # Create employee profile
                Employee.objects.create(
                    user=emp_user,
                    employee_id=f"EMP{emp_user.id:04d}",
                    employee_type='regular',
                    specialization=emp_data['specialization'],
                    hire_date=timezone.now().date(),
                    is_active=True,
                    current_status='available',
                    supervisor=employee  # Set super employee as supervisor
                )
                
                self.stdout.write(
                    self.style.SUCCESS(f'Created regular employee: {emp_data["username"]}')
                )

        self.stdout.write(
            self.style.SUCCESS('\n=== SUPER EMPLOYEE SETUP COMPLETE ===')
        )
        self.stdout.write(f'Username: {username}')
        self.stdout.write(f'Password: {password}')
        self.stdout.write(f'Employee ID: {employee.employee_id}')
        self.stdout.write(f'Login URL: http://localhost:8000/accounts/login/')
        self.stdout.write('\nThe super employee can now:')
        self.stdout.write('- View and manage all employees')
        self.stdout.write('- Assign tasks to employees')
        self.stdout.write('- Update employee status')
        self.stdout.write('- Monitor work progress')