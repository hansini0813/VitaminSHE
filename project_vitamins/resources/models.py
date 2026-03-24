from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class ResourceCategory(models.Model):
	name = models.CharField(max_length=80, unique=True)
	slug = models.SlugField(max_length=100, unique=True)
	description = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["name"]
		verbose_name_plural = "Resource categories"

	def __str__(self) -> str:
		return self.name

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.name)
		super().save(*args, **kwargs)


class ResourceArticle(models.Model):
	category = models.ForeignKey(
		ResourceCategory,
		on_delete=models.PROTECT,
		related_name="articles",
	)
	title = models.CharField(max_length=180)
	slug = models.SlugField(max_length=200, unique=True)
	summary = models.CharField(max_length=280)
	content = models.TextField()
	is_published = models.BooleanField(default=False)
	published_at = models.DateTimeField(blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-published_at", "-created_at"]

	def __str__(self) -> str:
		return self.title

	def clean(self) -> None:
		super().clean()
		if self.is_published and not self.published_at:
			raise ValidationError({"published_at": "Published articles require a published date."})

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.title)
		if self.is_published and not self.published_at:
			self.published_at = timezone.now()
		super().save(*args, **kwargs)


class SavedResource(models.Model):
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="saved_resources",
	)
	article = models.ForeignKey(
		ResourceArticle,
		on_delete=models.CASCADE,
		related_name="saved_by",
	)
	notes = models.CharField(max_length=255, blank=True)
	saved_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-saved_at"]
		constraints = [
			models.UniqueConstraint(fields=["user", "article"], name="uniq_user_saved_article"),
		]

	def __str__(self) -> str:
		return f"{self.user.get_username()} saved {self.article.title}"
