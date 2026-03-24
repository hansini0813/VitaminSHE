from django.contrib import admin

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
	list_display = (
		"user",
		"onboarding_status",
		"is_pregnant",
		"is_breastfeeding",
		"updated_at",
	)
	list_filter = ("onboarding_status", "is_pregnant", "is_breastfeeding")
	search_fields = ("user__username", "user__email")
	autocomplete_fields = ("user",)
