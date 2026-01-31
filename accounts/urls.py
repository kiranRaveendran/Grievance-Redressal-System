from django.urls import path
from .views import CustomLoginView, CustomLogoutView, register_view
from django.contrib.auth import views as auth_views

app_name = 'accounts'
urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('register/', register_view, name='register'),


]


