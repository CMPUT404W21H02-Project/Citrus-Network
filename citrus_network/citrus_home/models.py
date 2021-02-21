from django.db import models
import uuid
from django.contrib.auth.models import User


class CitrusAuthor(models.Model):
    user_type       = models.CharField(max_length=100, default="Author")
    author_id       = models.CharField(max_length=50)
    user            = models.OneToOneField(User, on_delete=models.CASCADE)
    host            = models.CharField(max_length=200, default="http://localhost:8000/")
    display_name    = models.CharField(max_length=300, default=f"{str(user)}")
    github          = models.CharField(max_length=300, default="", null=True)
