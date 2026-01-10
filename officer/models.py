# officer/models.py

from django.db import models
from django.conf import settings
from citizen.models import Grievance
from django.utils import timezone


class OfficerProfile(models.Model):
    """
    Stores additional details for officer users 
    such as department, contact details, and designation.
    """

    officer = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'officer'},  # ensures only officers
        related_name='officer_profile',
        null=True,
        blank=True
    )

    profile_image = models.ImageField(
        upload_to="officer_profiles/",
        blank=True,
        null=True,
        default="default_profile.png",
        help_text="Profile picture of the officer"
    )

    department = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Department the officer belongs to"
    )

    designation = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Officer's designation or title"
    )

    contact_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text="Contact phone number of the officer"
    )

    joined_date = models.DateField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Officer Profile"
        verbose_name_plural = "Officer Profiles"

    def __str__(self):
        return f"{self.officer.get_full_name() or self.officer.username} - {self.department or 'No Department'}"

    @property
    def get_profile_image_url(self):
        """
        Returns the URL of the profile image if exists,
        else returns the default image URL.
        """
        if self.profile_image:
            return self.profile_image.url
        return "/media/default_profile.png"


class OfficerAction(models.Model):
    """
    Tracks all actions taken by officers on citizen grievances.
    Maintains history including updated status and timestamps.
    """

    officer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'officer'},
        related_name='officer_actions'
    )

    grievance = models.ForeignKey(
        Grievance,
        on_delete=models.SET_NULL,
        null=True,
        related_name='status_updates'
    )

    action_taken = models.TextField(
        help_text="Describe what action was taken regarding the grievance."
    )

    updated_status = models.CharField(
        max_length=20,
        choices=Grievance.STATUS_CHOICES,
        help_text="Select new status after handling the grievance"
    )

    review_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending Approval'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        default='approved',
        help_text="Status of review/validation by admin or higher authority"
    )

    action_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Officer Action"
        verbose_name_plural = "Officer Actions"
        ordering = ['-action_date']

    def __str__(self):
        officer_name = self.officer.get_full_name() or self.officer.username
        grievance_label = f"#{self.grievance.id}" if self.grievance else "Deleted Grievance"
        return f"{officer_name} updated {grievance_label} → {self.updated_status}"
