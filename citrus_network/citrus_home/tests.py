from django.test import TestCase
from citrus_home.models import CitrusAuthor

# Create your tests here.
'''
 type            = models.CharField(max_length=100, default="Author")
    id              = models.CharField(max_length=50,primary_key=True)
    user            = models.OneToOneField(User, on_delete=models.CASCADE)
    host            = models.CharField(max_length=200, default="http://localhost:8000/")
    displayName     = models.CharField(max_length=300, default=f"{str(user)}")
    github          = models.CharField(max_length=300, default="", null=Tru
'''
class CitrusAuthorTestCase(TestCase):
    def setUp(self):
        CitrusAuthor.objects.create()
        
    