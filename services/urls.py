from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('', views.service_list_view, name='service_list'),
    path('category/<int:category_id>/', views.category_detail_view, name='category_detail'),
    path('<int:service_id>/', views.service_detail_view, name='service_detail'),
    path('<int:service_id>/book/', views.book_service_view, name='book_service'),
]
