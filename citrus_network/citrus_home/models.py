from django.db import models
import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class CitrusUserManager(BaseUserManager):
    def create_user(self, username, password=None):
        if not username:
            raise ValueError("Citrus Users must have a username")
        check_db = CitrusUser.objects.filter(username=username).count()
        print("the number of usernames is: ", check_db )
        if check_db == 0:
            user = self.model(username=username)
            user.set_password(password)
            user.save(using=self._db)
            return user
        else:
            print("here")
            return user
    def create_superuser(self, username, password):
        # if not email:
            # raise ValueError('Citrus Admin must have an email')
        user = self.create_user( 
                                password=password, 
                                username=username)
        user.is_admin=True
        user.is_staff=True
        user.is_superuser = True
        user.save(using=self._db)
        return user

"""
what does the citrus user model need?
type: author
id: http://localhost:8000/author/auto_generated_id
host: http://localhost:8000
displayName: Alex
url: http://localhost:8000/author/auto_generated_id
github: http://github.com/laracroft 
"""

class CitrusUser(AbstractBaseUser):
    # required fields
    username = models.CharField(max_length=50, unique=True)
    date_joined     = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login      = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_active       = models.BooleanField(default=True)
    is_admin        = models.BooleanField(default=False)
    is_staff        = models.BooleanField(default=False)
    is_superuser    = models.BooleanField(default=False)

    # added fields for CitrusUser
    uid             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_type       = models.CharField(max_length=50)
    id              = models.CharField(max_length=150)
    host            = models.CharField(max_length=150, default="http://localhost:8000")
    displayName     = models.CharField(max_length=50)
    url             = models.CharField(max_length=250)
    github          = models.CharField(max_length=200, default="")

    USERNAME_FIELD = 'username'
    REQUIRED_FIELD = ['username']

    objects = CitrusUserManager()

    def __str__(self):
        return self.username
    
    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

