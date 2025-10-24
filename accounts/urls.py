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
    
    # Super Employee Management URLs
    path('assign-task/', views.assign_task_view, name='assign_task'),
    path('update-employee-status/', views.update_employee_status_view, name='update_employee_status'),
    path('task-assignment/<int:assignment_id>/', views.task_assignment_detail_view, name='task_assignment_detail'),
    path('update-task-status/<int:assignment_id>/<str:status>/', views.update_task_status_view, name='update_task_status'),
]
