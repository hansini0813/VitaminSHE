from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView
from django.core.paginator import Paginator
from django.db import models

from .models import ResourceCategory, ResourceArticle, SavedResource


class ResourceListView(ListView):
    """Display all published resource articles."""

    model = ResourceArticle
    template_name = "resources/list.html"
    context_object_name = "articles"
    paginate_by = 12

    def get_queryset(self):
        """Return only published articles, ordered by publication date."""
        queryset = ResourceArticle.objects.filter(is_published=True).select_related(
            "category"
        )
        
        # Filter by category if provided
        category_slug = self.request.GET.get("category")
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        return queryset.order_by("-published_at")

    def get_context_data(self, **kwargs):
        """Add categories and selected category to context."""
        context = super().get_context_data(**kwargs)
        context["categories"] = ResourceCategory.objects.all()
        
        selected_category = self.request.GET.get("category")
        if selected_category:
            context["selected_category"] = get_object_or_404(
                ResourceCategory, slug=selected_category
            )
        
        # Get featured articles (limit to 6)
        context["featured_articles"] = ResourceArticle.objects.filter(
            is_published=True
        ).order_by("-published_at")[:6]
        
        return context


class ResourceDetailView(DetailView):
    """Display a single resource article with save option."""

    model = ResourceArticle
    template_name = "resources/detail.html"
    context_object_name = "article"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        """Return only published articles."""
        return ResourceArticle.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        """Add related articles and whether user has saved this article."""
        context = super().get_context_data(**kwargs)
        article = self.get_object()
        
        # Add related articles from same category
        context["related_articles"] = (
            article.category.articles.filter(is_published=True)
            .exclude(id=article.id)
            .order_by("-published_at")[:3]
        )
        
        # Add save status if user is authenticated
        if self.request.user.is_authenticated:
            context["is_saved"] = SavedResource.objects.filter(
                user=self.request.user, article=article
            ).exists()
        else:
            context["is_saved"] = False
        
        return context


class FeaturedResourcesView(ListView):
    """Display featured resources with categories and search/filter."""

    model = ResourceArticle
    template_name = "resources/featured.html"
    context_object_name = "featured_articles"

    def get_queryset(self):
        """Return only published articles, ordered by publication date."""
        return ResourceArticle.objects.filter(is_published=True).order_by(
            "-published_at"
        )[:12]

    def get_context_data(self, **kwargs):
        """Add all categories and featured info."""
        context = super().get_context_data(**kwargs)
        context["categories"] = ResourceCategory.objects.annotate(
            article_count=models.Count("articles", filter=models.Q(articles__is_published=True))
        ).order_by("name")
        return context

