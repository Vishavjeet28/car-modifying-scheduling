from django import forms
from django.core.exceptions import ValidationError
from services.models import Service, ServiceCategory, ServicePrice
from accounts.models import Employee
from .models import SystemSettings
from PIL import Image
import os
import json


class ServiceForm(forms.ModelForm):
    """Form for creating and updating services"""
    
    class Meta:
        model = Service
        fields = ['name', 'description', 'category', 'base_price', 'estimated_duration', 'is_active', 'image']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter service name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter service description'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'base_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'estimated_duration': forms.TimeInput(attrs={
                'class': 'form-control',
                'placeholder': 'HH:MM:SS'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active categories
        self.fields['category'].queryset = ServiceCategory.objects.filter(is_active=True)
        
        # Make fields required
        self.fields['name'].required = True
        self.fields['description'].required = True
        self.fields['category'].required = True
        self.fields['base_price'].required = True
        self.fields['estimated_duration'].required = True
    
    def clean_name(self):
        """Validate service name is unique"""
        name = self.cleaned_data.get('name')
        if name:
            # Check for existing service with same name (excluding current instance)
            existing = Service.objects.filter(name__iexact=name)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise ValidationError('A service with this name already exists.')
        return name
    
    def clean_base_price(self):
        """Validate base price is positive"""
        price = self.cleaned_data.get('base_price')
        if price is not None and price <= 0:
            raise ValidationError('Base price must be greater than 0.')
        return price
    
    def clean_image(self):
        """Validate uploaded image"""
        image = self.cleaned_data.get('image')
        if image:
            # Check file size (max 5MB)
            if image.size > 5 * 1024 * 1024:
                raise ValidationError('Image file size must be less than 5MB.')
            
            # Check file type
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
            ext = os.path.splitext(image.name)[1].lower()
            if ext not in valid_extensions:
                raise ValidationError('Please upload a valid image file (JPG, PNG, GIF, or WebP).')
            
            # Validate image dimensions using PIL
            try:
                img = Image.open(image)
                width, height = img.size
                
                # Check minimum dimensions
                if width < 100 or height < 100:
                    raise ValidationError('Image must be at least 100x100 pixels.')
                
                # Check maximum dimensions
                if width > 2000 or height > 2000:
                    raise ValidationError('Image must be no larger than 2000x2000 pixels.')
                    
            except Exception:
                raise ValidationError('Invalid image file.')
        
        return image


class ServiceSearchForm(forms.Form):
    """Form for searching and filtering services"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search services...',
            'id': 'service-search'
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=ServiceCategory.objects.filter(is_active=True),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'category-filter'
        })
    )
    
    status = forms.ChoiceField(
        choices=[
            ('', 'All Status'),
            ('active', 'Active'),
            ('inactive', 'Inactive')
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'status-filter'
        })
    )
    
    price_min = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min Price',
            'step': '0.01'
        })
    )
    
    price_max = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max Price',
            'step': '0.01'
        })
    )


class ServiceBulkActionForm(forms.Form):
    """Form for bulk operations on services"""
    
    ACTION_CHOICES = [
        ('activate', 'Activate Selected'),
        ('deactivate', 'Deactivate Selected'),
        ('delete', 'Delete Selected'),
        ('change_category', 'Change Category'),
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'bulk-action-select'
        })
    )
    
    selected_services = forms.CharField(
        widget=forms.HiddenInput(),
        required=True
    )
    
    # Optional field for category change
    new_category = forms.ModelChoiceField(
        queryset=ServiceCategory.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'new-category-select',
            'style': 'display: none;'
        })
    )
    
    def clean_selected_services(self):
        """Validate selected services"""
        selected = self.cleaned_data.get('selected_services')
        if selected:
            try:
                service_ids = [int(id.strip()) for id in selected.split(',') if id.strip()]
                if not service_ids:
                    raise ValidationError('No services selected.')
                return service_ids
            except ValueError:
                raise ValidationError('Invalid service selection.')
        raise ValidationError('No services selected.')
    
    def clean(self):
        """Validate form data based on action"""
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        new_category = cleaned_data.get('new_category')
        
        if action == 'change_category' and not new_category:
            raise ValidationError('Please select a category for the change category action.')
        
        return cleaned_data


class CategoryForm(forms.ModelForm):
    """Form for creating and updating service categories"""
    
    class Meta:
        model = ServiceCategory
        fields = ['name', 'description', 'icon', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter category name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter category description'
            }),
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., fas fa-car, fas fa-wrench'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields required
        self.fields['name'].required = True
        self.fields['description'].required = False
        self.fields['icon'].required = False
    
    def clean_name(self):
        """Validate category name is unique"""
        name = self.cleaned_data.get('name')
        if name:
            # Check for existing category with same name (excluding current instance)
            existing = ServiceCategory.objects.filter(name__iexact=name)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise ValidationError('A category with this name already exists.')
        return name
    
    def clean_icon(self):
        """Validate icon class format"""
        icon = self.cleaned_data.get('icon')
        if icon:
            # Basic validation for Font Awesome icon format
            if not (icon.startswith('fas ') or icon.startswith('far ') or 
                   icon.startswith('fab ') or icon.startswith('fal ')):
                raise ValidationError('Icon should be a valid Font Awesome class (e.g., "fas fa-car").')
        return icon


class CategorySearchForm(forms.Form):
    """Form for searching and filtering categories"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search categories...',
            'id': 'category-search'
        })
    )
    
    status = forms.ChoiceField(
        choices=[
            ('', 'All Status'),
            ('active', 'Active'),
            ('inactive', 'Inactive')
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'status-filter'
        })
    )


