from django.apps import apps
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.admin.sites import AlreadyRegistered

# -----------------------------
# CUSTOM ADMIN SITE
# -----------------------------
class CustomAdminSite(AdminSite):
    site_header = "Admin Panel"
    site_title = "Admin Portal"
    index_title = "Welcome to Admin Panel"

admin_site = CustomAdminSite(name="custom_admin")


# -----------------------------
# GRIEVANCE ADMIN
# -----------------------------
class GrievanceAdmin(admin.ModelAdmin):
    # Only include fields that exist on your model
    list_display = ("id", "title", "status", "created_at")
    search_fields = ("title", "description", "user__username")
    list_filter = ("status", "created_at")
    ordering = ("-created_at",)


# -----------------------------
# CATEGORY ADMIN
# -----------------------------
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "department")
    search_fields = ("name",)
    list_filter = ("department",)
    ordering = ("department", "name")


# -----------------------------
# DEPARTMENT ADMIN
# -----------------------------
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "code")
    search_fields = ("name", "code")
    ordering = ("name",)


# -----------------------------
# GRIEVANCE REMARK ADMIN
# -----------------------------
class GrievanceRemarkAdmin(admin.ModelAdmin):
    list_display = ("id", "grievance", "officer", "created_at")
    search_fields = ("remark", "officer__username", "grievance__title")
    ordering = ("-created_at",)


# -----------------------------
# FEEDBACK ADMIN
# -----------------------------
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("id", "grievance", "rating", "submitted_at")
    search_fields = ("grievance__title",)
    list_filter = ("rating",)
    ordering = ("-submitted_at",)


# -----------------------------
# CHANGELOG ADMIN
# -----------------------------
class ChangeLogAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "grievance", "action", "timestamp")
    search_fields = ("action", "user__username", "grievance__title")
    ordering = ("-timestamp",)


# -----------------------------
# SAFE REGISTRATION FUNCTION
# -----------------------------
def register_if_exists(model_name, admin_class=None, app_label="citizen"):
    """
    Safely register models from another app into the custom admin site.
    Skips registration if the model doesn't exist or is already registered.
    """
    try:
        model = apps.get_model(app_label, model_name)
        if admin_class:
            admin_site.register(model, admin_class)
        else:
            admin_site.register(model)
    except LookupError:
        # Model not found in the specified app
        pass
    except AlreadyRegistered:
        # Model already registered
        pass


# -----------------------------
# REGISTER MODELS
# -----------------------------
# Adjust app_label to match your models location
register_if_exists("Department", DepartmentAdmin, app_label="citizen")
register_if_exists("Category", CategoryAdmin, app_label="citizen")
register_if_exists("Grievance", GrievanceAdmin, app_label="adminpanel")
register_if_exists("GrievanceRemark", GrievanceRemarkAdmin, app_label="adminpanel")
register_if_exists("Feedback", FeedbackAdmin, app_label="adminpanel")
register_if_exists("ChangeLog", ChangeLogAdmin, app_label="adminpanel")
