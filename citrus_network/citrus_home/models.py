from django.db import models
import uuid
from django.contrib.auth.models import User
from django.core.validators import int_list_validator


class CitrusAuthor(models.Model):
    type            = models.CharField(max_length=100, default="Author")
    id              = models.CharField(max_length=50,primary_key=True)
    user            = models.OneToOneField(User, on_delete=models.CASCADE)
    host            = models.CharField(max_length=200, default="http://localhost:8000/")
    displayName     = models.CharField(max_length=300, default=f"{str(user)}")
    github          = models.CharField(max_length=300, default="", null=True)


# https://stackoverflow.com/questions/1429293/storing-an-integer-array-in-a-django-database
class Friend(models.Model):
    uuid              = models.ForeignKey(CitrusAuthor, on_delete=models.CASCADE)
    friends_uuid    = models.TextField(validators=[int_list_validator])

class Follower(models.Model):
    uuid              = models.ForeignKey(CitrusAuthor, on_delete=models.CASCADE)
    followers_uuid  = models.TextField(validators=[int_list_validator])
