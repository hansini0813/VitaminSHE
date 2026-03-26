from django.urls import path

from . import views

app_name = "recommendations"

urlpatterns = [
    path("", views.index, name="index"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("resources/", views.resources, name="resources"),
    path("vitamin/<str:vitamin_id>/", views.vitamin_detail, name="vitamin_detail"),
    # API endpoints
    path("api/recommendations/", views.api_vitamin_recommendations, name="api_recommendations"),
    path("api/vitamins/", views.api_all_vitamins, name="api_all_vitamins"),
    path("api/vitamin/<str:vitamin_id>/", views.api_vitamin_detail, name="api_vitamin_detail"),
]
