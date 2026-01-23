from django.db import models
from django.conf import settings
from citizen.models import Grievance
from django.utils import timezone


class OfficerProfile(models.Model):
    officer = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="officer_profile",
        limit_choices_to={"role": "officer"}
    )

    department = models.CharField(max_length=100, blank=True, null=True)
    designation = models.CharField(max_length=100, blank=True, null=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    joined_date = models.DateField(default=timezone.now)

    def __str__(self):
        return self.officer.username


# ===============================
# Officer Action (History)
# ===============================
class OfficerAction(models.Model):
    officer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="officer_actions"
    )

    grievance = models.ForeignKey(
        Grievance,
        on_delete=models.CASCADE,
        related_name="status_history"
    )

    action_taken = models.TextField()

    updated_status = models.CharField(
        max_length=20,
        choices=Grievance.STATUS_CHOICES
    )

    action_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-action_date"]

    def __str__(self):
        return f"{self.officer.username} → {self.updated_status}"
