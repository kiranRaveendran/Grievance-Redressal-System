from django.urls import path
from . import views

app_name = 'citizen'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('grievances/', views.grievances_list, name='grievances_list'),
    path('grievances/<int:pk>/', views.grievance_detail, name='grievance_detail'),
    path('grievance/<int:grievance_id>/feedback/', views.submit_feedback, name='submit_feedback'),
    path('submit/', views.submit_grievance, name='submit_grievance'),
    path('notifications/', views.notifications, name='notifications'),
    path('profile/', views.profile, name='profile'),
]






