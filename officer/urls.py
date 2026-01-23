
from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView
from .views import (
    OfficerDashboardView,
    OfficerDashboardAPI,
    OfficerAnalyticsView,
    OfficerAnalyticsAPI,
    OfficerGrievancePageView,
    OfficerFilterGrievanceAPI,
    UpdateGrievanceStatusAPI,
    OfficerSettingsView,
    OfficerProfileAPI,
    OfficerPasswordChangeAPI
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

app_name = 'officer'

urlpatterns = [


    # ================= DASHBOARD ==================
    path('dashboard/', OfficerDashboardView.as_view(), name='dashboard'),
    path('dashboard/api/', OfficerDashboardAPI.as_view(), name='officer_dashboard_api'),

    # ================= GRIEVANCES =================
    # Page
    path('grievances/', OfficerGrievancePageView.as_view(), name='officer_grievances'),

    # APIs
    path('get_grievances/', OfficerFilterGrievanceAPI.as_view(), name='get_grievances'),

    path('update-grievance-status/',UpdateGrievanceStatusAPI.as_view(),name='update_grievance_status_api'),

    # ================= ANALYTICS ==================
    path('analytics/', OfficerAnalyticsView.as_view(), name='officer_analytics'),
    path('analytics/api/', OfficerAnalyticsAPI.as_view(), name='officer_analytics_api'),

    # ================= SETTINGS ===================
    path('settings/', OfficerSettingsView.as_view(), name='officer_settings'),
    path('settings/api/profile/', OfficerProfileAPI.as_view(), name='officer_profile_api'),
    path('settings/api/change-password/', OfficerPasswordChangeAPI.as_view(), name='officer_password_api'),

    # ================= AUTH ========================
    path('logout/', views.logout_view, name='logout'),

    
]
