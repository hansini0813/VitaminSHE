from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class VitaminLog(models.Model):
	class VitaminType(models.TextChoices):
		VITAMIN_A = "vitamin_a", "Vitamin A"
		VITAMIN_B6 = "vitamin_b6", "Vitamin B6"
		VITAMIN_B12 = "vitamin_b12", "Vitamin B12"
		VITAMIN_C = "vitamin_c", "Vitamin C"
		VITAMIN_D = "vitamin_d", "Vitamin D"
		VITAMIN_E = "vitamin_e", "Vitamin E"
		VITAMIN_K = "vitamin_k", "Vitamin K"
		IRON = "iron", "Iron"
		CALCIUM = "calcium", "Calcium"
		MAGNESIUM = "magnesium", "Magnesium"
		ZINC = "zinc", "Zinc"
		OTHER = "other", "Other"

	class IntakeSource(models.TextChoices):
		FOOD = "food", "Food"
		SUPPLEMENT = "supplement", "Supplement"
		BOTH = "both", "Both"

	class Unit(models.TextChoices):
		MG = "mg", "mg"
		MCG = "mcg", "mcg"
		IU = "iu", "IU"

	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="vitamin_logs",
	)
	vitamin_type = models.CharField(max_length=32, choices=VitaminType.choices)
	custom_vitamin_name = models.CharField(max_length=80, blank=True)
	intake_source = models.CharField(
		max_length=20,
		choices=IntakeSource.choices,
		default=IntakeSource.FOOD,
	)
	amount = models.DecimalField(max_digits=7, decimal_places=2)
	unit = models.CharField(max_length=8, choices=Unit.choices, default=Unit.MG)
	logged_for = models.DateField(default=timezone.localdate)
	notes = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-logged_for", "-created_at"]
		constraints = [
			models.CheckConstraint(check=models.Q(amount__gt=0), name="tracking_amount_gt_zero"),
		]

	def __str__(self) -> str:
		label = self.get_vitamin_type_display()
		if self.vitamin_type == self.VitaminType.OTHER and self.custom_vitamin_name:
			label = self.custom_vitamin_name
		return f"{self.user.get_username()} - {label} ({self.logged_for})"

	def clean(self) -> None:
		super().clean()
		if self.logged_for > timezone.localdate():
			raise ValidationError({"logged_for": "Log date cannot be in the future."})

		custom_name = (self.custom_vitamin_name or "").strip()

		if self.vitamin_type == self.VitaminType.OTHER and not custom_name:
			raise ValidationError(
				{"custom_vitamin_name": "Provide a vitamin name when 'Other' is selected."}
			)

		if self.vitamin_type != self.VitaminType.OTHER and self.custom_vitamin_name:
			raise ValidationError(
				{"custom_vitamin_name": "Custom vitamin name is only allowed for 'Other'."}
			)
