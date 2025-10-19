from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('employee-dashboard/', views.employee_dashboard_view, name='employee_dashboard'),
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('appointment-history/', views.appointment_history_view, name='appointment_history'),
]
