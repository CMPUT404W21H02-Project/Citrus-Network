from django.db import models
import uuid
from django.contrib.auth.models import User
from django.core.validators import int_list_validator
from django.urls import reverse
# from django.dispatch import receiver
# from django.db.models.signals import pre_save

CONTENT_TYPE = {
    ('text/plain', 'Plain Text'),
    ('text/markdown', 'Markdown'),
    ('image/png;base64', 'Image/png'),
    ('image/jpeg;base64', 'Image/jpeg'),
    ('application/base64', 'Application'),
}

VISIBILITY_CHOICES  = {
    ("PUBLIC", "public"),
    ("PRIVATE_TO_AUTHOR", "private to author"),
    ("PRIVATE_TO_FRIENDS", "private to friends")
}

class CitrusAuthor(models.Model):
    type            = models.CharField(max_length=100, default="Author")
    id              = models.CharField(max_length=50,primary_key=True)
    user            = models.OneToOneField(User, on_delete=models.CASCADE)
    host            = models.CharField(max_length=200, default="http://localhost:8000/")
    displayName     = models.CharField(max_length=300, default=f"{str(user)}")
    github          = models.CharField(max_length=300, default="", null=True)
    url             = models.CharField(max_length=300, default="http://localhost:8000/", null=True)
    profile_picture = models.ImageField(null=True, blank=True, upload_to="images/")



"""
each post has a unqiue
title, id, author, description, content, categories
common_mark = markdown
posts have different types: public, shared to friends, private to author, private to friends
"""
class Post(models.Model):
    type                = models.CharField(max_length=50, default='post')
    # title of a post
    title               = models.CharField(max_length=200)
    # id of the post
    id                  = models.CharField(max_length=50, primary_key=True)
    # where did you get this post from?
    source              = models.CharField(max_length=300)
    # where is it actually from
    origin              = models.CharField(max_length=300)
    # a brief description of the post
    description         = models.CharField(max_length=300, null=True, blank=True)
    contentType         = models.CharField(max_length=20, default='text/plain', choices=CONTENT_TYPE)
    content             = models.TextField()
    author              = models.ForeignKey(CitrusAuthor, on_delete=models.CASCADE)
    # parse this and return as list for GET request
    categories          = models.CharField(max_length=400, null=True, blank=True)
    # total number of comments for this post
    count               = models.IntegerField(null=True, blank=True)
    # page size
    size                = models.IntegerField(null=True, blank=True)
    # the first page of comments
    comments            = models.CharField(max_length=300, null=True, blank=True)
    published           = models.DateTimeField(auto_now_add=True)
    # if visibility option is not provided the default will be public
    visibility          = models.CharField(max_length=50, choices=VISIBILITY_CHOICES, default="PUBLIC")
    # unlisted means it is public if you know the post name -- use this for images, it's so images don't show up in timelines
    unlisted            = models.BooleanField(default=False)
    # if private to author or private to friends is true add usernames to shared_with
    shared_with         = models.CharField(max_length=600, null=True, blank=True)

"""
a comment will belong to an author and also be associated with one post
"""
class Comment(models.Model):
    author          = models.ForeignKey(CitrusAuthor, on_delete=models.CASCADE)
    post            = models.ForeignKey(Post, on_delete=models.CASCADE)
    comment         = models.CharField(max_length=400)
    published       = models.DateTimeField(auto_now_add=True)
    id              = models.CharField(max_length=500, primary_key=True)



# https://stackoverflow.com/questions/1429293/storing-an-integer-array-in-a-django-database
class Friend(models.Model):
    uuid              = models.ForeignKey(CitrusAuthor, on_delete=models.CASCADE)
    friends_uuid    = models.TextField(validators=[int_list_validator])

class Follower(models.Model):
    uuid              = models.ForeignKey(CitrusAuthor, on_delete=models.CASCADE)
    followers_uuid    = models.TextField(validators=[int_list_validator])

#class Following(models.Model):
    #uuid              = models.ForeignKey(CitrusAuthor, on_delete=models.CASCADE)
    #following_uuid    = models.TextField(validators=[int_list_validator])

class Node(models.Model):
    # add a node with URL
    host = models.URLField(primary_key=True)
    # for Basic Auth TODO later
    node_username = models.CharField(max_length=100)
    node_password = models.CharField(max_length=100)
    host_username = models.CharField(max_length=100)
    host_password = models.CharField(max_length=100)
    public_posts = models.CharField(max_length=100)
    author_link = models.CharField(max_length=100)

class Inbox(models.Model):
    author = models.ForeignKey(CitrusAuthor, on_delete=models.CASCADE)
    items = models.TextField()


class Like(models.Model):
    author      = models.CharField(max_length=50, default="1")
    post_id     = models.CharField(max_length=50, blank=True, null=True)
    comment_id  = models.CharField(max_length=50, blank=True, null=True)   