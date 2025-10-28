# Contact Message System - Complete Documentation

## Overview
The Contact Message System provides a complete solution for handling customer inquiries through the website's contact form. Messages are stored in the database and accessible only to **Super Admin** and **Super Employee** users through the custom admin panel (NOT through Django's admin interface).

---

## Key Features

### ✅ Public Contact Form
- **Location**: `/contact/` (Contact Us page)
- **Fields**: Name, Email, Phone (optional), Subject, Message
- **Validation**: Email format, phone number format (if provided)
- **User Feedback**: Success message after submission
- **Security**: CSRF protection, form validation

### ✅ Custom Admin Panel Interface
- **Access Control**: Only Super Admin and Super Employee users
- **Location**: Admin Panel → Communication → Contact Messages
- **Not in Django Admin**: Hidden from standard `/admin/` interface

### ✅ Message Management Features
1. **List View**: Browse all messages with search and filtering
2. **Detail View**: View full message with auto-mark-as-read
3. **Status Management**: Mark messages as read/unread
4. **Admin Notes**: Add internal notes (not visible to customers)
5. **Quick Actions**: Reply via email, call, delete
6. **Badge Notification**: Unread count in sidebar

---

## File Structure

```
car-modification-scheduling/
├── main/                              # Contact message app
│   ├── models.py                      # ContactMessage model
│   ├── forms.py                       # ContactForm with validation
│   ├── admin.py                       # Django admin (commented out)
│   └── migrations/
│       └── 0001_initial.py            # Database schema
│
├── admin_panel/                       # Custom admin interface
│   ├── contact_views.py               # Contact message views
│   ├── urls.py                        # URL patterns (includes contact routes)
│   ├── templatetags/
│   │   └── contact_extras.py          # Unread count template tag
│   └── templates/admin_panel/
│       ├── base.html                  # Updated sidebar with Contact Messages link
│       └── contact/
│           ├── message_list.html      # List view with search/filter
│           ├── message_detail.html    # Detail view with full message
│           └── message_update.html    # Edit form for status/notes
│
├── carmodx/
│   └── views.py                       # Updated contact_view (handles submissions)
│
└── templates/
    └── contact.html                   # Public contact form
```

---

## Database Schema

### ContactMessage Model
**Location**: `main/models.py`

| Field | Type | Description |
|-------|------|-------------|
| `name` | CharField(100) | Sender's full name |
| `email` | EmailField | Sender's email address |
| `phone` | CharField(15) | Sender's phone (optional) |
| `subject` | CharField(200) | Message subject line |
| `message` | TextField | Full message content |
| `created_at` | DateTimeField | When message was submitted (auto) |
| `is_read` | BooleanField | Read/Unread status (default: False) |
| `admin_notes` | TextField | Internal notes (optional, blank) |

**Methods**:
- `mark_as_read()`: Sets is_read to True
- `__str__()`: Returns "Message from {name} - {subject}"

---

## Access Control

### Who Can Access Contact Messages?

✅ **ALLOWED**:
- Users with `is_superuser=True` (Super Admin)
- Users with `is_staff=True` AND `is_superuser=True` (Super Employee)

❌ **NOT ALLOWED**:
- Regular Django admin users (staff but not superuser)
- Regular employees
- Customers/visitors

### Implementation:
All views use the `@super_user_required` decorator from `admin_panel/decorators.py`:

```python
from admin_panel.decorators import super_user_required

@super_user_required
def contact_message_list(request):
    # Only accessible to super users
    ...
```

---

## URL Routes

### Public URLs (Anyone)
```
/contact/                              # Contact form page
```

### Admin Panel URLs (Super Users Only)
```
/admin-panel/contact-messages/                      # List all messages
/admin-panel/contact-messages/<id>/                 # View message detail
/admin-panel/contact-messages/<id>/edit/            # Edit status & notes
/admin-panel/contact-messages/<id>/mark-read/       # Quick action: mark as read
/admin-panel/contact-messages/<id>/mark-unread/     # Quick action: mark as unread
/admin-panel/contact-messages/<id>/delete/          # Delete message
```

**Base URL**: All admin panel URLs are prefixed with `/admin-panel/`

---

## Views Overview

### 1. ContactMessageListView (admin_panel/contact_views.py)
**Class-Based View**: ListView  
**Access**: Super users only  
**Features**:
- Displays all messages in a table
- Search functionality (name, email, subject, message)
- Filter by status (all/read/unread)
- Pagination (20 messages per page)
- Shows unread count badge
- Quick actions (view, mark read/unread, delete)

