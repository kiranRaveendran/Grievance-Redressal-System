import threading
import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView, LogoutView
from django.views.decorators.csrf import csrf_protect
from django.urls import reverse_lazy

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .forms import RegisterForm
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    AdminCreateUserSerializer,
)
from .permissions import IsAdminPanel
from accounts.utils.email_smtp import send_via_smtplib

User = get_user_model()



class CustomLoginView(LoginView):
    template_name = "accounts/login.html"

    def get_success_url(self):
        user = self.request.user

        if user.role == "admin":
            return reverse_lazy("adminpanel:dashboard")

        elif user.role == "officer":
            return reverse_lazy("officerpanel:dashboard")

        elif user.role == "citizen":
            return reverse_lazy("citizen:dashboard")  # ✅ DASHBOARD

        messages.error(self.request, "Unauthorized access.")
        return reverse_lazy("accounts:login")


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("accounts:login")



@csrf_protect
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = "citizen"
            user.is_active = True
            user.save()

           
            def send_mail_bg():
                try:
                    send_via_smtplib(
                        to_email=user.email,
                        subject="Welcome to Grievance Redressal System",
                        plain_text=f"Hi {user.username}, your account is ready.",
                    )
                except Exception as e:
                    logging.warning("Email failed: %s", e)

            threading.Thread(target=send_mail_bg, daemon=True).start()

            messages.success(request, "Registration successful. Please login.")
            return redirect("accounts:login")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})




class RegisterAPI(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save(role="citizen")
            return Response(UserSerializer(user).data, status=201)
        return Response(serializer.errors, status=400)


class MeAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


class AdminUserListCreateAPI(APIView):
    permission_classes = [IsAuthenticated, IsAdminPanel]

    def get(self, request):
        users = User.objects.all()
        return Response(UserSerializer(users, many=True).data)

    def post(self, request):
        serializer = AdminCreateUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=201)
        return Response(serializer.errors, status=400)


class AdminUserDetailAPI(APIView):
    permission_classes = [IsAuthenticated, IsAdminPanel]

    def get_object(self, pk):
        return get_object_or_404(User, pk=pk)

    def get(self, request, pk):
        return Response(UserSerializer(self.get_object(pk)).data)

    def patch(self, request, pk):
        user = self.get_object(pk)
        serializer = AdminCreateUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(UserSerializer(user).data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        user = self.get_object(pk)
        user.delete()
        return Response(status=204)
