from django.test import TestCase
from requests.api import request
from citrus_home.models import CitrusAuthor
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

# HTTP Based Tests
class ViewsGETTestCase(TestCase):
    def test_index_get(self):
        resp = self.client.get('/home/')
        self.assertEqual(resp.status_code, 200)
    
    def test_makepost_get(self):
        resp = self.client.get('/post/')
        self.assertEqual(resp.status_code, 200)
    
    def test_viewpost_get(self):
        resp = self.client.get('/view-post/')
        self.assertEqual(resp.status_code, 200)
    
    def test_stream_get(self):
        resp = self.client.get('/stream/')
        self.assertEqual(resp.status_code, 200)
    
class ViewsLOGINTestCase(TestCase):
    def setUp(self):
        user = User.objects.create_user('test', 'man@nervous.com', 'abc@=1234abc')
        self.nervousTestMan = CitrusAuthor.objects.create(type="Author",id=str(uuid.uuid4()), user=user,displayName="nervousMan")
        self.nervousTestMan.save()
        c = Client()
        self.client_object = c.login(username="test", password="abc@=1234abc")

    def test_login_post_authenticated(self):
        request_body = {
            'username': 'test',
            'password': 'abc@=1234abc'
        }
        response = self.client.post (
            '', request_body
        )
        self.assertEqual(response.status_code, 302)
    
    def test_logout(self):
        resp = self.client.get('/logout/')
        self.assertEqual(resp.status_code, 302)
    
    def tearDown(self):
        self.nervousTestMan.delete()

class ViewsRegisterTestCase(TestCase):
    def test_registration(self):
        request_body = {
            'username': 'test',
            'password': 'abc@=1234abc'
        }
        
        response = self.client.post (
            '/register/', request_body
        )
        self.assertEqual(response.status_code, 200)

class ViewsProfileTestCase(TestCase):
    def setUp(self):
        user = User.objects.create_user('test', 'man@nervous.com', 'abc@=1234abc')
        self.nervousTestMan = CitrusAuthor.objects.create(type="Author",id=str(uuid.uuid4()), user=user,displayName="nervousMan")
        self.nervousTestMan.save()
    
    def test_post_profile(self):
        request_body = {
            'username': 'test',
            'displayName': 'nervousMan',
            'github': 'https://github.com/test/tester'
        }
        response = self.client.post (
            '/profile/', request_body
        )
        print("TESGYHH")
        print(response)
        self.assertEqual(response.status_code, 200)

