from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Grievance, Feedback, CitizenProfile

User = get_user_model()


# -------------------- USER SERIALIZER --------------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # Only basic User fields
        fields = ['id', 'username', 'email']


# -------------------- CITIZEN PROFILE SERIALIZER --------------------
class CitizenProfileSerializer(serializers.ModelSerializer):
    # Include nested user info if needed
    user = UserSerializer(read_only=True)

    class Meta:
        model = CitizenProfile
        fields = ['id', 'user', 'phone', 'address', 'profile_image']


# -------------------- GRIEVANCE SERIALIZER --------------------
class GrievanceSerializer(serializers.ModelSerializer):
    citizen = UserSerializer(read_only=True)

    class Meta:
        model = Grievance
        fields = ['id', 'citizen', 'title', 'description', 'category', 'attachments', 'status', 'date']


# -------------------- FEEDBACK SERIALIZER --------------------


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['message', 'rating']
