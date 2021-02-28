from django.db import models
import uuid
from django.contrib.auth.models import User
from django_unixdatetimefield import UnixDateTimeField


class CitrusAuthor(models.Model):
    type            = models.CharField(max_length=100, default="Author")
    id              = models.CharField(max_length=50,primary_key=True)
    user            = models.OneToOneField(User, on_delete=models.CASCADE)
    host            = models.CharField(max_length=200, default="http://localhost:8000/")
    displayName     = models.CharField(max_length=300, default=f"{str(user)}")
    github          = models.CharField(max_length=300, default="", null=True)
    profile_picture = models.ImageField(null=True, blank=True, upload_to="images/")



"""
each post has a unqiue
title, id, author, description, content, categories
common_mark = markdown
posts have different types: public, shared to friends, private to author, private to friends
"""
class Post(models.Model):
    id                  = models.CharField(max_length=50, primary_key=True)
    title               = models.CharField(max_length=200)
    description         = models.CharField(max_length=300)
    content             = models.CharField(max_length=400)
    author              = models.ForeignKey(CitrusAuthor, on_delete=models.CASCADE)
    origin              = models.CharField(max_length=300)
    commonmark          = models.BooleanField(default=False)
    # image           = models.ImageField()
    # parse this and return as list for GET request
    categories          = models.CharField(max_length=400)
    # if visibility option is not provided the default will be public
    public              = models.BooleanField(default=True, blank=True)
    private_to_author   = models.BooleanField(default=False, blank=True)
    private_to_friend   = models.BooleanField(default=False, blank=True)
    # if private to author or private to friends is true add usernames to shared_with
    shared_with         = models.CharField(max_length=600)
    created             = models.DateTimeField(auto_now_add=True)



"""
a comment will belong to an author and also be associated with one post
"""
class Comment(models.Model):
    author          = models.ForeignKey(CitrusAuthor, on_delete=models.CASCADE)
    post            = models.ForeignKey(Post, on_delete=models.CASCADE)
    comment         = models.CharField(max_length=400)
    published       = models.DateTimeField(auto_now_add=True)
    id              = models.CharField(max_length=500, primary_key=True)