class CategoryBulkActionForm(forms.Form):
    """Form for bulk operations on categories"""
    
    ACTION_CHOICES = [
        ('activate', 'Activate Selected'),
        ('deactivate', 'Deactivate Selected'),
        ('delete', 'Delete Selected'),
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'bulk-action-select'
        })
    )
    
    selected_categories = forms.CharField(
        widget=forms.HiddenInput(),
        required=True
    )
    
    def clean_selected_categories(self):
        """Validate selected categories"""
        selected = self.cleaned_data.get('selected_categories')
        if selected:
            try:
                category_ids = [int(id.strip()) for id in selected.split(',') if id.strip()]
                if not category_ids:
                    raise ValidationError('No categories selected.')
                return category_ids
            except ValueError:
                raise ValidationError('Invalid category selection.')
        raise ValidationError('No categories selected.')


class ServicePriceForm(forms.ModelForm):
    """Form for creating and updating service prices"""
    
    class Meta:
        model = ServicePrice
        fields = ['service', 'vehicle_type', 'complexity_level', 'price', 'is_active']
        widgets = {
            'service': forms.Select(attrs={
                'class': 'form-select'
            }),
            'vehicle_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Sedan, SUV, Sports Car',
                'list': 'vehicle-types'
            }),
            'complexity_level': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Basic, Standard, Premium',
                'list': 'complexity-levels'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '0.00'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active services
        self.fields['service'].queryset = Service.objects.filter(is_active=True).select_related('category')
        
        # Make fields required
        self.fields['service'].required = True
        self.fields['vehicle_type'].required = True
        self.fields['complexity_level'].required = True
        self.fields['price'].required = True
    
    def clean_price(self):
        """Validate price is positive"""
        price = self.cleaned_data.get('price')
        if price is not None and price <= 0:
            raise ValidationError('Price must be greater than 0.')
        return price
    
    def clean_vehicle_type(self):
        """Clean and validate vehicle type"""
        vehicle_type = self.cleaned_data.get('vehicle_type')
        if vehicle_type:
            vehicle_type = vehicle_type.strip().title()
            if len(vehicle_type) < 2:
                raise ValidationError('Vehicle type must be at least 2 characters long.')
        return vehicle_type
    
    def clean_complexity_level(self):
        """Clean and validate complexity level"""
        complexity_level = self.cleaned_data.get('complexity_level')
        if complexity_level:
            complexity_level = complexity_level.strip().title()
            if len(complexity_level) < 2:
                raise ValidationError('Complexity level must be at least 2 characters long.')
        return complexity_level
    
    def clean(self):
        """Validate unique combination of service, vehicle_type, and complexity_level"""
        cleaned_data = super().clean()
        service = cleaned_data.get('service')
        vehicle_type = cleaned_data.get('vehicle_type')
        complexity_level = cleaned_data.get('complexity_level')
        
        if service and vehicle_type and complexity_level:
            # Check for existing price with same combination (excluding current instance)
            existing = ServicePrice.objects.filter(
                service=service,
                vehicle_type=vehicle_type,
                complexity_level=complexity_level
            )
            
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise ValidationError(
                    f'A price already exists for {service.name} - {vehicle_type} - {complexity_level}.'
                )
        
        return cleaned_data


