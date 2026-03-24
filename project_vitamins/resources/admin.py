from django.contrib import admin

from .models import ResourceArticle, ResourceCategory, SavedResource


@admin.register(ResourceCategory)
class ResourceCategoryAdmin(admin.ModelAdmin):
	list_display = ("name", "slug", "created_at")
	search_fields = ("name", "description")
	prepopulated_fields = {"slug": ("name",)}


@admin.register(ResourceArticle)
class ResourceArticleAdmin(admin.ModelAdmin):
	list_display = ("title", "category", "is_published", "published_at", "updated_at")
	list_filter = ("category", "is_published")
	search_fields = ("title", "summary", "content")
	prepopulated_fields = {"slug": ("title",)}
	autocomplete_fields = ("category",)


@admin.register(SavedResource)
class SavedResourceAdmin(admin.ModelAdmin):
	list_display = ("user", "article", "saved_at")
	list_filter = ("saved_at",)
	search_fields = ("user__username", "article__title", "notes")
	autocomplete_fields = ("user", "article")
