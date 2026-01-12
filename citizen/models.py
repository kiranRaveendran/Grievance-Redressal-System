from django.db import models
from accounts.models import User

class Grievance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    status = models.CharField(max_length=50, choices=[('Open','Open'),('Resolved','Resolved'),('Escalated','Escalated')])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id} - {self.title}"


