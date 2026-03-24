from django.urls import path

from . import views

app_name = "resources"

urlpatterns = [
    path("", views.ResourceListView.as_view(), name="list"),
    path("featured/", views.FeaturedResourcesView.as_view(), name="featured"),
    path("articles/<slug:slug>/", views.ResourceDetailView.as_view(), name="detail"),
]
