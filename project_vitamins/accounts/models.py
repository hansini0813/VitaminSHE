from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class UserProfile(models.Model):
	class OnboardingStatus(models.TextChoices):
		PENDING = "pending", "Pending"
		COMPLETED = "completed", "Completed"

	user = models.OneToOneField(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="profile",
	)
	date_of_birth = models.DateField(blank=True, null=True)
	daily_water_goal_ml = models.PositiveIntegerField(default=2000)
	is_pregnant = models.BooleanField(default=False)
	is_breastfeeding = models.BooleanField(default=False)
	dietary_preferences = models.CharField(max_length=255, blank=True)
	onboarding_status = models.CharField(
		max_length=20,
		choices=OnboardingStatus.choices,
		default=OnboardingStatus.PENDING,
	)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-updated_at"]

	def __str__(self) -> str:
		return f"Profile for {self.user.get_username()}"

	def clean(self) -> None:
		super().clean()
		if self.date_of_birth and self.date_of_birth > timezone.localdate():
			raise ValidationError({"date_of_birth": "Date of birth cannot be in the future."})

		if self.daily_water_goal_ml < 500 or self.daily_water_goal_ml > 8000:
			raise ValidationError(
				{"daily_water_goal_ml": "Daily water goal must be between 500 and 8000 ml."}
			)
