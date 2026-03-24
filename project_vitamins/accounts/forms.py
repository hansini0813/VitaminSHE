from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import UserProfile

User = get_user_model()


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            "date_of_birth",
            "daily_water_goal_ml",
            "is_pregnant",
            "is_breastfeeding",
            "dietary_preferences",
        ]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "dietary_preferences": forms.TextInput(
                attrs={"placeholder": "Vegetarian, lactose-free, etc."}
            ),
        }


class ProfileUpdateForm(UserProfileForm):
    class Meta(UserProfileForm.Meta):
        fields = UserProfileForm.Meta.fields


class OnboardingForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=True)

    class Meta:
        model = UserProfile
        fields = [
            "date_of_birth",
            "daily_water_goal_ml",
            "is_pregnant",
            "is_breastfeeding",
            "dietary_preferences",
        ]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if self.user:
            self.fields["first_name"].initial = self.user.first_name
            self.fields["last_name"].initial = self.user.last_name
            self.fields["email"].initial = self.user.email

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        qs = User.objects.filter(email__iexact=email)
        if self.user:
            qs = qs.exclude(pk=self.user.pk)
        if qs.exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def save(self, commit=True):
        profile = super().save(commit=False)

        if self.user:
            self.user.first_name = self.cleaned_data["first_name"].strip()
            self.user.last_name = self.cleaned_data["last_name"].strip()
            self.user.email = self.cleaned_data["email"]
            if commit:
                self.user.save(update_fields=["first_name", "last_name", "email"])

            profile.user = self.user
        elif not profile.pk and not profile.user_id:
            raise ValueError("OnboardingForm requires a user for new profiles.")

        profile.onboarding_status = UserProfile.OnboardingStatus.COMPLETED

        if commit:
            profile.save()

        return profile
