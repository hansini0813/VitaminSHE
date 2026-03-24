from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class SavedClinic(models.Model):
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="saved_clinics",
	)
	name = models.CharField(max_length=180)
	address_line = models.CharField(max_length=255)
	city = models.CharField(max_length=120)
	state = models.CharField(max_length=120, blank=True)
	postal_code = models.CharField(max_length=20, blank=True)
	country = models.CharField(max_length=120, default="USA")
	latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
	longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
	phone = models.CharField(max_length=30, blank=True)
	website = models.URLField(blank=True)
	external_place_id = models.CharField(max_length=120, blank=True)
	notes = models.CharField(max_length=255, blank=True)
	saved_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-saved_at"]
		constraints = [
			models.UniqueConstraint(
				fields=["user", "external_place_id"],
				condition=~models.Q(external_place_id=""),
				name="uniq_user_external_place",
			)
		]

	def __str__(self) -> str:
		return f"{self.name} ({self.city})"

	def clean(self) -> None:
		super().clean()
		if self.latitude is not None and not (-90 <= self.latitude <= 90):
			raise ValidationError({"latitude": "Latitude must be between -90 and 90."})

		if self.longitude is not None and not (-180 <= self.longitude <= 180):
			raise ValidationError({"longitude": "Longitude must be between -180 and 180."})
