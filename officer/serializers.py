from rest_framework import serializers
from django.contrib.auth.models import User
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
   

    class Meta:
        model = Grievance
        fields = "__all__"
       
    # ----------------------------
    # Get citizen name safely
    # ----------------------------
    def get_citizen_name(self, obj):
        if obj.user:
            return obj.user.username
        return None

    # ----------------------------
    # Get assigned officer name
    # ----------------------------
    def get_assigned_officer(self, obj):
        """
        Returns assigned officer name.
        Priority:
        1. Officer full name
        2. Officer username
        """
        officer = getattr(obj, 'assigned_to', None)
        if officer:
            return officer.get_full_name() or officer.username
        return None
