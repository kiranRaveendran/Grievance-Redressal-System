from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    citizen_dashboard,
    feed_page,
    submit_grievance,
    view_grievance_page,
    citizen_profile,
    submit_feedback,
    citizen_logout,
    GrievanceCreateAPI,
    FeedbackCreateAPI,
    CitizenProfileAPI
)

app_name = 'citizen'

urlpatterns = [
    path("dashboard/", citizen_dashboard, name="dashboard"),
    path("feed/", feed_page, name="feed_page"),
    path("submit-grievance/", submit_grievance, name="submit_grievance"),
    path("view-grievance/", view_grievance_page, name="view_grievance"),
    path("profile/", citizen_profile, name="profile"),
    path("submit-feedback/", submit_feedback, name="submit_feedback"),
    path("logout/", citizen_logout, name="citizen_logout"),
    path("login/", auth_views.LoginView.as_view(template_name="accounts/login.html"), name="login"),

    # API endpoints
    path("api/grievances/", GrievanceCreateAPI.as_view(), name="api_grievances"),
    path("api/feedback/", FeedbackCreateAPI.as_view(), name="api_feedback"),
    path("api/profile/", CitizenProfileAPI.as_view(), name="api_profile"),
    
]
