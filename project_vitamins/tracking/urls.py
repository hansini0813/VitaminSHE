from django.urls import path

from . import views

app_name = "tracking"

urlpatterns = [
    path("", views.VitaminLogListView.as_view(), name="index"),
    path("add/", views.VitaminLogCreateView.as_view(), name="create"),
    path("<int:pk>/edit/", views.VitaminLogUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", views.VitaminLogDeleteView.as_view(), name="delete"),
]
