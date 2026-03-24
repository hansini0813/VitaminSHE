from django.urls import path

from . import views

app_name = "locator"

urlpatterns = [
    path("", views.locator_view, name="index"),
    path("saved/", views.saved_clinics_view, name="saved"),
    path("api/nearby/", views.nearby_api, name="nearby_api"),
    path("api/save/", views.save_clinic, name="save_clinic"),
    path("api/remove/", views.remove_clinic, name="remove_clinic"),
]