**Template**: `admin_panel/contact/message_list.html`

**Context Variables**:
```python
{
    'messages': QuerySet,          # Filtered/searched messages
    'search_query': str,           # Current search term
    'status_filter': str,          # Current filter (read/unread/all)
    'unread_count': int,           # Total unread messages
    'read_count': int,             # Total read messages
    'total_messages': int,         # Total all messages
}
```

### 2. ContactMessageDetailView (admin_panel/contact_views.py)
**Class-Based View**: DetailView  
**Access**: Super users only  
**Features**:
- Shows full message details
- Auto-marks as read when viewed (via get() override)
- Displays sender information with contact links
- Shows admin notes if any
- Quick action buttons (edit, delete, mark read/unread)
- Reply via email button (opens mailto:)
- Call button (if phone provided)

**Template**: `admin_panel/contact/message_detail.html`

**Context Variables**:
```python
{
    'message': ContactMessage,     # The message object (aliased as 'object')
}
```

### 3. ContactMessageUpdateView (admin_panel/contact_views.py)
**Class-Based View**: UpdateView  
**Access**: Super users only  
**Features**:
- Edit `is_read` status (dropdown: Read/Unread)
- Edit `admin_notes` (textarea)
- Shows original message as read-only
- Success message on save
- Redirects to detail view after save

**Template**: `admin_panel/contact/message_update.html`

**Form Fields**:
- `is_read`: BooleanField (dropdown)
- `admin_notes`: TextField (optional)

**Context Variables**:
```python
{
    'object': ContactMessage,      # The message being edited
    'form': ModelForm,             # Form instance
}
```

### 4. Helper Functions (admin_panel/contact_views.py)

#### mark_as_read(request, pk)
**Function-Based View**  
**Access**: Super users only  
**Purpose**: Quick action to mark message as read  
**Redirect**: Back to message detail page

#### mark_as_unread(request, pk)
**Function-Based View**  
**Access**: Super users only  
**Purpose**: Quick action to mark message as unread  
**Redirect**: Back to message detail page

#### delete_message(request, pk)
**Function-Based View**  
**Access**: Super users only  
**Purpose**: Delete message permanently  
**Redirect**: Back to message list page  
**Confirmation**: JavaScript confirmation required

---

## Template Features

### Sidebar Navigation (admin_panel/base.html)
```django
{% load contact_extras %}
{% get_unread_contact_count as unread_count %}

<!-- Shows unread badge in sidebar -->
<i class="bi bi-envelope me-3"></i>Contact Messages
{% if unread_count > 0 %}
    <span class="badge bg-danger rounded-pill ms-2">{{ unread_count }}</span>
{% endif %}
```

### Message List Template Highlights
- **Status badges**: Red (Unread) / Green (Read)
- **Table highlighting**: Yellow background for unread rows
- **Search form**: Text input + status dropdown
- **Pagination**: First/Previous/Next/Last links
- **Empty state**: Shows inbox icon when no messages

### Message Detail Template Highlights
- **Avatar circle**: First letter of sender's name
- **Contact links**: Clickable email (mailto:) and phone (tel:)
- **Message formatting**: Uses `linebreaks` filter for paragraphs
- **Action sidebar**: Status card, admin notes card, actions card
- **Quick reply**: "Reply via Email" button with pre-filled subject

### Message Update Template Highlights
- **Read-only info**: Original message shown in alert box
- **Status dropdown**: Read/Unread selector
- **Notes textarea**: Large text area for internal notes
- **Helper tips**: Best practices card at bottom
- **Form validation**: Bootstrap validation styles

---

## Form Handling

### Public Contact Form (main/forms.py)
```python
class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'name': TextInput(attrs={'class': 'form-control'}),
            'email': EmailInput(attrs={'class': 'form-control'}),
            'phone': TextInput(attrs={'class': 'form-control'}),
            'subject': TextInput(attrs={'class': 'form-control'}),
            'message': Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }
    
    def clean_phone(self):
        """Validate phone number format"""
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remove non-numeric characters
            phone_digits = re.sub(r'\D', '', phone)
            if len(phone_digits) < 10:
                raise ValidationError("Please enter a valid phone number")
        return phone
```

**Validation Rules**:
- Name: Required, max 100 characters
- Email: Required, valid email format
- Phone: Optional, min 10 digits (can include formatting)
- Subject: Required, max 200 characters
- Message: Required, no length limit

