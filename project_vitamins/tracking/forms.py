from django import forms

from .models import VitaminLog


class VitaminLogForm(forms.ModelForm):
    class Meta:
        model = VitaminLog
        fields = [
            "vitamin_type",
            "custom_vitamin_name",
            "intake_source",
            "amount",
            "unit",
            "logged_for",
            "notes",
        ]
        widgets = {
            "logged_for": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_custom_vitamin_name(self):
        value = self.cleaned_data.get("custom_vitamin_name", "").strip()
        return value
