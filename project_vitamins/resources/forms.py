from django import forms

from .models import ResourceArticle, ResourceCategory, SavedResource


class ResourceCategoryForm(forms.ModelForm):
    class Meta:
        model = ResourceCategory
        fields = ["name", "slug", "description"]


class ResourceArticleForm(forms.ModelForm):
    class Meta:
        model = ResourceArticle
        fields = [
            "category",
            "title",
            "slug",
            "summary",
            "content",
            "is_published",
            "published_at",
        ]
        widgets = {
            "summary": forms.Textarea(attrs={"rows": 2}),
            "content": forms.Textarea(attrs={"rows": 8}),
            "published_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }


class SavedResourceForm(forms.ModelForm):
    class Meta:
        model = SavedResource
        fields = ["article", "notes"]