class PricingSearchForm(forms.Form):
    """Form for searching and filtering pricing"""
    
    service = forms.ModelChoiceField(
        queryset=Service.objects.filter(is_active=True).select_related('category'),
        required=False,
        empty_label="All Services",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'service-filter'
        })
    )
    
    vehicle_type = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Vehicle Type',
            'list': 'vehicle-types'
        })
    )
    
    complexity_level = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Complexity Level',
            'list': 'complexity-levels'
        })
    )
    
    status = forms.ChoiceField(
        choices=[
            ('', 'All Status'),
            ('active', 'Active'),
            ('inactive', 'Inactive')
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'status-filter'
        })
    )
    
    price_min = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min Price',
            'step': '0.01'
        })
    )
    
    price_max = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max Price',
            'step': '0.01'
        })
    )


class BulkPricingForm(forms.Form):
    """Form for bulk pricing operations"""
    
    ACTION_CHOICES = [
        ('activate_all', 'Activate All Prices'),
        ('deactivate_all', 'Deactivate All Prices'),
        ('delete_all', 'Delete All Prices'),
        ('apply_percentage', 'Apply Percentage Change'),
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'bulk-pricing-action'
        })
    )
    
    service = forms.ModelChoiceField(
        queryset=Service.objects.filter(is_active=True).select_related('category'),
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'bulk-pricing-service'
        })
    )
    
    percentage = forms.DecimalField(
        required=False,
        min_value=-100,
        max_value=1000,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Percentage (e.g., 10 for +10%, -5 for -5%)',
            'step': '0.1',
            'id': 'percentage-input',
            'style': 'display: none;'
        })
    )
    
    def clean(self):
        """Validate form data based on action"""
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        percentage = cleaned_data.get('percentage')
        
        if action == 'apply_percentage' and percentage is None:
            raise ValidationError('Percentage is required for percentage change action.')
        
        return cleaned_data


class PriceImportForm(forms.Form):
    """Form for importing pricing data from CSV"""
    
    csv_file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv',
            'id': 'csv-file-input'
        }),
        help_text='Upload a CSV file with columns: service_name, vehicle_type, complexity_level, price'
    )
    
    overwrite_existing = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text='Check to overwrite existing prices with same service/vehicle/complexity combination'
    )
    
    def clean_csv_file(self):
        """Validate CSV file"""
        csv_file = self.cleaned_data.get('csv_file')
        if csv_file:
            # Check file size (max 1MB)
            if csv_file.size > 1024 * 1024:
                raise ValidationError('CSV file size must be less than 1MB.')
            
            # Check file extension
            if not csv_file.name.lower().endswith('.csv'):
                raise ValidationError('Please upload a CSV file.')
            
            # Basic content validation
            try:
                content = csv_file.read().decode('utf-8')
                csv_file.seek(0)  # Reset file pointer
                
                lines = content.strip().split('\n')
                if len(lines) < 2:  # Header + at least one data row
                    raise ValidationError('CSV file must contain at least a header row and one data row.')
                
                # Check header
                header = lines[0].lower().strip()
                required_columns = ['service_name', 'vehicle_type', 'complexity_level', 'price']
                for col in required_columns:
                    if col not in header:
                        raise ValidationError(f'CSV file must contain column: {col}')
                        
            except UnicodeDecodeError:
                raise ValidationError('CSV file must be UTF-8 encoded.')
            except Exception as e:
                raise ValidationError(f'Invalid CSV file: {str(e)}')
        
        return csv_file

