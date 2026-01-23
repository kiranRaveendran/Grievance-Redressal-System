from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from citizen.models import Grievance
from officer.models import OfficerProfile


# =====================================================
# Officer Password Change Serializer
# =====================================================
class OfficerPasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value


# =====================================================
# Officer Profile Serializer
# =====================================================
class OfficerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfficerProfile
        fields = [
            'id',
            'officer',
            'profile_image',
            'department',
            'designation',
            'contact_number',
            'joined_date',
            'updated_at',
        ]
        read_only_fields = ['joined_date', 'updated_at']


# =====================================================
# Grievance Serializer (Officer View)
# =====================================================
class GrievanceSerializer(serializers.ModelSerializer):
    citizen_name = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    assigned_officer_name = serializers.SerializerMethodField()


    class Meta:
        model = Grievance
        fields = [
            'id',
            'citizen_name',
            'category_name',
            'assigned_officer_name',
            'description',
            'status',          # 🔥 DB STATUS (new / in_progress / resolved)
            'created_at',
        ]

    def get_citizen_name(self, obj):
        if obj.user:
            return obj.user.get_full_name() or obj.user.username
        return "—"

    def get_category_name(self, obj):
        if obj.category:
            return obj.category.name
        return "—"

    def get_assigned_officer_name(self, obj):
        if obj.assigned_to:
            return obj.assigned_to.get_full_name() or obj.assigned_to.username
        return "—"