### Public Form Submission (carmodx/views.py)
```python
def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()  # Saves to database
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('contact')  # Prevents resubmission
    else:
        form = ContactForm()
    
    return render(request, 'contact.html', {'form': form})
```

---

## Workflow Example

### Customer Submits Contact Form

1. **User visits** `/contact/`
2. **Fills form**: Name, email, phone, subject, message
3. **Clicks submit**: Form validated
4. **Success**: Message saved to database with `is_read=False`
5. **Feedback**: "Your message has been sent successfully!" shown
6. **Redirect**: Back to contact page (prevents resubmission)

### Admin Reviews Message

1. **Admin logs in** as super user
2. **Sees badge** in sidebar: "Contact Messages (3)" with red badge
3. **Clicks link**: Goes to `/admin-panel/contact-messages/`
4. **Sees table**: Unread messages highlighted in yellow
5. **Searches**: Types "refund" in search box
6. **Filters**: Selects "Unread Only" from dropdown
7. **Clicks message**: Goes to detail view
8. **Auto-marked**: Message automatically marked as read
9. **Views details**: Full message, sender info, timestamp
10. **Adds notes**: Clicks "Edit" → adds "Spoke with customer on phone"
11. **Saves**: Returns to detail view with success message

### Admin Takes Action

**Option 1: Reply via Email**
- Click "Reply via Email" button
- Opens default email client with:
  - To: customer@email.com
  - Subject: Re: Original Subject
- Admin sends reply outside the system

**Option 2: Call Customer**
- Click phone number or "Call" button
- Opens phone app (mobile) or dialer (desktop)
- Admin speaks with customer directly

**Option 3: Mark for Follow-Up**
- Click "Mark as Unread"
- Message goes back to unread list
- Badge count increases

**Option 4: Archive/Delete**
- Click "Delete Message"
- JavaScript confirmation appears
- Message permanently removed from database

---

## Security Features

### 1. Access Control
- `@super_user_required` decorator on all admin views
- Checks `request.user.is_superuser`
- Returns 403 Forbidden if not authorized
- Sidebar menu only shows to super users

### 2. CSRF Protection
- All forms include `{% csrf_token %}`
- Django validates CSRF token on POST
- Prevents cross-site request forgery attacks

### 3. Input Validation
- Email format validation (Django EmailField)
- Phone number validation (custom clean_phone method)
- XSS prevention (Django auto-escapes template variables)
- SQL injection prevention (Django ORM parameterized queries)

### 4. Data Privacy
- Admin notes NOT visible to customers
- Messages only accessible to authorized users
- No public API endpoints for messages
- Read-only fields for customer data in admin

---

## Testing the System

### Test 1: Submit Contact Form
```bash
1. Go to http://localhost:8000/contact/
2. Fill in all fields:
   - Name: John Doe
   - Email: john@example.com
   - Phone: (555) 123-4567
   - Subject: Question about service
   - Message: I would like to know more about...
3. Click "Send Message"
4. Verify success message appears
5. Verify page redirects (no data in form)
```

### Test 2: View in Admin Panel
```bash
1. Login as super user
2. Go to http://localhost:8000/admin-panel/
3. Check sidebar: "Contact Messages" link with badge
4. Click "Contact Messages"
5. Verify message appears in table with "Unread" badge
6. Verify message row has yellow background
7. Click message name or "View" button
8. Verify detail page loads
9. Check that badge now shows "Read"
10. Go back to list - yellow highlight should be gone
```

### Test 3: Search and Filter
```bash
1. In message list, enter "John" in search box
2. Click "Search"
3. Verify only John's message appears
4. Select "Unread Only" from filter dropdown
5. Click "Search"
6. Verify only unread messages appear
7. Clear search and select "Read Only"
8. Verify only read messages appear
```

### Test 4: Edit Message
```bash
1. Open message detail page
2. Click "Edit" button
3. Change status to "Unread"
4. Add admin notes: "Follow up next week"
5. Click "Save Changes"
6. Verify success message
7. Verify status changed to "Unread"
8. Verify notes appear in sidebar
9. Go back to list - message should be yellow again
```

### Test 5: Quick Actions
```bash
1. In message list, click "Mark as Read" (green check icon)
2. Verify page refreshes and badge changes
3. Click "Mark as Unread" (yellow X icon)
4. Verify badge changes back
5. Click "Delete" (red trash icon)
6. Verify JavaScript confirmation appears
7. Click "Cancel" - message stays
8. Click "Delete" again and confirm
9. Verify message removed from list
10. Verify success message appears
```