# Employee Management Forms

class EmployeeCreateForm(forms.ModelForm):
    """Form for creating employees with user account integration"""
    
    # User account fields
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter username'
        }),
        help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter email address'
        })
    )
    
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter first name'
        })
    )
    
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter last name'
        })
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        }),
        help_text='Password must be at least 8 characters long.'
    )
    
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    )
    
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+91XXXXXXXXXX'
        })
    )
    
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Enter address'
        })
    )
    
    class Meta:
        model = Employee
        fields = ['employee_id', 'specialization', 'hire_date', 'is_active']
        widgets = {
            'employee_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter employee ID'
            }),
            'specialization': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Engine Specialist, Body Work Expert'
            }),
            'hire_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields required
        self.fields['username'].required = True
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['password'].required = True
        self.fields['confirm_password'].required = True
        self.fields['employee_id'].required = True
        self.fields['hire_date'].required = True
    
    def clean_username(self):
        """Validate username is unique"""
        username = self.cleaned_data.get('username')
        if username:
            from accounts.models import User
            if User.objects.filter(username=username).exists():
                raise ValidationError('A user with this username already exists.')
        return username
    
    def clean_email(self):
        """Validate email is unique"""
        email = self.cleaned_data.get('email')
        if email:
            from accounts.models import User
            if User.objects.filter(email=email).exists():
                raise ValidationError('A user with this email already exists.')
        return email
    
    def clean_employee_id(self):
        """Validate employee ID is unique"""
        employee_id = self.cleaned_data.get('employee_id')
        if employee_id:
            from accounts.models import Employee
            if Employee.objects.filter(employee_id=employee_id).exists():
                raise ValidationError('An employee with this ID already exists.')
        return employee_id
    
    def clean_password(self):
        """Validate password strength"""
        password = self.cleaned_data.get('password')
        if password:
            if len(password) < 8:
                raise ValidationError('Password must be at least 8 characters long.')
        return password
    
    def clean(self):
        """Validate password confirmation"""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise ValidationError('Passwords do not match.')
        
        return cleaned_data


class EmployeeUpdateForm(forms.ModelForm):
    """Form for updating employees with user account integration"""
    
    # User account fields
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter username'
        })
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter email address'
        })
    )
    
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter first name'
        })
    )
    
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter last name'
        })
    )
    
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Leave blank to keep current password'
        }),
        help_text='Leave blank to keep current password. Must be at least 8 characters if changing.'
    )
    
    confirm_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password'
        })
    )
    
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+91XXXXXXXXXX'
        })
    )
    
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Enter address'
        })
    )
    
    class Meta:
        model = Employee
        fields = ['employee_id', 'specialization', 'hire_date', 'is_active']
        widgets = {
            'employee_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter employee ID'
            }),
            'specialization': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Engine Specialist, Body Work Expert'
            }),
            'hire_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields required
        self.fields['username'].required = True
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['employee_id'].required = True
        self.fields['hire_date'].required = True
    
    def clean_username(self):
        """Validate username is unique (excluding current user)"""
        username = self.cleaned_data.get('username')
        if username and self.instance:
            from accounts.models import User
            existing = User.objects.filter(username=username)
            if self.instance.user:
                existing = existing.exclude(pk=self.instance.user.pk)
            if existing.exists():
                raise ValidationError('A user with this username already exists.')
        return username
    
    def clean_email(self):
        """Validate email is unique (excluding current user)"""
        email = self.cleaned_data.get('email')
        if email and self.instance:
            from accounts.models import User
            existing = User.objects.filter(email=email)
            if self.instance.user:
                existing = existing.exclude(pk=self.instance.user.pk)
            if existing.exists():
                raise ValidationError('A user with this email already exists.')
        return email
    
    def clean_employee_id(self):
        """Validate employee ID is unique (excluding current employee)"""
        employee_id = self.cleaned_data.get('employee_id')
        if employee_id and self.instance:
            from accounts.models import Employee
            existing = Employee.objects.filter(employee_id=employee_id)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise ValidationError('An employee with this ID already exists.')
        return employee_id
    
    def clean_password(self):
        """Validate password strength if provided"""
        password = self.cleaned_data.get('password')
        if password and len(password) < 8:
            raise ValidationError('Password must be at least 8 characters long.')
        return password
    
    def clean(self):
        """Validate password confirmation if password is provided"""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and password != confirm_password:
            raise ValidationError('Passwords do not match.')
        
        return cleaned_data


