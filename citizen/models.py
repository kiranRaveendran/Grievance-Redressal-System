from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model





# class CitizenProfile(models.Model):
#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="citizen_profile"
#     )
#     phone = models.CharField(max_length=15, blank=True)
#     address = models.TextField(blank=True)

#     def __str__(self):
#         return str(self.user)


# -------------------------------------------------
# CITIZEN GRIEVANCE MODEL
# -------------------------------------------------
class CitizenProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="citizen_profile"
    )
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    profile_image = models.ImageField(
        upload_to="profile_images/",
        blank=True,
        null=True
    )

    def __str__(self):
        return str(self.user)


    
    

# -------------------------------------------------
# FEEDBACK MODEL
# -------------------------------------------------
class Feedback(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="feedbacks"
    )
    message = models.TextField()
    rating = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback by {self.user.username}"


# -------------------------------------------------
# OFFICER GRIEVANCE VIEW MODEL
# -------------------------------------------------



class Grievance(models.Model):
    citizen = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="citizen_grievances"
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50)

    attachments= models.ImageField(
        upload_to="grievance_files/",
        blank=True,
        null=True
    )

    date = models.DateTimeField(auto_now_add=True)

    STATUS_CHOICES = (
        ("Pending", "Pending"),
        ("In Progress", "In Progress"),
        ("Resolved", "Resolved"),
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    def __str__(self):
        return self.title


class GrievanceView(models.Model):
    grievance = models.ForeignKey(
        Grievance,
        on_delete=models.CASCADE,
        related_name="officer_views"
    )
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="submitted_grievances"
    )
    assigned_officer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assigned_grievances"
    )
    status = models.CharField(max_length=20, default="Pending")
    remarks = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.grievance.title} → {self.status}"
