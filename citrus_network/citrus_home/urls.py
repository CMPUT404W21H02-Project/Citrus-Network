from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
  url(r'^service/author/(?P<id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',views.manage_profile, name='profile'),
  url(r'^service/author/(?P<id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/github$',views.get_github_events, name='github'),
  url(r'^service/author/(?P<id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/posts/(?P<pid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$', views.manage_post),
  url(r'^service/author/(?P<id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/posts/$', views.manage_post),
  url(r'^service/author/(?P<id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/posts/(?P<pid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/comment/$', views.handle_comment),
  path('', views.login_redirect, name='login_url'),
  path('home/', views.home_redirect, name='home_url'),
  path('register/', views.register_redirect, name='register_url'),
  path('logout/',views.logout_redirect,name = 'logout_url'),
  path("profile/",views.render_profile,name="profile"),
  url(r'^service/author/(?P<id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',views.manage_profile, name='profile_api'),
  url(r'^service/author/(?P<id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/github$',views.get_github_events, name='github'),
  path('stream/', views.stream_redirect, name='stream_url'),
  # https://stackoverflow.com/questions/32950432/django-urls-uuid-not-working/47948076
  path('service/author/<uuid:author_id>/followers/', views.get_followers),
  path('service/author/<uuid:author_id>/followers/<uuid:foreign_author_id>/', views.edit_followers),
  path('post/', views.make_post_redirect, name='make_post_url'),
  path('view-post/', views.post_redirect, name='view_post_url'),
  path('service/author/<uuid:author_id>/friends/', views.get_friends),
  path('service/author/<uuid:author_id>/friends/<uuid:foreign_author_id>/', views.edit_friends),
  path('service/author/<uuid:author_id>/nonfollowers/', views.get_not_followers),
]