class EmployeeSearchForm(forms.Form):
    """Form for searching and filtering employees"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search employees...',
            'id': 'employee-search'
        })
    )
    
    status = forms.ChoiceField(
        choices=[
            ('', 'All Status'),
            ('active', 'Active'),
            ('inactive', 'Inactive')
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'status-filter'
        })
    )
    
    specialization = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filter by specialization',
            'id': 'specialization-filter'
        })
    )


class EmployeeBulkActionForm(forms.Form):
    """Form for bulk operations on employees"""
    
    ACTION_CHOICES = [
        ('activate', 'Activate Selected'),
        ('deactivate', 'Deactivate Selected'),
        ('change_specialization', 'Change Specialization'),
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'bulk-action-select'
        })
    )
    
    selected_employees = forms.CharField(
        widget=forms.HiddenInput(),
        required=True
    )
    
    # Optional field for specialization change
    new_specialization = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new specialization',
            'id': 'new-specialization-input',
            'style': 'display: none;'
        })
    )
    
    def clean_selected_employees(self):
        """Validate selected employees"""
        selected = self.cleaned_data.get('selected_employees')
        if selected:
            try:
                employee_ids = [int(id.strip()) for id in selected.split(',') if id.strip()]
                if not employee_ids:
                    raise ValidationError('No employees selected.')
                return employee_ids
            except ValueError:
                raise ValidationError('Invalid employee selection.')
        raise ValidationError('No employees selected.')
    
    def clean(self):
        """Validate form data based on action"""
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        new_specialization = cleaned_data.get('new_specialization')
        
        if action == 'change_specialization' and not new_specialization:
            raise ValidationError('Please enter a specialization for the change specialization action.')
        
        return cleaned_data


# System Settings Forms

class SystemSettingsForm(forms.ModelForm):
    """Form for creating and updating system settings"""
    
    class Meta:
        model = SystemSettings
        fields = ['key', 'value', 'description']
        widgets = {
            'key': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter setting key (e.g., time_slot_duration)'
            }),
            'value': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter setting value'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter description of this setting'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['key'].required = True
        self.fields['value'].required = True
        self.fields['description'].required = False
    
    def clean_key(self):
        """Validate setting key format and uniqueness"""
        key = self.cleaned_data.get('key')
        if key:
            key = key.strip().lower()
            
            # Validate key format (alphanumeric and underscores only)
            import re
            if not re.match(r'^[a-z0-9_]+$', key):
                raise ValidationError('Setting key can only contain lowercase letters, numbers, and underscores.')
            
            # Check for existing setting with same key (excluding current instance)
            existing = SystemSettings.objects.filter(key=key)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise ValidationError('A setting with this key already exists.')
        
        return key
    
    def clean_value(self):
        """Validate setting value based on key type"""
        value = self.cleaned_data.get('value')
        key = self.cleaned_data.get('key', '')
        
        if value and key:
            # Validate specific setting types
            if key.endswith('_duration') or key.endswith('_time'):
                # Time-based settings should be in HH:MM format or minutes
                if ':' in value:
                    try:
                        hours, minutes = value.split(':')
                        int(hours)
                        int(minutes)
                    except ValueError:
                        raise ValidationError('Time values should be in HH:MM format.')
                else:
                    try:
                        int(value)
                    except ValueError:
                        raise ValidationError('Duration values should be in minutes or HH:MM format.')
            
            elif key.endswith('_count') or key.endswith('_limit') or key.endswith('_max'):
                # Numeric settings
                try:
                    num_value = int(value)
                    if num_value < 0:
                        raise ValidationError('Count/limit values must be non-negative.')
                except ValueError:
                    raise ValidationError('Count/limit values must be valid integers.')
            
            elif key.endswith('_enabled') or key.endswith('_active'):
                # Boolean settings
                if value.lower() not in ['true', 'false', '1', '0', 'yes', 'no']:
                    raise ValidationError('Boolean values should be true/false, 1/0, or yes/no.')
            
            elif key.endswith('_email') or 'email' in key:
                # Email settings
                from django.core.validators import validate_email
                try:
                    validate_email(value)
                except ValidationError:
                    raise ValidationError('Please enter a valid email address.')
            
            elif key.endswith('_json') or key.startswith('json_'):
                # JSON settings
                try:
                    json.loads(value)
                except json.JSONDecodeError:
                    raise ValidationError('Please enter valid JSON format.')
        
        return value


class SystemSettingsSearchForm(forms.Form):
    """Form for searching and filtering system settings"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search settings...',
            'id': 'settings-search'
        })
    )
    
    category = forms.ChoiceField(
        choices=[
            ('', 'All Categories'),
            ('time_slots', 'Time Slots'),
            ('appointments', 'Appointments'),
            ('notifications', 'Notifications'),
            ('system', 'System'),
            ('email', 'Email'),
            ('other', 'Other')
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'category-filter'
        })
    )


