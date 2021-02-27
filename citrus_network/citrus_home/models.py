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
    id              = models.CharField(max_length=50, primary_key=True)
    title           = models.CharField(max_length=200)
    description     = models.CharField(max_length=300)
    content         = models.CharField(max_length=400)
    author          = models.ForeignKey(CitrusAuthor, on_delete=models.CASCADE)
    commonmark      = models.BooleanField(default=False)
    # choices for who can see a post
    PUBLIC          = 'PUB'
    SHARED_FRIENDS  = 'SHF'
    PRIVATE_AUTHOR  = 'PVA'
    PRIVATE_FRIENDS = 'PVF'
    visibility_choice = [
        (PUBLIC, 'public'),
        (SHARED_FRIENDS, 'shared with friends'),
        (PRIVATE_AUTHOR, 'shared with select author'),
        (PRIVATE_FRIENDS, 'shared with select friends'),
    ]
    visibility      = models.CharField(max_length=3, choices=visibility_choice, default=PUBLIC)
    # created         = UnixDateTimeField()







