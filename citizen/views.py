from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from adminpanel.models import Grievance, Feedback
from .forms import CitizenGrievanceForm


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

    # Compute metrics for dashboard-style cards
    total = grievances.count()
    open_count = grievances.filter(status__in=[Grievance.STATUS_NEW, Grievance.STATUS_IN_PROGRESS]).count()
    resolved_count = grievances.filter(status=Grievance.STATUS_RESOLVED).count()
    escalated_count = grievances.filter(status=Grievance.STATUS_ESCALATED).count()

    return render(request, "citizen/grievances_list.html", {
        "grievances": grievances,
        "total": total,
        "open_count": open_count,
        "resolved_count": resolved_count,
        "escalated_count": escalated_count,
    })


# -----------------------------
# GRIEVANCE DETAIL
# -----------------------------
@login_required
def grievance_detail(request, pk):
    grievance = get_object_or_404(
        Grievance,
        pk=pk,
        user=request.user
    )

    return render(request, "citizen/grievance_detail.html", {
        "grievance": grievance
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
        form = CitizenGrievanceForm()

    return render(request, "citizen/submit_grievance.html", {
        "form": form
    })
def notifications(request):
    # Example: show empty notifications page
    return render(request, 'citizen/notifications.html')

def profile(request):
    return render(request, 'citizen/profile.html')


