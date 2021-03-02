from django.test.testcases import TestCase
from django.test import TestCase, Client
from django.urls import reverse
from citrus_home.models import CitrusAuthor, Friend, Follower
from django.contrib.auth.models import User
import json, uuid

class TestViews(TestCase):
    def setUp(self):
        self.mockuuid = str(uuid.uuid4())
        user = User.objects.create_user('test', 'man@nervous.com', 'abc@=1234abc')
        self.nervousTestMan = CitrusAuthor.objects.create(type="Author",id= self.mockuuid, user=user,displayName="nervousMan")
        self.nervousTestMan.save()
        self.c = Client()
        self.client_object = self.c.login(username="test", password="abc@=1234abc")

    def test_home_redirect_GET(self):
        response = self.c.get(reverse('home_url'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'citrus_home/index.html')
    
    def test_make_post_redirect_GET(self):
        response = self.c.get(reverse('make_post_url'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'citrus_home/makepost.html')
    
    def test_view_post_redirect_GET(self):
        response = self.c.get(reverse('view_post_url'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'citrus_home/viewpost.html')
    
    def test_stream_GET(self):
        response = self.c.get(reverse('stream_url'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'citrus_home/stream.html')
    
    def test_render_profile_new_POST(self):
        request_body = {
            'username': 'test1',
            'displayName': 'nervousManTest',
            'github': 'https://github.com/'
        }
        response = self.c.post(reverse('profile'), request_body)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'citrus_home/profile.html')
    
    def test_render_profile(self):
        response = self.c.get(reverse('profile'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'citrus_home/profile.html')
    
    # def test_manage_profile(self):
    #     response = self.c.get(reverse('profile_api'), args=[self.mockuuid])
    #     print("TESTTYSH")
    #     print(response)
    #     self.assertEquals(response.status_code, 200)
    
    def tearDown(self):
        self.nervousTestMan.delete()

class TestViewsAuthentication(TestCase):
    def setUp(self):
        user = User.objects.create_user('test', 'man@nervous.com', 'abc@=1234abc')
        self.nervousTestMan = CitrusAuthor.objects.create(type="Author",id=str(uuid.uuid4()), user=user,displayName="nervousMan")
        self.nervousTestMan.save()
        self.c = Client()
    
    def test_login_POST(self):
        self.client_object = self.c.login(username="test", password="abc@=1234abc")
        request_body = {
            'username': 'test',
            'password': 'abc@=1234abc'
        }
        response = self.c.post(reverse('login_url'), request_body)
        self.assertRedirects(response, expected_url=reverse('home_url'), status_code=302, target_status_code=200)
    
    def test_login_not_authenticated(self):
        self.client_object = self.c.login(username="test", password="abc@=1234abc")
        request_body = {
            'username': '',
            'password': ''
        }
        response = self.c.post(reverse('login_url'), request_body)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'citrus_home/login.html')
    
    def test_login_user_still_logged_in(self):
        self.client_object = self.c.login(username="test", password="abc@=1234abc")
        response = self.c.get(reverse('login_url'))
        self.assertRedirects(response, expected_url=reverse('home_url'), status_code=302, target_status_code=200)
    
    def test_login_user_not_authenticated(self):
        response = self.c.get(reverse('login_url'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'citrus_home/login.html')
    
    def test_logout(self):
        response = self.c.get(reverse('logout_url'))
        self.assertRedirects(response, expected_url=reverse('login_url'), status_code=302, target_status_code=200)
        
    def tearDown(self):
        self.nervousTestMan.delete()

class TestViewsRegistration(TestCase):
    #TODO FIX
    def test_register_POST(self):
        request_body = {
            'username': 'test1',
            'password': 'abc@=1234abc'
        }
        c = Client()
        response = c.post(reverse('register_url'), request_body)
        self.client_object = c.login(username="test1", password="abc@=1234abc")
        self.assertEqual(response.status_code, 200)
    
    #TODO FIX
    # def test_uuid(self):
    #     mock_uuid = str(uuid.uuid4())
    #     user = User.objects.create_user('test1', 'man@nervous.com', 'abc@=1234abc')
    #     self.nervousTestMan = CitrusAuthor.objects.create(type="Author",id=mock_uuid, user=user,displayName="nervousMan")
    #     self.nervousTestMan.save()
    #     self.assertEqual(mock_uuid, user.get_uuid())
    #     self.nervousTestMan.delete()
        