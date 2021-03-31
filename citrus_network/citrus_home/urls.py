from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
  # MAIN
  path('', views.login_redirect, name='login_url'),
  path('home/', views.home_redirect, name='home_url'),
  path('register/', views.register_redirect, name='register_url'),
  path('logout/',views.logout_redirect,name = 'logout_url'),

  # POST
  url(r'^service/author/(?P<id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/posts/(?P<pid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$', views.manage_post),
  url(r'^service/author/(?P<id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/posts/(?P<pid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/comment/$', views.handle_comment),
  url(r'^service/author/(?P<id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/posts/$', views.manage_post, name="manage_post"),
  url(r'^service/author/(?P<author_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/get-posts/$', views.get_authors_public_posts, name="get_authors_posts"),
  url(r'^service/author/(?P<author_id>[0-9a-f]{8}[0-9a-f]{4}[0-9a-f]{4}[0-9a-f]{4}[0-9a-f]{12})/get-posts/$', views.get_authors_public_posts, name="get_authors_posts"),
  path('post/', views.make_post_redirect, name='make_post_url'),
  path('service/author/<uuid:author_id>/view-post/<uuid:post_id>/', views.post_redirect, name='view_post_url'),
  path('home-test/', views.handleStream, name='get_stream'),

  # AUTHORS:
  path('service/authors/', views.get_authors, name='authors'),
  url(r'^service/author/(?P<id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',views.manage_profile, name='profile'),
  url(r'^service/author/(?P<id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/github$',views.get_github_events, name='github'),
  path("profile/",views.render_profile,name="render_profile"),
  path("profile/<uuid:author_id>/",views.render_author_profile,name="render_author_profile"),


  # FOLLOWERS & FRIENDS:
  url(r'^service/author/(?P<id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',views.manage_profile, name='profile_api'),
  url(r'^author/(?P<id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',views.manage_profile, name='profile_api2'),
  path("findfriends/",views.render_find_friends_page,name='findfriends_url'),
  path("friends/",views.render_friends_page,name='friends_url'),
  path("followers/",views.render_followers_page, name='followers_url'),
  path('service/author/<uuid:author_id>/friends/', views.get_friends, name='get_friends'),
  path('service/author/<uuid:author_id>/friends/<uuid:foreign_author_id>/', views.edit_friends, name='edit_friends'),
  path('service/author/<uuid:author_id>/nonfollowers/', views.get_not_followers, name='not_followers'),
  path('service/author/<uuid:author_id>/followers/', views.get_followers, name='followers'),
  path('service/author/<uuid:author_id>/followers/<uuid:foreign_author_id>/', views.edit_followers, name='edit_followers'),

  # OTHER SERVERS
  url(r'^service/author/(?P<author_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/followers/(?P<foreign_author_id>[0-9a-f]{8}[0-9a-f]{4}[0-9a-f]{4}[0-9a-f]{4}[0-9a-f]{12})/$',  views.edit_followers, name='edit_followers'),
  url(r'^service/author/(?P<author_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/friends/(?P<foreign_author_id>[0-9a-f]{8}[0-9a-f]{4}[0-9a-f]{4}[0-9a-f]{4}[0-9a-f]{12})/$', views.edit_friends, name='edit_friends'),
  url(r'^profile/(?P<author_id>[0-9a-f]{8}[0-9a-f]{4}[0-9a-f]{4}[0-9a-f]{4}[0-9a-f]{12})/$', views.render_author_profile, name="render_profile"),

  # INBOX
  path('service/author/<uuid:author_id>/inbox/', views.handle_inbox, name='inbox'),
  path('home-test/', views.handleStream, name='get_stream'),
  path('service/author/<uuid:author_id>/inbox/', views.handle_inbox, name='inbox'),  
  path('inbox/', views.inbox_redirect, name='inbox_redirect'),
  path('public-posts/', views.browse_posts, name='public_posts'),
  # urls for likes
  path('service/author/<uuid:author_id>/post/<uuid:post_id>/likes', views.handle_likes, name='post_likes'),
  path('service/author/<uuid:author_id>/post/<uuid:post_id>/comments/<uuid:comment_id>/likes', views.handle_likes, name='comment_likes'),
  path('service/author/<uuid:author_id>/liked', views.handle_likes, name='all_likes'),
  path('posts/', views.public_posts_redirect, name='view_public_posts'),
]

