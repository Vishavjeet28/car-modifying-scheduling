# Generated manually to clear existing data and simplify appointment model

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


def clear_existing_data(apps, schema_editor):
    """Clear existing appointment data to avoid conflicts"""
    Appointment = apps.get_model('appointments', 'Appointment')
    AppointmentHistory = apps.get_model('appointments', 'AppointmentHistory')
    TimeSlot = apps.get_model('appointments', 'TimeSlot')
    
    # Clear all existing data
    AppointmentHistory.objects.all().delete()
    Appointment.objects.all().delete()
    TimeSlot.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0001_initial'),
        ('services', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Clear existing data first
        migrations.RunPython(clear_existing_data, migrations.RunPython.noop),
        
        # Remove the old models
        migrations.DeleteModel(
            name='AppointmentHistory',
        ),
        migrations.DeleteModel(
            name='TimeSlot',
        ),
        
        # Remove fields from Appointment that we don't need
        migrations.RemoveField(
            model_name='appointment',
            name='time_slot',
        ),
        migrations.RemoveField(
            model_name='appointment',
            name='employee',
        ),
        migrations.RemoveField(
            model_name='appointment',
            name='priority',
        ),
        migrations.RemoveField(
            model_name='appointment',
            name='estimated_price',
        ),
        migrations.RemoveField(
            model_name='appointment',
            name='final_price',
        ),
        migrations.RemoveField(
            model_name='appointment',
            name='confirmed_at',
        ),
        migrations.RemoveField(
            model_name='appointment',
            name='completed_at',
        ),
        migrations.RemoveField(
            model_name='appointment',
            name='customer_notes',
        ),
        migrations.RemoveField(
            model_name='appointment',
            name='employee_notes',
        ),
        migrations.RemoveField(
            model_name='appointment',
            name='admin_notes',
        ),
        
        # Rename service to selected_service
        migrations.RenameField(
            model_name='appointment',
            old_name='service',
            new_name='selected_service',
        ),
        
        # Update customer field relationship
        migrations.AlterField(
            model_name='appointment',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appointments', to=settings.AUTH_USER_MODEL),
        ),
        
        # Add new fields
        migrations.AddField(
            model_name='appointment',
            name='slot_date',
            field=models.DateField(default='2025-10-15'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='appointment',
            name='slot_time',
            field=models.CharField(choices=[('09:00', '9:00 AM'), ('11:00', '11:00 AM'), ('13:00', '1:00 PM'), ('15:00', '3:00 PM'), ('17:00', '5:00 PM')], default='09:00', max_length=5),
            preserve_default=False,
        ),
        
        # Update status choices
        migrations.AlterField(
            model_name='appointment',
            name='status',
            field=models.CharField(choices=[('booked', 'Booked'), ('cancelled', 'Cancelled'), ('completed', 'Completed')], default='booked', max_length=20),
        ),
        
        # Add unique constraint
        migrations.AlterUniqueTogether(
            name='appointment',
            unique_together={('customer', 'slot_date')},
        ),
    ]