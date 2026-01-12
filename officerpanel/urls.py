from django.urls import path
from . import views

app_name = "officerpanel"

urlpatterns = [
    # Template views
    path("", views.officer_dashboard, name="dashboard"),
    path("grievances/", views.officer_grievances_list, name="grievances_list"),
    path("grievances/<int:pk>/", views.officer_grievance_detail_view, name="grievance_detail"),

    # API endpoints
    path(
        "api/grievances/",
        views.api_officer_grievances_list,
        name="api_grievances_list"
    ),
    path(
        "api/grievances/<int:pk>/",
        views.api_officer_grievance_detail,
        name="api_grievance_detail"
    ),
    path(
        "api/grievances/<int:pk>/remark/",
        views.api_officer_add_remark,
        name="api_add_remark"
    ),
    path(
        "api/grievances/<int:pk>/status/",
        views.api_officer_update_status,
        name="api_update_status"
    ),
    path(
        "api/grievances/<int:pk>/feedback/",
        views.api_officer_submit_feedback,
        name="api_feedback"
    ),
]



