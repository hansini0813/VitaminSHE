from django import forms

from .models import Recommendation


class RecommendationForm(forms.ModelForm):
    class Meta:
        model = Recommendation
        fields = [
            "recommendation_type",
            "title",
            "description",
            "source_log",
            "starts_on",
            "ends_on",
            "is_active",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "starts_on": forms.DateInput(attrs={"type": "date"}),
            "ends_on": forms.DateInput(attrs={"type": "date"}),
        }
