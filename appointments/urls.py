from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('book/', views.book_appointment_view, name='book_appointment'),
    path('my-appointments/', views.my_appointments_view, name='my_appointments'),
    path('list/', views.appointment_list_view, name='appointment_list'),
    path('<int:appointment_id>/', views.appointment_detail_view, name='appointment_detail'),
    path('<int:appointment_id>/cancel/', views.cancel_appointment_view, name='cancel_appointment'),
    path('<int:appointment_id>/update-status/', views.update_appointment_status_view, name='update_status'),
    path('api/available-slots/', views.get_available_slots_api, name='available_slots_api'),
    path('slot-occupancy/', views.slot_occupancy_view, name='slot_occupancy'),
]
