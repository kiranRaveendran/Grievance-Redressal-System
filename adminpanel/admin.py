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

# Create the instance BEFORE using it
admin_site = CustomAdminSite(name="custom_admin")

# -----------------------------
# GRIEVANCE ADMIN
# -----------------------------
class GrievanceAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "status", "created_at")
    search_fields = ("title", "description", "user__username")
    list_filter = ("status", "created_at")
    ordering = ("-created_at",)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "department")
    search_fields = ("name",)
    list_filter = ("department",)
    ordering = ("department", "name")


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "code")
    search_fields = ("name", "code")
    ordering = ("name",)


class GrievanceRemarkAdmin(admin.ModelAdmin):
    list_display = ("id", "grievance", "officer", "created_at")
    search_fields = ("remark", "officer__username", "grievance__title")
    ordering = ("-created_at",)


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("id", "grievance", "rating", "submitted_at")
    search_fields = ("grievance__title",)
    list_filter = ("rating",)
    ordering = ("-submitted_at",)


class ChangeLogAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "grievance", "action", "timestamp")
    search_fields = ("action", "user__username", "grievance__title")
    ordering = ("-timestamp",)


# -----------------------------
# SAFE REGISTRATION FUNCTION
# -----------------------------
def register_if_exists(model_name, admin_class=None, app_label="adminpanel"):
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
register_if_exists("Department", DepartmentAdmin, app_label="adminpanel")
register_if_exists("Category", CategoryAdmin, app_label="adminpanel")
register_if_exists("Grievance", GrievanceAdmin, app_label="adminpanel")
register_if_exists("GrievanceRemark", GrievanceRemarkAdmin, app_label="adminpanel")
register_if_exists("Feedback", FeedbackAdmin, app_label="adminpanel")
register_if_exists("ChangeLog", ChangeLogAdmin, app_label="adminpanel")
