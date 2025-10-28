# Contact Message System Documentation

## 📧 **Contact Form Functionality**

### Overview
The contact form system allows visitors to send messages to the website administrators. All messages are stored in the database and can be viewed through the Django admin panel.

---

## 🎯 **For Website Visitors**

### How to Send a Message:

1. Go to the contact page: `http://127.0.0.1:8000/contact/`
2. Fill in the contact form:
   - **Name** (required)
   - **Email** (required)
   - **Phone** (optional)
   - **Subject** (required)
   - **Message** (required)
3. Click **"Send Message"**
4. You'll see a success message confirming your submission

---

## 👑 **For Administrators**

### How to View Contact Messages:

#### **Option 1: Django Admin Panel**
1. Go to: `http://127.0.0.1:8000/admin/`
2. Login with your superuser credentials
3. Click on **"Contact Messages"** under the "Main" app section
4. You'll see a list of all contact submissions

#### **Option 2: Super Admin Panel** (if added)
1. Go to: `http://127.0.0.1:8000/admin-panel/`
2. Navigate to contact messages section

---

## 📋 **Message List View Features**

### **List Display Columns:**
- Name
- Email
- Subject
- Created At (submission date/time)
- Is Read (status indicator)

### **Filters:**
- By read/unread status
- By submission date

### **Search:**
- Search by name, email, subject, or message content

### **Actions:**
- Mark selected messages as read
- Mark selected messages as unread

---

## 📖 **Message Detail View**

When you click on a message, you'll see:

### **Contact Information:**
- Name
- Email
- Phone (if provided)

### **Message Details:**
- Subject
- Full message text
- Submission timestamp

### **Status & Notes:**
- Read/Unread checkbox
- Admin notes field (internal use only - not visible to the sender)

---

## 🔧 **Database Structure**

### **ContactMessage Model Fields:**

```python
- name: CharField(max_length=100)
- email: EmailField()
- phone: CharField(max_length=20, blank=True)
- subject: CharField(max_length=200)
- message: TextField()
- created_at: DateTimeField(auto_now_add=True)
- is_read: BooleanField(default=False)
- admin_notes: TextField(blank=True)
```

---

## 📊 **Viewing Messages via Django Shell**

You can also query messages programmatically:

```python
python manage.py shell
```

```python
from main.models import ContactMessage

# Get all messages
all_messages = ContactMessage.objects.all()

# Get unread messages
unread = ContactMessage.objects.filter(is_read=False)

# Get messages from today
from django.utils import timezone
from datetime import timedelta
today = timezone.now().date()
today_messages = ContactMessage.objects.filter(
    created_at__date=today
)

# Get a specific message
message = ContactMessage.objects.get(id=1)
print(f"From: {message.name}")
print(f"Subject: {message.subject}")
print(f"Message: {message.message}")

# Mark message as read
message.mark_as_read()
```

---

## 🔐 **Access Control**

### **Public Access:**
- Anyone can submit a contact form (no login required)

### **Admin Access:**
- Only superusers can view contact messages in the admin panel
- Messages are read-only (name, email, subject, message fields)
- Admins can only edit: read status and admin notes

---

## ✅ **Features**

### **Form Validation:**
- Required fields are validated
- Email format is validated
- Phone number validation (digits, spaces, +, - only)

### **Success Messages:**
- Users see a confirmation message after submission
- Page redirects to prevent duplicate submissions

### **Admin Features:**
- Bulk actions (mark as read/unread)
- Filtering and searching
- Organized fieldsets in detail view
- Internal notes for tracking responses

---

## 📝 **Example Admin Workflow**

1. **New message arrives** → Shows as unread (red indicator)
2. **Admin reviews message** → Opens message detail
3. **Admin responds** (via email/phone) → Adds notes in "admin_notes" field
4. **Admin marks as read** → Message status updated
5. **Admin notes saved** → Internal record of response kept

---

## 🚀 **Quick Access URLs**

| Page | URL | Access |
|------|-----|--------|
| Contact Form | `http://127.0.0.1:8000/contact/` | Public |
| Admin Panel | `http://127.0.0.1:8000/admin/` | Superuser only |
| Contact Messages Admin | `http://127.0.0.1:8000/admin/main/contactmessage/` | Superuser only |

---

## 🎉 **System Status: FULLY OPERATIONAL**

The contact message system is now fully functional and ready to receive customer inquiries!

**Created:** October 28, 2025  
**App:** main  
**Model:** ContactMessage  
**Admin:** Registered and configured
