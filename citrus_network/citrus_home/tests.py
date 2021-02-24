from django.test import TestCase
from citrus_home.models import CitrusAuthor
from django.contrib.auth.models import User
import uuid
from django.test import Client


#https://docs.djangoproject.com/en/3.1/topics/testing/overview/
#on a terminal run $ python manage.py test

#TEST DONT PULL FROM YOUR DB, BUT FROM A MOCK DB
#DJANGO WILL RUN TESTS THAT START WITH THE WORD "TEST"


class CitrusAuthorTestCase(TestCase):
    def setUp(self):
        user = User.objects.create_user('coolGuy', 'coolGuy@test.com', 'coolpassword')
        CitrusAuthor.objects.create(type="Author",id=str(uuid.uuid4()), user=user,displayName="coolTestGuy")
        
    def test_citrus_author_fields(self):
        #check that displayName when provided is set to desired name instead of username
        testUser =  CitrusAuthor.objects.get(displayName="coolTestGuy")
        self.assertEqual(testUser.displayName, "coolTestGuy")


       

