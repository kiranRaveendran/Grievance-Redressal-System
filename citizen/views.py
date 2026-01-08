from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.authentication import TokenAuthentication

from .models import Grievance, Feedback, CitizenProfile, GrievanceView
from .forms import GrievanceForm
from .serializers import FeedbackSerializer, GrievanceSerializer, CitizenProfileSerializer

User = get_user_model()


# -------------------- NORMAL VIEWS --------------------

@login_required(login_url='/accounts/login/')
def feed_page(request):
    form = GrievanceForm()
    return render(request, "citizen/feed.html", {"form": form})


@login_required(login_url='/accounts/login/')
def submit_grievance(request):
    if request.method == "POST":
        Grievance.objects.create(
            citizen=request.user,
            title=request.POST.get("title"),
            description=request.POST.get("description"),
            category=request.POST.get("category"),
            attachments=request.FILES.get("attachments")
        )
        messages.success(request, "Your grievance has been submitted successfully.")
        return redirect("citizen:dashboard")
    return render(request, "citizen/feed.html")


@login_required(login_url='/accounts/login/')
def citizen_dashboard(request):
    grievances = Grievance.objects.filter(citizen=request.user)
    return render(request, "citizen/dashboard.html", {
        "total_open": grievances.exclude(status="Resolved").count(),
        "total_all": grievances.count(),
        "recent_grievances": grievances.order_by('-date')[:5],
    })


@login_required(login_url='/accounts/login/')
def view_grievance_page(request):
    grievance = Grievance.objects.filter(citizen=request.user).order_by('-date').first()
    grievance_view = GrievanceView.objects.filter(grievance=grievance).first() if grievance else None
    return render(request, 'citizen/grievanceview.html', {
        'grievance': grievance,
        'grievance_view': grievance_view
    })


@login_required(login_url='/accounts/login/')
def citizen_profile(request):
    profile, _ = CitizenProfile.objects.get_or_create(user=request.user)
    grievances = Grievance.objects.filter(citizen=request.user).order_by('-date')

    if request.method == "POST":
        if "save_profile" in request.POST:
            profile.phone = request.POST.get("phone", "")
            profile.address = request.POST.get("address", "")
            if request.FILES.get("profile_image"):
                profile.profile_image = request.FILES["profile_image"]
            profile.save()
            messages.success(request, "Profile updated successfully")
            return redirect("citizen:profile")

        elif "change_password" in request.POST:
            old = request.POST.get("old_password")
            new = request.POST.get("new_password")
            confirm = request.POST.get("confirm_password")

            if new != confirm:
                messages.error(request, "Passwords do not match")
            elif not request.user.check_password(old):
                messages.error(request, "Old password incorrect")
            else:
                request.user.set_password(new)
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, "Password changed successfully")
            return redirect("citizen:profile")

    return render(request, "citizen/profile.html", {
        "profile": profile,
        "grievances": grievances
    })


@login_required(login_url='/accounts/login/')
def submit_feedback(request):
    if request.method == "POST":
        message = request.POST.get("message")
        rating = request.POST.get("rating")

        if not rating:
            messages.error(request, "Please select a rating.")
            return redirect("citizen:dashboard")

        Feedback.objects.create(user=request.user, message=message, rating=int(rating))
        messages.success(request, "Feedback submitted successfully.")
        return redirect("citizen:dashboard")


def citizen_logout(request):
    logout(request)
    return redirect("citizen:login")


# -------------------- API VIEWS --------------------

class GrievanceCreateAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = GrievanceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(citizen=request.user, date=timezone.now())
            return Response({"message": "Grievance submitted successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class FeedbackCreateAPI(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]


    def post(self, request):
        serializer = FeedbackSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(
                {"message": "Feedback submitted successfully"},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class CitizenProfileAPI(APIView):
    permission_classes = [IsAuthenticated]


    def get(self, request):
        profile, _ = CitizenProfile.objects.get_or_create(user=request.user)
        serializer = CitizenProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        profile, _ = CitizenProfile.objects.get_or_create(user=request.user)
        serializer = CitizenProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated successfully"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




 



