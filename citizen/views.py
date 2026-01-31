from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import os

from adminpanel.models import Grievance, Feedback
from .forms import CitizenGrievanceForm, CitizenFeedbackForm
from django.contrib.auth import update_session_auth_hash
from .models import Profile


# -----------------------------
# CITIZEN DASHBOARD
# -----------------------------
@login_required
def dashboard(request):
    total = Grievance.objects.filter(user=request.user).count()
    new_count = Grievance.objects.filter(user=request.user, status=Grievance.STATUS_NEW).count()
    in_progress_count = Grievance.objects.filter(user=request.user, status=Grievance.STATUS_IN_PROGRESS).count()
    resolved_count = Grievance.objects.filter(user=request.user, status=Grievance.STATUS_RESOLVED).count()
    escalated_count = Grievance.objects.filter(user=request.user, status=Grievance.STATUS_ESCALATED).count()

    return render(request, "citizen/dashboard.html", {
        "total_grievances": total,
        "new_grievances": new_count,
        "in_progress_grievances": in_progress_count,
        "resolved_grievances": resolved_count,
        "escalated_grievances": escalated_count,
    })


# -----------------------------
# LIST OF GRIEVANCES
# -----------------------------
@login_required
def grievances_list(request):
    grievances = Grievance.objects.filter(user=request.user).order_by("-created_at")

    return render(request, "citizen/grievances_list.html", {
        "grievances": grievances,
        "total_grievances": grievances.count(),
        "new_grievances": grievances.filter(status=Grievance.STATUS_NEW).count(),
        "in_progress_grievances": grievances.filter(status=Grievance.STATUS_IN_PROGRESS).count(),
        "resolved_grievances": grievances.filter(status=Grievance.STATUS_RESOLVED).count(),
        "escalated_grievances": grievances.filter(status=Grievance.STATUS_ESCALATED).count(),
    })

# -----------------------------
# GRIEVANCE DETAIL
# -----------------------------
def grievance_detail(request, pk):
    grievance = get_object_or_404(Grievance, pk=pk)

    # Check if attached file is an image
    is_image = False
    attached_file_url = None
    if grievance.attached_file:
        attached_file_url = grievance.attached_file.url
        ext = os.path.splitext(grievance.attached_file.name)[1].lower()
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            is_image = True

    return render(request, "citizen/grievance_detail.html", {
        "grievance": grievance,
        "attached_file_url": attached_file_url,
        "is_image": is_image
    })


# -----------------------------
# SUBMIT GRIEVANCE
# -----------------------------
@login_required
def submit_grievance(request):
    if request.method == "POST":
        form = CitizenGrievanceForm(request.POST, request.FILES)

        if form.is_valid():
            grievance = form.save(commit=False)
            grievance.user = request.user
            grievance.save()

            return redirect("citizen:grievances_list")
        else:
            print(form.errors)  # DEBUG (important)

    else:
        form = CitizenGrievanceForm()

    return render(request, "citizen/submit_grievance.html", {
        "form": form
    })
@login_required
def submit_feedback(request, grievance_id):
    grievance = get_object_or_404(Grievance, pk=grievance_id)

    if request.method == "POST":
        form = CitizenFeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.grievance = grievance
            feedback.save()
            messages.success(request, "Feedback submitted successfully!")
            return redirect("citizen:grievance_detail", pk=grievance.id)
        else:
            print(form.errors)
    else:
        form = CitizenFeedbackForm()

    return render(request, "citizen/submit_feedback.html", {
        "form": form,
        "grievance": grievance
    })
def notifications(request):
    # Example: show empty notifications page
    return render(request, 'citizen/notifications.html')


@login_required
def profile(request):
    # Ensure the user has a profile
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        # Handle profile update
        if request.POST.get("update_profile"):
            name = request.POST.get("name")
            phone = request.POST.get("phone")
            address = request.POST.get("address")

            # Update User first name
            request.user.first_name = name
            request.user.save()

            # Update Profile
            profile.phone = phone
            profile.address = address
            profile.save()

            messages.success(request, "Profile updated successfully!")
            return redirect("citizen:profile")

        # Handle password change
        elif request.POST.get("change_password"):
            current_password = request.POST.get("current_password")
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")

            if not request.user.check_password(current_password):
                messages.error(request, "Current password is incorrect.")
            elif new_password != confirm_password:
                messages.error(request, "New passwords do not match.")
            else:
                request.user.set_password(new_password)
                request.user.save()
                # Keep the user logged in after password change
                update_session_auth_hash(request, request.user)
                messages.success(request, "Password changed successfully!")
                return redirect("citizen:profile")

    return render(request, "citizen/profile.html", {"user": request.user})