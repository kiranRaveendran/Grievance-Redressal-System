from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from django.views.decorators.csrf import csrf_protect

from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth import logout
from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField
from django.utils.timezone import now, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Grievance  
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework.parsers import JSONParser
from rest_framework import status
from django.db.models.functions import TruncDate
from citizen.models import Grievance, Category
from .models import OfficerAction
from .serializers import (GrievanceSerializer, OfficerProfileSerializer, OfficerPasswordChangeSerializer)
from django.conf import settings
from django.contrib.auth.views import redirect_to_login




# -----------------------
# OFFICER PERMISSION CHECK
# -----------------------
class OfficerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and getattr(user, "role", None) == "officer"

    def handle_no_permission(self):
        return redirect_to_login(
            self.request.get_full_path(),
            login_url="accounts:login"
        )

# ======================================================
# 1️⃣ Officer Dashboard Page (HTML)
# ======================================================
class OfficerDashboardView(LoginRequiredMixin, OfficerRequiredMixin, TemplateView):
    template_name = "officer/dashboard.html"
   
# ======================================================
# 2️⃣ Officer Dashboard API
# ======================================================

class OfficerDashboardAPI(APIView):
    authentication_classes = [JWTAuthentication]   
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            if request.user.is_superuser:
                grievances = Grievance.objects.all()
            else:
                grievances = Grievance.objects.filter(assigned_to=request.user)

            counts = grievances.values("status").annotate(total=Count("id"))
            count_dict = {item["status"]: item["total"] for item in counts}

            return Response({
                "name": request.user.username,  
                "pending": count_dict.get("pending", 0),
                "in_progress": count_dict.get("in_progress", 0),
                "resolved": count_dict.get("resolved", 0)
            })

        except Exception as e:
            return Response({"error": str(e)}, status=500)
# ======================================================
# 3️⃣ Officer Grievance Page (HTML)
# ======================================================
class OfficerGrievancePageView(LoginRequiredMixin, OfficerRequiredMixin, TemplateView):
    template_name = "officer/officer_grievances.html"
   
# ======================================================
# 4️⃣ Officer Filter Grievance API
# ======================================================
class OfficerFilterGrievanceAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        category = request.GET.get("category")

        if request.user.is_superuser:
            grievances = Grievance.objects.all()
        else:
            grievances = Grievance.objects.filter(assigned_to=request.user)

        if category:
            grievances = grievances.filter(category__id=category)

        serializer = GrievanceSerializer(grievances, many=True)
        categories = Category.objects.all().values("id", "name")

        return Response({
            "grievances": serializer.data,
            "categories": list(categories)
        }, status=200)

# ======================================================
# 5️⃣ Update Grievance Status API
# ======================================================

class UpdateGrievanceStatusAPI(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def post(self, request):
        print("REQUEST DATA:", request.data)

        grievance_id = request.data.get("grievance_id")
        status = request.data.get("status")

        if not grievance_id or not status:
            return Response(
                {"error": "grievance_id and status are required"},
                status=400
            )

        try:
            grievance = Grievance.objects.get(id=grievance_id)

            # ✅ Update grievance status
            grievance.status = status
            grievance.save()

            # ✅ Log officer action
            OfficerAction.objects.create(
                officer=request.user,
                grievance=grievance,
                action_taken=f"Status updated to {status}",
                updated_status=status
            )

            return Response(
                {"message": "Grievance status updated successfully"},
                status=200
            )

        except Grievance.DoesNotExist:
            return Response(
                {"error": "Grievance not found"},
                status=404
            )
# ======================================================
# 6️⃣ Officer Analytics Page (HTML)
# ======================================================
class OfficerAnalyticsView(LoginRequiredMixin, OfficerRequiredMixin, TemplateView):
    template_name = "officer/officer_analytics.html"
 

# ======================================================
# 7️⃣ Officer Analytics API
# ======================================================
class OfficerAnalyticsAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # SUPERUSER: see all grievances
        if request.user.is_superuser:
            grievances = Grievance.objects.all()
        else:
            # OFFICER: only assigned grievances
            grievances = Grievance.objects.filter(
                assigned_to=request.user
            )

        total = grievances.count()
        pending = grievances.filter(status='pending').count()
        in_progress = grievances.filter(status='in_progress').count()
        resolved = grievances.filter(status='resolved').count()

        # Average resolution time
        resolved_qs = grievances.filter(status='resolved').annotate(
            resolution_duration=ExpressionWrapper(
                F('updated_at') - F('created_at'),
                output_field=DurationField()
            )
        )

        avg_duration = resolved_qs.aggregate(
            avg_resolution=Avg('resolution_duration')
        )['avg_resolution']

        avg_days = (
            round(avg_duration.total_seconds() / (24 * 3600), 2)
            if avg_duration else "—"
        )

        # Daily trend
        daily_trend_qs = (
            grievances
            .annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(count=Count('id'))
            .order_by('date')
        )

        daily_trend = [
            {
                'date': x['date'].strftime('%Y-%m-%d'),
                'count': x['count']
            }
            for x in daily_trend_qs
        ]

        return Response({
            "total_grievances": total,
            "pending": pending,
            "in_progress": in_progress,
            "resolved": resolved,
            "avg_resolution_days": avg_days,
            "daily_trend": daily_trend
        })
# ======================================================
# 8️⃣ Officer Settings Page
# ======================================================
class OfficerSettingsView(LoginRequiredMixin, OfficerRequiredMixin, TemplateView):
    template_name = "officer/officer_settings.html"
   

# ======================================================
# 9️⃣ Officer Profile API
# ======================================================

class OfficerProfileAPI(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        name = request.data.get("name")

        if not name:
            return Response(
                {"error": "Name is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = request.user
        user.first_name = name
        user.save()

        return Response(
            {
                "message": "Profile updated successfully",
                "first_name": user.first_name,
            },
            status=status.HTTP_200_OK
        )
# ======================================================
# 🔟 Officer Change Password API
# ======================================================

class OfficerPasswordChangeAPI(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not old_password or not new_password:
            return Response(
                {"error": "Both old and new passwords are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = request.user

        # Check old password
        if not user.check_password(old_password):
            return Response(
                {"error": "Old password is incorrect"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Set new password
        user.set_password(new_password)
        user.save()

        return Response(
            {"message": "Password changed successfully"},
            status=status.HTTP_200_OK
        )
# ======================================================
# 🔚 Logout
# ======================================================
def logout_view(request):
    logout(request)
    return redirect(settings.LOGIN_URL)
