from django.contrib import admin

from .models import SavedClinic


@admin.register(SavedClinic)
class SavedClinicAdmin(admin.ModelAdmin):
	list_display = ("name", "city", "country", "user", "saved_at")
	list_filter = ("country", "city", "saved_at")
	search_fields = ("name", "city", "address_line", "user__username", "external_place_id")
	autocomplete_fields = ("user",)