### Test 6: Access Control
```bash
1. Logout from super user account
2. Login as regular staff user (is_staff=True, is_superuser=False)
3. Go to http://localhost:8000/admin-panel/
4. Verify "Contact Messages" does NOT appear in sidebar
5. Try to access directly: http://localhost:8000/admin-panel/contact-messages/
6. Verify 403 Forbidden error or redirect to login
```

---

## Common Issues & Solutions

### Issue 1: Contact Messages link not showing in sidebar
**Symptom**: Sidebar doesn't show "Contact Messages" link  
**Cause**: User is not a super user  
**Solution**: 
```python
# In Django shell or admin
user = User.objects.get(username='your_username')
user.is_superuser = True
user.save()
```

### Issue 2: Template tag not working (no unread count)
**Symptom**: Badge doesn't show unread count  
**Cause**: Template tag not loaded or main app not in INSTALLED_APPS  
**Solution**:
1. Check `carmodx/settings.py` includes `'main'` in INSTALLED_APPS
2. Restart Django server
3. Check template includes `{% load contact_extras %}`

### Issue 3: Forms not submitting
**Symptom**: Contact form shows errors but fields are valid  
**Cause**: CSRF token missing or invalid  
**Solution**:
1. Check template includes `{% csrf_token %}`
2. Clear browser cookies
3. Check middleware includes `CsrfViewMiddleware`

### Issue 4: Pagination not working
**Symptom**: Shows all messages instead of 20 per page  
**Cause**: ListView paginate_by not set  
**Solution**: Check `ContactMessageListView.paginate_by = 20`

### Issue 5: Auto-mark as read not working
**Symptom**: Messages stay unread when viewed  
**Cause**: get() method not calling mark_as_read()  
**Solution**: Check `ContactMessageDetailView.get()` override:
```python
def get(self, request, *args, **kwargs):
    response = super().get(request, *args, **kwargs)
    if not self.object.is_read:
        self.object.mark_as_read()
    return response
```

---

## Future Enhancements (Optional)

### 1. Email Notifications
- Send email to admin when new message received
- Requires email configuration in settings.py
- Can use Django's send_mail() function

### 2. Reply Within System
- Add reply form in admin panel
- Store replies in database (separate model)
- Show conversation thread

### 3. Export Functionality
- Export messages to CSV/Excel
- Filter by date range
- Download button in list view

### 4. Categories/Tags
- Add category field (Sales, Support, Complaint)
- Filter by category
- Auto-assignment to staff

### 5. Priority Levels
- Add priority field (Low, Medium, High, Urgent)
- Sort by priority
- Color-coded badges

### 6. Statistics Dashboard
- Chart showing messages over time
- Average response time
- Most common subjects (word cloud)

---

## Maintenance

### Database Cleanup
To delete old read messages:

```python
from main.models import ContactMessage
from datetime import datetime, timedelta

# Delete read messages older than 90 days
cutoff_date = datetime.now() - timedelta(days=90)
ContactMessage.objects.filter(
    is_read=True,
    created_at__lt=cutoff_date
).delete()
```

### Backup Messages
To export all messages:

```python
import csv
from main.models import ContactMessage

with open('contact_messages_backup.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(['Name', 'Email', 'Phone', 'Subject', 'Message', 'Date', 'Read', 'Notes'])
    
    for msg in ContactMessage.objects.all():
        writer.writerow([
            msg.name,
            msg.email,
            msg.phone or '',
            msg.subject,
            msg.message,
            msg.created_at.strftime('%Y-%m-%d %H:%M'),
            msg.is_read,
            msg.admin_notes or ''
        ])
```

---

## Support

For issues or questions about the Contact Message System:
1. Check this documentation first
2. Review the code comments in:
   - `main/models.py`
   - `admin_panel/contact_views.py`
   - Template files in `admin_panel/templates/admin_panel/contact/`
3. Check Django logs for error messages
4. Test with Django shell: `python manage.py shell`

---

## Changelog

**v1.0.0** (Current)
- Initial implementation
- Public contact form
- Custom admin panel interface
- Search and filter functionality
- Auto-mark as read on view
- Admin notes feature
- Quick actions (mark read/unread, delete)
- Unread count badge in sidebar
- Hidden from Django admin

---

**Last Updated**: January 2025  
**Django Version**: 4.2.7  
**Bootstrap Version**: 5.3.0
