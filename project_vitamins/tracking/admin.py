from django.contrib import admin

from .models import VitaminLog


@admin.register(VitaminLog)
class VitaminLogAdmin(admin.ModelAdmin):
	list_display = ("user", "vitamin_type", "amount", "unit", "intake_source", "logged_for")
	list_filter = ("vitamin_type", "intake_source", "unit", "logged_for")
	search_fields = ("user__username", "user__email", "custom_vitamin_name", "notes")
	autocomplete_fields = ("user",)
	date_hierarchy = "logged_for"
