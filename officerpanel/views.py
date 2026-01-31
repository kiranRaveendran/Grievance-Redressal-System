from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import status as drf_status

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from adminpanel.models import Grievance, GrievanceRemark, Feedback,Category
from .serializers import (
    OfficerGrievanceListSerializer,
    OfficerGrievanceDetailSerializer,
    OfficerAddRemarkSerializer,
    OfficerFeedbackSerializer
)

# =====================================================
# PERMISSION HELPER
# =====================================================

def is_officer(user):
    return (
        user.is_authenticated and
        getattr(user, "role", None) == "officer"
    )

# =====================================================
# TEMPLATE VIEWS
# =====================================================

# officerpanel/views.py

@login_required
def officer_dashboard(request):
    user = request.user
    if not user.is_officer():
        return render(request, "403.html", status=403)

    categories = [
        "Public Complaints",
        "Service Requests",
        "Infrastructure",
        "Legal Issues",
        "Sanitation",
        "Other"
    ]

    category_data = []

    for cat_name in categories:
        # Get the category object first
        try:
            cat_obj = Category.objects.get(name=cat_name)
        except Category.DoesNotExist:
            continue  # skip if category not defined

        grievances = Grievance.objects.filter(assigned_officer=user, category=cat_obj)
        category_data.append({
            "name": cat_name,
            "total": grievances.count(),
            "pending": grievances.filter(status=Grievance.STATUS_PENDING).count(),
            "in_progress": grievances.filter(status=Grievance.STATUS_IN_PROGRESS).count(),
            "resolved": grievances.filter(status=Grievance.STATUS_RESOLVED).count(),
            "feedback_pending": grievances.filter(status=Grievance.STATUS_RESOLVED).exclude(feedback__isnull=False).count(),
            "feedback_done": grievances.filter(status=Grievance.STATUS_RESOLVED, feedback__isnull=False).count(),
        })

    context = {"categories": category_data, "user": user}
    return render(request, "officerpanel/dashboard.html", context)

@login_required
def officer_grievances_list(request):
    if not is_officer(request.user):
        return render(request, "403.html", status=403)

    return render(request, "officerpanel/grievances_list.html")


@login_required
def officer_grievance_detail_view(request, pk):
    if not is_officer(request.user):
        return render(request, "403.html", status=403)

    return render(
        request,
        "officerpanel/grievance_detail.html",
        {"grievance_id": pk}
    )

# =====================================================
# API VIEWS
# =====================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_officer_grievances_list(request):
    if not is_officer(request.user):
        return Response({"detail": "Not authorized"}, status=403)

    grievances = Grievance.objects.filter(
        assigned_officer=request.user
    ).order_by("-created_at")

    serializer = OfficerGrievanceListSerializer(grievances, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_officer_grievance_detail(request, pk):
    if not is_officer(request.user):
        return Response({"detail": "Not authorized"}, status=403)

    grievance = get_object_or_404(
        Grievance,
        pk=pk,
        assigned_officer=request.user
    )

    serializer = OfficerGrievanceDetailSerializer(grievance)
    return Response(serializer.data)


@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_officer_add_remark(request, pk):
    if not is_officer(request.user):
        return Response({"detail": "Not authorized"}, status=403)

    grievance = get_object_or_404(
        Grievance,
        pk=pk,
        assigned_officer=request.user
    )

    serializer = OfficerAddRemarkSerializer(data=request.data)
    if serializer.is_valid():
        remark = serializer.save(
            grievance=grievance,
            officer=request.user
        )
        return Response(
            {
                "remark": remark.remark,
                "created_at": remark.created_at
            },
            status=201
        )

    return Response(serializer.errors, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_officer_update_status(request, pk):
    """
    Update status of grievance by officer
    Send email to citizen if status is resolved
    """
    try:
        grievance = Grievance.objects.get(pk=pk)
    except Grievance.DoesNotExist:
        return Response({"detail": "Grievance not found."}, status=drf_status.HTTP_404_NOT_FOUND)

    new_status = request.data.get('status')
    if new_status not in ['pending', 'in_progress', 'resolved']:
        return Response({"detail": "Invalid status"}, status=drf_status.HTTP_400_BAD_REQUEST)

    grievance.status = new_status
    grievance.save()

    # Send email if resolved
    if new_status == 'resolved' and grievance.user.email:
        subject = f"Your grievance {grievance.tracking_id} has been resolved"
        message = f"""
Hello {grievance.user.first_name or grievance.user.username},

Your grievance titled "{grievance.title}" has been marked as RESOLVED by our officer.

You can view your grievance details here: 
http://{request.get_host()}/grievances/{grievance.pk}/

Thank you,
Grievance Redressal System
"""
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [grievance.user.email],
            fail_silently=False
        )

    return Response({"detail": "Status updated successfully."})
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_officer_submit_feedback(request, pk):
    if not is_officer(request.user):
        return Response({"detail": "Not authorized"}, status=403)

    grievance = get_object_or_404(
        Grievance,
        pk=pk,
        assigned_officer=request.user
    )

    if grievance.status != Grievance.STATUS_RESOLVED:
        return Response(
            {"detail": "Feedback allowed only for resolved grievances"},
            status=400
        )

    serializer = OfficerFeedbackSerializer(data=request.data)
    if serializer.is_valid():
        feedback, _ = Feedback.objects.get_or_create(grievance=grievance)

        for field, value in serializer.validated_data.items():
            setattr(feedback, field, value)

        feedback.save()
        return Response({"detail": "Feedback submitted"}, status=201)

    return Response(serializer.errors, status=400)
