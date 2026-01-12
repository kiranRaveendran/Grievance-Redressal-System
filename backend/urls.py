from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('adminpanel/', include('adminpanel.urls')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('officer/', include('officerpanel.urls')),
    path('citizen/', include('citizen.urls')),
    # Auth
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    # Redirect root to login
    path('', RedirectView.as_view(pattern_name='accounts:login', permanent=False)),
]







