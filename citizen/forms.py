# citizen/forms.py
from django import forms
from adminpanel.models import Grievance, Feedback

# ----------------------------
# Grievance Submission Form
# ----------------------------
class CitizenGrievanceForm(forms.ModelForm):
    class Meta:
        model = Grievance
        fields = ["title", "category", "description", "attached_file"]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "w-full p-2 border rounded"
            }),
            "category": forms.Select(attrs={
                "class": "w-full p-2 border rounded"
            }),
            "description": forms.Textarea(attrs={
                "class": "w-full p-2 border rounded",
                "rows": 4
            }),
        }

# ----------------------------
# Feedback Form
# ----------------------------
class CitizenFeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ["rating", "comments"]
        widgets = {
            "rating": forms.NumberInput(attrs={
                "class": "w-full p-2 border rounded",
                "min": 1,
                "max": 5
            }),
            "comments": forms.Textarea(attrs={
                "class": "w-full p-2 border rounded",
                "rows": 4
            }),
        }


