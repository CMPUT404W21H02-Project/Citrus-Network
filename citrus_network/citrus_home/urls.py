from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
  path('', views.index, name='index'),
  path('home/', views.home_redirect),
  path('test', views.test_sign_up),
  url(r'^service/author/(?P<id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',views.get_profile, name='profile'),
  # path('service/author/<uuid:id>/',views.get_profile, name='profile'),
  path('service/author/<uuid:id>/edit',views.post_profile, name='edit'),

]