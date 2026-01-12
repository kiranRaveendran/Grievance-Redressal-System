from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('citizen', 'Citizen'),
        ('officer', 'Officer'),
        ('admin', 'Admin'),
    )

    CATEGORY_CHOICES = (
        ('water', 'Water'),
        ('electricity', 'Electricity'),
        ('roads', 'Roads'),
        ('health', 'Health'),
        ('education', 'Education'),
        ('other', 'Other'),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='citizen'
    )

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        blank=True,
        null=True,
        help_text="Applicable only if role is officer"
    )

    email_verified = models.BooleanField(default=False)

    def is_citizen(self):
        return self.role == 'citizen'

    def is_officer(self):
        return self.role == 'officer'

    def is_adminpanel(self):
        return self.role == 'admin'


