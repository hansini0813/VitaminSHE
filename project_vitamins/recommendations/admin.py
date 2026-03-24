from django.contrib import admin

from .models import Recommendation


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
	list_display = ("user", "recommendation_type", "title", "starts_on", "ends_on", "is_active")
	list_filter = ("recommendation_type", "is_active", "starts_on")
	search_fields = ("user__username", "title", "description")
	autocomplete_fields = ("user", "source_log")
