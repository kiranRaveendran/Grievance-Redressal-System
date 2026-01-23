from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import logout
from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField
from django.db.models.functions import TruncDate
from rest_framework.parsers import JSONParser
from rest_framework.authentication import TokenAuthentication

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework import status
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from citizen.models import Grievance, Category
from officer.models import OfficerAction
from .serializers import (
    GrievanceSerializer,
    OfficerProfileSerializer,
    OfficerPasswordChangeSerializer
)

# ======================================================
# STATUS NORMALIZATION (🔥 MOST IMPORTANT)
# ======================================================
STATUS_NORMALIZE = {
    "pending": "Pending",
    "Pending": "Pending",
    "in_progress": "In Progress",
    "In Progress": "In Progress",
    "resolved": "Resolved",
    "Resolved": "Resolved",
}

# ======================================================
# OFFICER PERMISSION MIXIN
# ======================================================
class OfficerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and getattr(self.request.user, "role", None) == "officer"

    def handle_no_permission(self):
        return redirect_to_login(self.request.get_full_path(), login_url="accounts:login")

# ======================================================
# 1️⃣ Officer Dashboard Page
# ======================================================
@method_decorator(never_cache, name='dispatch')
class OfficerDashboardView(LoginRequiredMixin, OfficerRequiredMixin, TemplateView):
    template_name = "officer/dashboard.html"

# ======================================================
# 2️⃣ Officer Dashboard API
# ======================================================
class OfficerDashboardAPI(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_superuser:
            grievances = Grievance.objects.all()
        else:
            grievances = Grievance.objects.filter(assigned_to=request.user)

        return Response({
            "name": request.user.username,
            "pending": grievances.filter(status="pending").count(),
            "in_progress": grievances.filter(status="in_progress").count(),
            "resolved": grievances.filter(status="resolved").count(),
        })

# ======================================================
# 3️⃣ Officer Grievance Page
# ======================================================
@method_decorator(never_cache, name='dispatch')
class OfficerGrievancePageView(LoginRequiredMixin, OfficerRequiredMixin, TemplateView):
    template_name = "officer/officer_grievances.html"

# ======================================================
# 4️⃣ Officer Filter Grievance API
# ======================================================
class OfficerFilterGrievanceAPI(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        category = request.GET.get("category")

        if request.user.is_superuser:
            grievances = Grievance.objects.all()
        else:
            grievances = Grievance.objects.filter(assigned_to=request.user)

        if category:
            grievances = grievances.filter(category__id=category)

        serializer = GrievanceSerializer(grievances, many=True, context={"request": request})
        categories = Category.objects.all().values("id", "name")

        return Response({
            "grievances": serializer.data,
            "categories": list(categories)
        })


# ======================================================
# 5️⃣ Update Grievance Status API (🔥 FIXED)
# ======================================================

class UpdateGrievanceStatusAPI(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def post(self, request):
        grievance_id = request.data.get("grievance_id")
        status = request.data.get("status")

        if not grievance_id or not status:
            return Response({"error": "Missing data"}, status=400)

        if status not in ["pending", "in_progress", "resolved"]:
            return Response({"error": "Invalid status"}, status=400)

        try:
            grievance = Grievance.objects.get(id=grievance_id)
            grievance.status = status
            grievance.save()

            return Response({
                "success": True,
                "status": grievance.status
            })

        except Grievance.DoesNotExist:
            return Response({"error": "Not found"}, status=404)
# ======================================================
# 6️⃣ Officer Analytics Page
# ======================================================
class OfficerAnalyticsView(LoginRequiredMixin, OfficerRequiredMixin, TemplateView):
    template_name = "officer/officer_analytics.html"

# ======================================================
# 7️⃣ Officer Analytics API
# ======================================================


class OfficerAnalyticsAPI(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):

        if request.user.is_superuser:
            grievances = Grievance.objects.all()
        else:
            grievances = Grievance.objects.filter(assigned_to=request.user)

        total = grievances.count()

        # ✅ CORRECT STATUS VALUES
        pending = grievances.filter(status="pending").count()
        in_progress = grievances.filter(status="in_progress").count()
        resolved = grievances.filter(status="resolved").count()

        # ✅ AVG RESOLUTION TIME
        resolved_qs = grievances.filter(status="resolved").annotate(
            resolution_duration=ExpressionWrapper(
                F("updated_at") - F("created_at"),
                output_field=DurationField()
            )
        )

        avg_duration = resolved_qs.aggregate(
            avg=Avg("resolution_duration")
        )["avg"]

        avg_days = (
            round(avg_duration.total_seconds() / 86400, 2)
            if avg_duration else "—"
        )

        # ✅ DAILY TREND
        daily_trend_qs = (
            grievances
            .annotate(date=TruncDate("created_at"))
            .values("date")
            .annotate(count=Count("id"))
            .order_by("date")
        )

        daily_trend = [
            {
                "date": x["date"].strftime("%Y-%m-%d"),
                "count": x["count"]
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

    def get(self, request):
        return Response({"name": request.user.first_name or ""})

    def post(self, request):
        name = request.data.get("name")
        if not name:
            return Response({"error": "Name required"}, status=400)

        request.user.first_name = name
        request.user.save()
        return Response({"message": "Profile updated", "first_name": name})

# ======================================================
# 🔟 Officer Password Change API
# ======================================================
class OfficerPasswordChangeAPI(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        old = request.data.get("old_password")
        new = request.data.get("new_password")

        if not request.user.check_password(old):
            return Response({"error": "Wrong old password"}, status=400)

        request.user.set_password(new)
        request.user.save()
        return Response({"message": "Password changed"})

# ======================================================
# 🔚 Logout
# ======================================================
def logout_view(request):
    logout(request)
    return redirect('accounts:login')
