from django.urls import path
from . import views

urlpatterns = [
  path('', views.login_redirect),
  path('home/', views.home_redirect),
  path('register/', views.register_redirect),
]