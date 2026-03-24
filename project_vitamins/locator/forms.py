from django import forms

from .models import SavedClinic


class SavedClinicForm(forms.ModelForm):
    class Meta:
        model = SavedClinic
        fields = [
            "name",
            "address_line",
            "city",
            "state",
            "postal_code",
            "country",
            "latitude",
            "longitude",
            "phone",
            "website",
            "external_place_id",
            "notes",
        ]
