# CarModX - Car Modification Scheduling System
## Complete User Guide

---

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [User Roles](#user-roles)
4. [Customer Features](#customer-features)
5. [Employee Features](#employee-features)
6. [Super Employee (Manager) Features](#super-employee-manager-features)
7. [Admin Panel Features](#admin-panel-features)
8. [Common Tasks](#common-tasks)
9. [Troubleshooting](#troubleshooting)

---

## Introduction

**CarModX** is a comprehensive car modification and service scheduling system that allows customers to book appointments for various car services, employees to manage their work, and administrators to oversee the entire operation.

### Key Features:
- ✅ Online appointment booking with real-time slot availability
- ✅ Multiple service categories (Paint Jobs, Audio Systems, Body Modifications, etc.)
- ✅ Role-based access control (Customer, Employee, Super Employee, Admin)
- ✅ Task assignment and progress tracking
- ✅ Performance metrics and analytics
- ✅ Automated notifications and status updates

---

## Getting Started

### System Requirements
- Python 3.13+
- Django 4.2.7
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Installation Steps

1. **Clone the repository**
```bash
git clone https://github.com/Vishavjeet28/car-modifying-scheduling.git
cd car-modifying-scheduling
```

2. **Create virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# OR
.venv\Scripts\activate  # On Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run migrations**
```bash
python manage.py migrate
```

5. **Create superuser (Admin)**
```bash
python manage.py createsuperuser
```

6. **Start the development server**
```bash
python manage.py runserver 8000
```

7. **Access the application**
```
http://127.0.0.1:8000/
```

---

## User Roles

The system supports four different user roles:

### 1. **Customer**
- Book appointments for car services
- View appointment history
- Cancel appointments
- Manage profile

### 2. **Regular Employee**
- View assigned tasks
- Accept and complete work assignments
- Track work progress
- Update work status

### 3. **Super Employee (Manager)**
- All regular employee features
- Assign tasks to other employees
- Monitor team performance
- Manage employee workload
- View team statistics

### 4. **Admin (Store Owner)**
- Full system access
- Manage employees
- Manage services
- View analytics and reports
- System configuration

---

## Customer Features

### 📸 Screenshot Locations:
- [ ] Home page
- [ ] Registration page
- [ ] Login page
- [ ] Customer dashboard
- [ ] Service catalog
- [ ] Booking form
- [ ] Appointment confirmation

### How to Use as a Customer:

#### 1. **Registration** (`http://127.0.0.1:8000/accounts/register/`)
- Navigate to the registration page
- Fill in your details:
  - First Name
  - Last Name
  - Username
  - Email
  - Password
- Select "Customer" as your account type
- Click "Register"

#### 2. **Login** (`http://127.0.0.1:8000/accounts/login/`)
- Enter your username and password
- Click "Sign In"
- You'll be redirected to the customer dashboard

#### 3. **Browse Services** (`http://127.0.0.1:8000/services/`)
- View all available services
- Filter by category
- See pricing and duration
- Click on a service for details

#### 4. **Book an Appointment** (`http://127.0.0.1:8000/services/<service_id>/book/`)

**Step-by-Step Booking Process:**

a. **Select Service**
   - Click "Book Now" on any service

b. **Choose Date**
   - Select your preferred date from the calendar
   - Only future dates are available

c. **Select Time Slot**
   - Available time slots will appear
   - Occupied slots are grayed out
   - Click on an available slot to select it

d. **Enter Vehicle Details**
   - Vehicle Make (e.g., Toyota)
   - Vehicle Model (e.g., Camry)
   - Vehicle Year (e.g., 2020)
   - License Plate Number

e. **Add Special Requirements** (Optional)
   - Any specific instructions or requirements

f. **Review and Confirm**
   - Check the booking summary
   - Click "Confirm Booking"

g. **Confirmation**
   - You'll receive a confirmation with appointment ID
   - Appointment details will be displayed

#### 5. **View Appointments** (`http://127.0.0.1:8000/appointments/my-appointments/`)
- See all your appointments
- Filter by status (Booked, Completed, Cancelled)
- View appointment details
- Cancel appointments if needed

#### 6. **Cancel Appointment**
- Navigate to appointment details
- Click "Cancel Appointment"
- Confirm cancellation
- Note: Only bookings with status "Booked" can be cancelled

---

## Employee Features

### 📸 Screenshot Locations:
- [ ] Employee login
- [ ] Employee dashboard
- [ ] Task assignments list
- [ ] Work in progress view
- [ ] Work completion form

### How to Use as an Employee:

#### 1. **Login** (`http://127.0.0.1:8000/accounts/login/`)
- Use your employee credentials
- Access employee dashboard

#### 2. **Employee Dashboard** (`http://127.0.0.1:8000/accounts/employee-dashboard/`)

**Dashboard Overview:**
- **Personal Statistics**
  - Active Appointments
  - Completed Today
  - Pending Tasks
  - Overdue Tasks

- **My Assigned Work**
  - View all work assigned to you
  - See customer details
  - View vehicle information
  - Access work management tools

- **Task Assignments**
  - Tasks assigned by your supervisor
  - Accept/Reject tasks
  - Update progress
  - Mark as complete

- **Recently Completed Work**
  - Your work history
  - Performance records

#### 3. **Accept Task Assignment**
- Navigate to "Task Assignments" section
- Review task details
- Click "Accept" button
- Task status changes to "Accepted"

#### 4. **Start Work**
- Find accepted task
- Click "Start Work" button
- Work status changes to "In Progress"
- Work start time is recorded

#### 5. **Update Progress**
- Access task details
- Update progress percentage
- Add work notes
- Save changes

#### 6. **Complete Work**
- Click "Complete" button
- Add final work notes
- Submit completion
- Work completion time is recorded

---

## Super Employee (Manager) Features

### 📸 Screenshot Locations:
- [ ] Super employee dashboard
- [ ] Team overview
- [ ] Employee management
- [ ] Task assignment form
- [ ] Performance metrics

### How to Use as a Super Employee:

#### 1. **Access Management Dashboard** (`http://127.0.0.1:8000/accounts/employee-dashboard/`)

**Super Employee Dashboard Sections:**

a. **Team Statistics**
   - Total Employees
   - Available Employees
   - Busy Employees
   - Total Active Work
   - Work Completed Today
   - Overdue Assignments

b. **Employee Management**
   - View all employees
   - See employee status (Available, Busy, On Break, Off Duty)
   - Monitor active tasks
   - Track performance ratings

c. **Unassigned Work**
   - View work waiting to be assigned
   - Assign to specific employees
   - Set priority levels

d. **Task Assignments**
   - All tasks you've assigned
   - Track assignment status
   - Monitor progress

#### 2. **Assign Task to Employee**

**Steps:**
a. Click "Assign Task" button
b. Fill in task details:
   - Employee (select from dropdown)
   - Task Title
   - Description
   - Priority (Low, Normal, High, Urgent)
   - Due Date and Time
   - Link to appointment (optional)
c. Click "Create Assignment"
d. Employee will see the task in their dashboard

#### 3. **Monitor Employee Performance**
- View employee statistics
- Check completion rates
- Track active tasks
- Identify bottlenecks

#### 4. **Update Employee Status**
- Change employee availability
- Update current status
- Add management notes

---

## Admin Panel Features

### 📸 Screenshot Locations:
- [ ] Admin panel dashboard
- [ ] Employee management
- [ ] Service management
- [ ] Appointment overview
- [ ] Analytics and reports

### How to Use the Admin Panel:

#### 1. **Access Admin Panel** (`http://127.0.0.1:8000/admin-panel/`)

**Requirements:**
- Must be logged in as admin/superuser

#### 2. **Dashboard Overview** (`http://127.0.0.1:8000/admin-panel/dashboard/`)

**Key Metrics:**
- Total Appointments
- Total Revenue
- Active Employees
- Customer Count
- Today's Appointments
- Pending Tasks

**Visual Analytics:**
- Appointment trend charts
- Revenue graphs
- Service distribution
- Employee performance

#### 3. **Employee Management** (`http://127.0.0.1:8000/admin-panel/employees/`)

**Features:**
- View all employees
- Add new employees
- Edit employee details
- Activate/Deactivate employees
- View employee performance
- Assign roles (Regular/Super Employee)

**How to Add Employee:**
a. Click "Add Employee"
b. Fill in details:
   - User Information (Username, Email, Name)
   - Employee ID
   - Employee Type (Regular/Super)
   - Specialization
   - Hire Date
   - Contact Information
c. Save

**How to View Employee Details:**
a. Click "View Detail" on any employee
b. See:
   - Employee information
   - Appointment history
   - Performance metrics
   - Recent activity

#### 4. **Service Management** (`http://127.0.0.1:8000/admin-panel/services/`)

**Features:**
- View all services
- Add new services
- Edit service details
- Activate/Deactivate services
- Set pricing
- Manage categories

**How to Add Service:**
a. Click "Add Service"
b. Fill in details:
   - Service Name
   - Category
   - Description
   - Base Price
   - Duration (hours)
   - Upload image (optional)
c. Save

#### 5. **Appointment Management** (`http://127.0.0.1:8000/admin-panel/appointments/`)

**Features:**
- View all appointments
- Filter by status, date, employee
- Search appointments
- View appointment details
- Manually create appointments
- Cancel appointments

#### 6. **Analytics and Reports**

**Available Reports:**
- Daily appointment summary
- Revenue reports
- Employee performance
- Service popularity
- Customer statistics

---

## Common Tasks

### For Customers:

#### ✅ How to Book an Appointment
1. Login → Browse Services → Select Service → Click "Book Now"
2. Choose Date → Select Time Slot
3. Enter Vehicle Details
4. Add Requirements (optional)
5. Review → Confirm Booking

#### ✅ How to Cancel an Appointment
1. Login → My Appointments
2. Find appointment → Click "View Details"
3. Click "Cancel Appointment"
4. Confirm cancellation

#### ✅ How to View Appointment History
1. Login → Navigate to "My Appointments"
2. Use filters to sort by status
3. Click on any appointment for details

### For Employees:

#### ✅ How to Accept and Complete a Task
1. Login → Employee Dashboard
2. Find task in "Task Assignments"
3. Click "Accept"
4. Click "Start Work" when ready
5. Update progress as you work
6. Click "Complete" when finished
7. Add final notes → Submit

#### ✅ How to View Your Schedule
1. Login → Employee Dashboard
2. Check "My Assigned Work" section
3. View today's work in top section

### For Super Employees:

#### ✅ How to Assign Work to Employee
1. Login → Super Employee Dashboard
2. Find unassigned work OR click "Assign Task"
3. Select employee
4. Fill in task details
5. Set priority and due date
6. Submit assignment

#### ✅ How to Monitor Team Performance
1. Login → Dashboard
2. Review "Employee Management" section
3. Check individual employee stats
4. View team overview metrics

### For Admins:

#### ✅ How to Add New Service
1. Login → Admin Panel → Services
2. Click "Add Service"
3. Enter service details
4. Set pricing and duration
5. Save

#### ✅ How to Manage Employees
1. Login → Admin Panel → Employees
2. View employee list
3. Click "View Detail" or "Edit"
4. Make changes
5. Save

---

## Troubleshooting

### Common Issues:

#### Issue: Cannot login
**Solution:**
- Check username and password
- Ensure account is active
- Clear browser cache
- Contact administrator

#### Issue: No time slots available
**Solution:**
- Try a different date
- Check if date is in the past
- Contact store if persistent

#### Issue: Cannot cancel appointment
**Solution:**
- Check appointment status (must be "Booked")
- Ensure appointment date is in future
- Contact administrator for help

#### Issue: Task assignment not showing
**Solution:**
- Refresh the page
- Check if you're logged in as employee
- Verify task was assigned to you

#### Issue: Admin panel access denied
**Solution:**
- Ensure you're logged in with admin account
- Check user role
- Contact system administrator

---

## Screenshots Guide

### Recommended Screenshots to Take:

#### 1. **Home & Authentication** (5 screenshots)
- [ ] Home page/Landing page
- [ ] Registration form
- [ ] Login page
- [ ] Password reset page
- [ ] Successful registration confirmation

#### 2. **Customer Flow** (10 screenshots)
- [ ] Customer dashboard
- [ ] Service catalog/list
- [ ] Service detail page
- [ ] Booking form - Date selection
- [ ] Booking form - Time slot selection
- [ ] Booking form - Vehicle details
- [ ] Booking confirmation
- [ ] My appointments page
- [ ] Appointment detail view
- [ ] Appointment cancellation

#### 3. **Employee Flow** (8 screenshots)
- [ ] Regular employee dashboard
- [ ] My assigned work section
- [ ] Task assignments section
- [ ] Task detail view
- [ ] Accept task screen
- [ ] Start work screen
- [ ] Update progress form
- [ ] Complete work confirmation

#### 4. **Super Employee Flow** (8 screenshots)
- [ ] Super employee dashboard
- [ ] Team overview section
- [ ] Employee management table
- [ ] Unassigned work section
- [ ] Task assignment form
- [ ] Employee performance metrics
- [ ] Task assignment detail
- [ ] My assignments tracking

#### 5. **Admin Panel** (12 screenshots)
- [ ] Admin panel dashboard
- [ ] Dashboard analytics/charts
- [ ] Employee list page
- [ ] Add employee form
- [ ] Employee detail view
- [ ] Service list page
- [ ] Add service form
- [ ] Edit service form
- [ ] Appointment list page
- [ ] Appointment filters/search
- [ ] System settings
- [ ] Reports page

### How to Take Screenshots:

**macOS:**
- Press `Cmd + Shift + 4` → Click and drag to select area
- Press `Cmd + Shift + 3` → Capture entire screen

**Windows:**
- Press `Windows + Shift + S` → Select area
- Use Snipping Tool

**For Better Documentation:**
1. Use consistent browser window size
2. Hide personal information
3. Use clean test data
4. Annotate screenshots with arrows/highlights
5. Number screenshots in order

---

## Converting to Word Document

### Method 1: Using Pandoc
```bash
pandoc USER_GUIDE.md -o CarModX_User_Guide.docx
```

### Method 2: Manual Copy-Paste
1. Open this file in any Markdown viewer
2. Copy content
3. Paste into Microsoft Word
4. Add your screenshots
5. Format as needed

### Method 3: Online Converter
- Use websites like:
  - cloudconvert.com
  - markdowntoword.com
  - dillinger.io

---

## Additional Resources

### Project Links:
- **GitHub Repository**: https://github.com/Vishavjeet28/car-modifying-scheduling
- **Live Demo**: (Add if deployed)

### Technology Stack:
- **Backend**: Django 4.2.7, Python 3.13
- **Frontend**: Bootstrap 5, JavaScript
- **Database**: SQLite (Development) / PostgreSQL (Production)
- **Additional**: Crispy Forms, Font Awesome

### Support:
For issues or questions:
- Open an issue on GitHub
- Contact: (Add your contact info)

---

## Version History

**v1.0.0** (October 2025)
- Initial release
- Customer booking system
- Employee task management
- Super employee management dashboard
- Admin panel with analytics

---

## License

(Add your license information here)

---

**Last Updated**: October 27, 2025
**Author**: Vishavjeet Singh
**Project**: CarModX - Car Modification Scheduling System
