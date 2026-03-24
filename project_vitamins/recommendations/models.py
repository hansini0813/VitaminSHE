from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Recommendation(models.Model):
	class RecommendationType(models.TextChoices):
		DIET = "diet", "Diet"
		SUPPLEMENT = "supplement", "Supplement"
		LIFESTYLE = "lifestyle", "Lifestyle"
		MEDICAL = "medical", "Medical Follow-up"

	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="recommendations",
	)
	recommendation_type = models.CharField(max_length=20, choices=RecommendationType.choices)
	title = models.CharField(max_length=140)
	description = models.TextField()
	source_log = models.ForeignKey(
		"tracking.VitaminLog",
		on_delete=models.SET_NULL,
		blank=True,
		null=True,
		related_name="recommendations",
	)
	starts_on = models.DateField(default=timezone.localdate)
	ends_on = models.DateField(blank=True, null=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self) -> str:
		return f"{self.user.get_username()} - {self.title}"

	def clean(self) -> None:
		super().clean()
		if self.ends_on and self.ends_on < self.starts_on:
			raise ValidationError({"ends_on": "End date cannot be before start date."})
