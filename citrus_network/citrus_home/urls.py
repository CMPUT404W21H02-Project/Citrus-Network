from django.urls import path
from . import views

urlpatterns = [
  path('', views.index, name='index'),
  path('home/', views.home_redirect),
  path('test', views.test_sign_up),
  path('service/author/<uuid:id>/',views.fetch_profile, name='profile'),
]