class SystemSettingsBulkActionForm(forms.Form):
    """Form for bulk operations on system settings"""
    
    ACTION_CHOICES = [
        ('reset_selected', 'Reset Selected to Defaults'),
        ('delete_selected', 'Delete Selected'),
        ('export_selected', 'Export Selected'),
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'bulk-action-select'
        })
    )
    
    selected_settings = forms.CharField(
        widget=forms.HiddenInput(),
        required=True
    )
    
    def clean_selected_settings(self):
        """Validate selected settings"""
        selected = self.cleaned_data.get('selected_settings')
        if selected:
            try:
                setting_ids = [int(id.strip()) for id in selected.split(',') if id.strip()]
                if not setting_ids:
                    raise ValidationError('No settings selected.')
                return setting_ids
            except ValueError:
                raise ValidationError('Invalid setting selection.')
        raise ValidationError('No settings selected.')


class SettingsImportForm(forms.Form):
    """Form for importing settings from JSON file"""
    
    json_file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.json',
            'id': 'json-file-input'
        }),
        help_text='Upload a JSON file with settings data'
    )
    
    overwrite_existing = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text='Check to overwrite existing settings with same keys'
    )
    
    def clean_json_file(self):
        """Validate JSON file"""
        json_file = self.cleaned_data.get('json_file')
        if json_file:
            # Check file size (max 1MB)
            if json_file.size > 1024 * 1024:
                raise ValidationError('JSON file size must be less than 1MB.')
            
            # Check file extension
            if not json_file.name.lower().endswith('.json'):
                raise ValidationError('Please upload a JSON file.')
            
            # Validate JSON content
            try:
                content = json_file.read().decode('utf-8')
                json_file.seek(0)  # Reset file pointer
                
                data = json.loads(content)
                if not isinstance(data, dict):
                    raise ValidationError('JSON file must contain a settings object.')
                
                # Validate required fields in each setting
                for key, setting_data in data.items():
                    if not isinstance(setting_data, dict):
                        raise ValidationError(f'Setting "{key}" must be an object.')
                    
                    if 'value' not in setting_data:
                        raise ValidationError(f'Setting "{key}" must have a "value" field.')
                        
            except UnicodeDecodeError:
                raise ValidationError('JSON file must be UTF-8 encoded.')
            except json.JSONDecodeError as e:
                raise ValidationError(f'Invalid JSON file: {str(e)}')
            except Exception as e:
                raise ValidationError(f'Error processing JSON file: {str(e)}')
        
        return json_file


