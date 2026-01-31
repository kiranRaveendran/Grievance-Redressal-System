# citizen/models.py
from django.db import models
from accounts.models import User

class Grievance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    status = models.CharField(max_length=50, choices=[('Open','Open'),('Resolved','Resolved'),('Escalated','Escalated')])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id} - {self.title}"

class Feedback(models.Model):
    grievance = models.OneToOneField(Grievance, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=[(1,'1'),(2,'2'),(3,'3'),(4,'4'),(5,'5')])
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for Grievance {self.grievance.id}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username

