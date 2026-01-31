# from django.conf import settings
# from django.db import models
# from django.utils import timezone
# from django.db.models import Index
# from django.core.validators import MinValueValidator, MaxValueValidator

# AUTH_USER = settings.AUTH_USER_MODEL


# def grievance_upload_to(instance, filename):
#     tracking = instance.tracking_id or "untracked"
#     return f"grievance_files/{tracking}/{filename}"



# class Department(models.Model):
#     name = models.CharField(max_length=150, unique=True)
#     code = models.CharField(max_length=50, unique=True, blank=True, null=True)
#     description = models.TextField(blank=True, null=True)

#     class Meta:
#         ordering = ["name"]
#         verbose_name_plural = "Departments"

#     def __str__(self):
#         return self.name



# class Category(models.Model):
#     name = models.CharField(max_length=150)
#     department = models.ForeignKey(
#         Department,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name="categories",
#     )

#     class Meta:
#         unique_together = ("name", "department")
#         ordering = ["department__name", "name"]

#     def __str__(self):
#         return f"{self.name} ({self.department})" if self.department else self.name



# class Grievance(models.Model):
#     STATUS_NEW = "new"
#     STATUS_IN_PROGRESS = "in_progress"
#     STATUS_RESOLVED = "resolved"
#     STATUS_ESCALATED = "escalated"

#     STATUS_CHOICES = [
#         (STATUS_NEW, "New"),
#         (STATUS_IN_PROGRESS, "In Progress"),
#         (STATUS_RESOLVED, "Resolved"),
#         (STATUS_ESCALATED, "Escalated"),
#     ]

#     tracking_id = models.CharField(max_length=40, unique=True, blank=True)

#     user = models.ForeignKey(
#         AUTH_USER,
#         on_delete=models.SET_NULL,
#         null=True,
#         related_name="grievances",
#     )

#     title = models.CharField(max_length=255)
#     description = models.TextField()

#     category = models.ForeignKey(
#         Category,
#         on_delete=models.SET_NULL,
#         null=True,
#         related_name="grievances",
#     )

#     # department = models.ForeignKey(
#     #     Department,
#     #     on_delete=models.SET_NULL,
#     #     null=True,
#     #     related_name="grievances",
#     # )

#     attached_file = models.FileField(
#         upload_to=grievance_upload_to,
#         blank=True,
#         null=True,
#     )

#     assigned_officer = models.ForeignKey(
#         AUTH_USER,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name="assigned_grievances",
#     )

#     status = models.CharField(
#         max_length=20,
#         choices=STATUS_CHOICES,
#         default=STATUS_NEW,
#         db_index=True,
#     )

#     created_at = models.DateTimeField(auto_now_add=True, db_index=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         ordering = ["-created_at"]
#         indexes = [
#             Index(fields=["status"]),
#             Index(fields=["created_at"]),
#         ]

#     def __str__(self):
#         return f"{self.tracking_id or 'NEW'} - {self.title}"

#     def _generate_tracking_id(self):
#         year = timezone.now().year
#         return f"KER-{year}-{self.pk:06d}"

#     def save(self, *args, **kwargs):
#         if not self.pk:
#             super().save(*args, **kwargs)
#             self.tracking_id = self._generate_tracking_id()
#             Grievance.objects.filter(pk=self.pk).update(
#                 tracking_id=self.tracking_id
#             )
#             return
#         super().save(*args, **kwargs)



# class GrievanceRemark(models.Model):
#     grievance = models.ForeignKey(
#         Grievance,
#         on_delete=models.CASCADE,
#         related_name="remarks",
#     )
#     officer = models.ForeignKey(
#         AUTH_USER,
#         on_delete=models.SET_NULL,
#         null=True,
#         related_name="remarks",
#     )
#     remark = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ["created_at"]

#     def __str__(self):
#         return f"Remark on {self.grievance.tracking_id}"



# class Feedback(models.Model):
#     grievance = models.OneToOneField(
#         Grievance,
#         on_delete=models.CASCADE,
#         related_name="feedback",
#     )
#     rating = models.PositiveSmallIntegerField(
#         validators=[MinValueValidator(1), MaxValueValidator(5)]
#     )
#     comments = models.TextField(blank=True)
#     submitted_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ["-submitted_at"]

