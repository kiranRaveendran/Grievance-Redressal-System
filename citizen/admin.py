from django.contrib import admin
from adminpanel.models import Grievance, Category, Feedback, GrievanceRemark

# Admin for managing citizen grievances
class CitizenGrievanceAdmin(admin.ModelAdmin):
    list_display = ('tracking_id', 'title', 'user', 'status', 'category', 'created_at')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('title', 'tracking_id', 'user__username')
    readonly_fields = ('tracking_id',)

admin.site.register(Grievance, CitizenGrievanceAdmin)
admin.site.register(Category)
admin.site.register(Feedback)
admin.site.register(GrievanceRemark)


