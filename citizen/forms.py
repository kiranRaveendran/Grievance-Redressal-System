from django import forms
from adminpanel.models import Grievance

class CitizenGrievanceForm(forms.ModelForm):
    class Meta:
        model = Grievance
        fields = ["title", "category", "department", "description", "attached_file"]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "w-full p-2 border rounded"
            }),
            "category": forms.Select(attrs={
                "class": "w-full p-2 border rounded"
            }),
            "department": forms.Select(attrs={
                "class": "w-full p-2 border rounded"
            }),
            "description": forms.Textarea(attrs={
                "class": "w-full p-2 border rounded",
                "rows": 4
            }),
        }



