from rest_framework import serializers
from django.contrib.auth import get_user_model
from adminpanel.models import Grievance, GrievanceRemark, Feedback, Category, Department
from adminpanel.serializers import SimpleUserSerializer, CategorySerializer

User = get_user_model()

# Officer Grievance List (assigned to officer)
class OfficerGrievanceListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    department = serializers.StringRelatedField(read_only=True)
    user = SimpleUserSerializer(read_only=True)

    class Meta:
        model = Grievance
        fields = [
            "id", "tracking_id", "title", "description",
            "status", "category", "department",
            "user", "created_at", "updated_at"
        ]


# Grievance Detail for Officer
class OfficerGrievanceDetailSerializer(OfficerGrievanceListSerializer):
    remarks = serializers.SerializerMethodField()
    feedback = serializers.SerializerMethodField()

    class Meta(OfficerGrievanceListSerializer.Meta):
        fields = OfficerGrievanceListSerializer.Meta.fields + ["remarks", "feedback"]

    def get_remarks(self, obj):
        qs = GrievanceRemark.objects.filter(grievance=obj).order_by("created_at")
        return [{"remark": r.remark, "officer": r.officer.username, "created_at": r.created_at} for r in qs]

    def get_feedback(self, obj):
        if hasattr(obj, "feedback") and obj.feedback:
            f = obj.feedback
            return {"rating": f.rating, "comments": f.comments, "submitted_at": f.submitted_at}
        return None


# Add Remark Serializer
class OfficerAddRemarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrievanceRemark
        fields = ["remark"]

# Feedback Serializer
class OfficerFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ["rating", "comments"]