class TimeSlotSettingsForm(forms.Form):
    """Form for configuring time slot settings"""
    
    slot_duration = forms.IntegerField(
        min_value=15,
        max_value=480,
        initial=60,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Duration in minutes'
        }),
        help_text='Duration of each time slot in minutes (15-480)'
    )
    
    start_time = forms.TimeField(
        initial='09:00',
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time'
        }),
        help_text='Business start time'
    )
    
    end_time = forms.TimeField(
        initial='18:00',
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time'
        }),
        help_text='Business end time'
    )
    
    break_start = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time'
        }),
        help_text='Break start time (optional)'
    )
    
    break_end = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time'
        }),
        help_text='Break end time (optional)'
    )
    
    advance_booking_days = forms.IntegerField(
        min_value=1,
        max_value=365,
        initial=30,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Number of days'
        }),
        help_text='How many days in advance customers can book (1-365)'
    )
    
    def clean(self):
        """Validate time slot configuration"""
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        break_start = cleaned_data.get('break_start')
        break_end = cleaned_data.get('break_end')
        
        if start_time and end_time:
            if start_time >= end_time:
                raise ValidationError('End time must be after start time.')
        
        if break_start and break_end:
            if break_start >= break_end:
                raise ValidationError('Break end time must be after break start time.')
            
            if start_time and end_time:
                if break_start < start_time or break_end > end_time:
                    raise ValidationError('Break times must be within business hours.')
        
        if (break_start and not break_end) or (break_end and not break_start):
            raise ValidationError('Both break start and end times must be specified.')
        
        return cleaned_data


class AppointmentSettingsForm(forms.Form):
    """Form for configuring appointment settings"""
    
    max_appointments_per_slot = forms.IntegerField(
        min_value=1,
        max_value=10,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Number of appointments'
        }),
        help_text='Maximum appointments per time slot (1-10)'
    )
    
    cancellation_deadline_hours = forms.IntegerField(
        min_value=1,
        max_value=168,
        initial=24,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Hours before appointment'
        }),
        help_text='Hours before appointment when cancellation is allowed (1-168)'
    )
    
    auto_confirm_appointments = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text='Automatically confirm new appointments'
    )
    
    send_reminder_notifications = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text='Send reminder notifications to customers'
    )
    
    reminder_hours_before = forms.IntegerField(
        min_value=1,
        max_value=168,
        initial=24,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Hours before appointment'
        }),
        help_text='Hours before appointment to send reminder (1-168)'
    )
    
    require_employee_assignment = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text='Require employee assignment for appointments'
    )


class NotificationSettingsForm(forms.Form):
    """Form for configuring notification settings"""
    
    admin_email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'admin@example.com'
        }),
        help_text='Email address for admin notifications'
    )
    
    from_email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'noreply@example.com'
        }),
        help_text='From email address for system notifications'
    )
    
    email_notifications_enabled = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text='Enable email notifications'
    )
    
    sms_notifications_enabled = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text='Enable SMS notifications'
    )
    
    notify_new_appointments = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text='Notify admin of new appointments'
    )
    
    notify_cancellations = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text='Notify admin of appointment cancellations'
    )
    
    notify_employee_assignments = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text='Notify employees of new assignments'
    )