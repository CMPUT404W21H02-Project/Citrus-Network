from django.test import TestCase
from requests.api import request
from citrus_home.models import CitrusAuthor, Friend, Follower
from django.contrib.auth.models import User
import uuid
from django.test import Client
from django.contrib.auth import authenticate


#https://docs.djangoproject.com/en/3.1/topics/testing/overview/
#on a terminal run $ python manage.py test

#TEST DONT PULL FROM YOUR DB, BUT FROM A MOCK DB
#DJANGO WILL RUN TESTS THAT START WITH THE WORD "TEST"

class CitrusAuthorTestCase(TestCase):
    def setUp(self):
        user = User.objects.create_user(username = 'coolGuy', password='coolpassword')
        self.testUser = CitrusAuthor.objects.create(type="Author",id=str(uuid.uuid4()), user=user,displayName="coolTestGuy")
        self.testUser.save()

    def test_citrus_display_name_edit(self):
        # tests that when a user sets their display name it doesnt default back to the username
        user =  CitrusAuthor.objects.get(displayName="coolTestGuy")
        self.assertEqual(user.displayName, "coolTestGuy")
        self.assertEqual(user.type, "Author")
    
    def test_citrus_author_user_one_to_one(self):
        # tests that the user child object of Citrus author parent object is truly one to one
        userChild = User.objects.get(username="coolGuy")
        authorParent =  CitrusAuthor.objects.get(displayName="coolTestGuy")
        self.assertEqual(authorParent.user, userChild)
    
    def tearDown(self):
        self.testUser.delete()

class LoginTestCase(TestCase):
        
    def setUp(self):
        user = User.objects.create_user('nervousMan', 'man@nervous.com', 'aManThatsNervous')
        self.nervousTestMan = CitrusAuthor.objects.create(type="Author",id=str(uuid.uuid4()), user=user,displayName="nervousMan")
        self.nervousTestMan.save()

    def test_correct(self):
        # tests that authentication passes with correct credentials
        user = authenticate(username='nervousMan', password='aManThatsNervous')
        self.assertTrue((user is not None) and user.is_authenticated)

    def test_incorrect_username(self):
        # tests that authentication does not pass with incorrect username
        user = authenticate(username='wrong', password='aManThatsNervous')
        self.assertFalse(user is not None and user.is_authenticated)

    def test_incorrect_password(self):
        # tests that authentication does not pass with incorrect password
        user = authenticate(username='nervousMan', password='wrong')
        self.assertFalse(user is not None and user.is_authenticated)

    def tearDown(self):
        self.nervousTestMan.delete()