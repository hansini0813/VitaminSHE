from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='VitaminSHE-home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('healthcheck/', views.healthcheck, name='VitaminSHE-healthcheck'),
    path('food/', views.food, name='VitaminSHE-food'),
    path('book/', views.book, name='VitaminSHE-book'),
    path('why/', views.why, name='VitaminSHE-why'),
]