#     def __str__(self):
#         return f"Feedback for {self.grievance.tracking_id}"



# class ChangeLog(models.Model):
#     user = models.ForeignKey(
#         AUTH_USER,
#         on_delete=models.SET_NULL,
#         null=True,
#     )
#     grievance = models.ForeignKey(
#         Grievance,
#         on_delete=models.CASCADE,
#         related_name="changes",
#     )
#     action = models.CharField(max_length=100)
#     before = models.TextField(blank=True)
#     after = models.TextField(blank=True)
#     timestamp = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ["-timestamp"]

#     def __str__(self):
#         return f"{self.action} @ {self.timestamp:%Y-%m-%d %H:%M}"

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.db.models import Index
from django.core.validators import MinValueValidator, MaxValueValidator

AUTH_USER = settings.AUTH_USER_MODEL


def grievance_upload_to(instance, filename):
    tracking = instance.tracking_id or "untracked"
    return f"grievance_files/{tracking}/{filename}"


# =====================
# DEPARTMENT
# =====================
class Department(models.Model):
    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=50, unique=True, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Departments"

    def __str__(self):
        return self.name


# =====================
# CATEGORY
# =====================
class Category(models.Model):
    name = models.CharField(max_length=150)
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,          # ✅ KEEP nullable
        blank=True,         # ✅ KEEP blank
        related_name="categories",
    )

    class Meta:
        unique_together = ("name", "department")
        ordering = ["department__name", "name"]

    def __str__(self):
        if self.department:
            return f"{self.name} ({self.department.name})"
        return self.name


# =====================
# GRIEVANCE
# =====================
class Grievance(models.Model):
    STATUS_NEW = "new"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_RESOLVED = "resolved"
    STATUS_ESCALATED = "escalated"

    STATUS_CHOICES = [
        (STATUS_NEW, "New"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_RESOLVED, "Resolved"),
        (STATUS_ESCALATED, "Escalated"),
    ]

    tracking_id = models.CharField(max_length=40, unique=True, blank=True)

    user = models.ForeignKey(
        AUTH_USER,
        on_delete=models.SET_NULL,
        null=True,
        related_name="grievances",
    )

    title = models.CharField(max_length=255)
    description = models.TextField()

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="grievances",
    )

    attached_file = models.FileField(
        upload_to=grievance_upload_to,
        blank=True,
        null=True,
    )

    assigned_officer = models.ForeignKey(
        AUTH_USER,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_grievances",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_NEW,
        db_index=True,
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            Index(fields=["status"]),
            Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.tracking_id or 'NEW'} - {self.title}"

    def _generate_tracking_id(self):
        year = timezone.now().year
        return f"KER-{year}-{self.pk:06d}"

    def save(self, *args, **kwargs):
        if not self.pk:
            super().save(*args, **kwargs)
            self.tracking_id = self._generate_tracking_id()
            Grievance.objects.filter(pk=self.pk).update(
                tracking_id=self.tracking_id
            )
            return
        super().save(*args, **kwargs)


# =====================
# REMARK
# =====================
class GrievanceRemark(models.Model):
    grievance = models.ForeignKey(
        Grievance,
        on_delete=models.CASCADE,
        related_name="remarks",
    )
    officer = models.ForeignKey(
        AUTH_USER,
        on_delete=models.SET_NULL,
        null=True,
        related_name="remarks",
    )
    remark = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Remark on {self.grievance.tracking_id}"


# =====================
# FEEDBACK
# =====================
class Feedback(models.Model):
    grievance = models.OneToOneField(
        Grievance,
        on_delete=models.CASCADE,
        related_name="feedback",
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comments = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"Feedback for {self.grievance.tracking_id}"


# =====================
# CHANGE LOG
# =====================
class ChangeLog(models.Model):
    user = models.ForeignKey(
        AUTH_USER,
        on_delete=models.SET_NULL,
        null=True,
    )
    grievance = models.ForeignKey(
        Grievance,
        on_delete=models.CASCADE,
        related_name="changes",
    )
    action = models.CharField(max_length=100)
    before = models.TextField(blank=True)
    after = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.action} @ {self.timestamp:%Y-%m-%d %H:%M}"
