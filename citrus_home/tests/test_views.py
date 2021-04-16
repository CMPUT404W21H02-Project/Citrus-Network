from django.http.response import JsonResponse
from django.test.testcases import TestCase
from django.test import TestCase, Client
from django.urls import reverse
from citrus_home.models import CitrusAuthor, Friend, Follower, Node, Post
from django.contrib.auth.models import User
import json, uuid

class TestViews(TestCase):
    def setUp(self):
        self.mockuuid = str(uuid.uuid4())
        user = User.objects.create_user('test', 'man@nervous.com', 'abc@=1234abc', is_active=True)
        self.nervousTestMan = CitrusAuthor.objects.create(type="Author",id= self.mockuuid, user=user,displayName="nervousMan",github="https://github.com/1")
        self.nervousTestMan.save()

        self.mockuuid2 = str(uuid.uuid4())
        user2 = User.objects.create_user('test2', 'man2@nervous.com', '2abc@=1234abc', is_active=True)
        self.nervousTestMan2 = CitrusAuthor.objects.create(type="Author",id= self.mockuuid2, user=user2,displayName="nervousMan2",github="https://github.com/2")
        self.nervousTestMan2.save()

        self.mockuuid3 = str(uuid.uuid4())
        user3 = User.objects.create_user('test3', 'man3@nervous.com', '3abc@=1234abc', is_active=True)
        self.nervousTestMan3 = CitrusAuthor.objects.create(type="Author",id= self.mockuuid3, user=user3,displayName="nervousMan3")
        self.nervousTestMan3.save()

        self.new_follower_object = Follower(uuid = self.nervousTestMan,followers_uuid= self.mockuuid2)
        self.new_follower_object.save()

        self.nodeTeam3 = Node.objects.create(
            host="https://cmput-404-socialdistribution.herokuapp.com/",
            node_username = "socialdistribution_t18",
            node_password = "c404t18",
            host_username = "CitrusNetwork",
            host_password = "oranges",
            public_posts = "1",
            author_link = "1"
        )
        self.nodeTeam3.save()

        self.nodeTeam18 = Node.objects.create(
            host="https://team3-socialdistribution.herokuapp.com/",
            node_username = "team3",
            node_password = "cmput404",
            host_username = "CitrusNetwork",
            host_password = "oranges",
            public_posts = "1",
            author_link = "1"
        )
        self.nodeTeam18.save()

        self.c = Client()
        self.client_object = self.c.login(username="test", password="abc@=1234abc")

    def test_home_redirect_GET(self):
        response = self.c.get(reverse('home_url'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'citrus_home/stream.html')
    
    # def test_view_post_redirect_GET(self):
    #     test_uuid = str(uuid.uuid4())
    #     response = self.c.get(reverse('view_post_url', args=[self.mockuuid, test_uuid]))
    #     self.assertEquals(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'citrus_home/viewpost.html')
    
    '''
        Tests Profile Activities
    '''
    def test_render_profile_new_POST(self):
        request_body = {
            'username': 'test1',
            'displayName': 'nervousManTest',
            'github': 'https://github.com/'
        }
        response = self.c.post(reverse('render_profile'), request_body)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'citrus_home/profile.html')
    
    def test_render_profile(self):
        response = self.c.get(reverse('render_profile'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'citrus_home/profile.html')
    
    def test_render_author_profile_GET(self):
        response = self.c.get(reverse('render_author_profile', args=[self.mockuuid]))
        self.assertEquals(response.status_code, 302)
    
    def test_render_author_profile_GET_different_author(self):
        response = self.c.get(reverse('render_author_profile', args=[self.mockuuid2]))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'citrus_home/viewprofile.html')
    
    def test_get_authors_public_posts(self):
        response = self.c.get(reverse('get_authors_posts', args=[self.mockuuid]))
        self.assertEquals(response.status_code, 200)

    def test_manage_profile_GET(self):
        response = self.c.get(reverse('profile_api', args=[self.mockuuid]))
        self.assertEquals(response.status_code, 200)

    def test_manage_profile_POST(self):
        request_body = {
            'username': 'test1',
            'displayName': 'nervousManTest',
            'github': 'https://github.com/'
        }
        response = self.c.post(reverse('profile_api', args=[self.mockuuid]), request_body)
        self.assertEquals(response.status_code, 200)
    
    def test_manage_profile_form_error_OTHER(self):
        request_body = {
            'username': 'test1',
            'displayName': 'nervousMan',
            'github': 'https://github.com/'
        }
        response = self.c.put(reverse('profile_api', args=[self.mockuuid]), request_body)
        self.assertEquals(response.status_code, 405)
    
    '''
        Tests GitHub activity
    '''
    def test_github_events_wrong_url_GET(self):
        response = self.c.get(reverse('github', args=[self.mockuuid3]))
        self.assertEquals(response.status_code, 404)
    
    def test_github_events_GET(self):
        request_body = {
            'username': 'test1',
            'displayName': 'nervousManTest',
            'github': 'https://github.com/abramhindle'
        }
        response = self.c.post(reverse('profile_api', args=[self.mockuuid]), request_body)
        self.assertEquals(response.status_code, 200)
        response = self.c.get(reverse('github', args=[self.mockuuid]))
        self.assertEquals(response.status_code, 200)
    
    '''
        Tests Get all Authors
    '''
    def test_get_authors(self):
        response = self.c.get(reverse('authors'))
        self.assertEquals(response.status_code, 200)
    
    def test_get_authors_method_NOT_ALLOWED(self):
        response = self.c.post(reverse('authors'))
        self.assertEquals(response.status_code, 405)
    
    '''
        Tests Not Followers
    '''
    def test_get_not_followers_GET(self):
        response = self.c.get(reverse('not_followers', args=[self.mockuuid]))
        self.assertEquals(response.status_code, 200)

    def test_get_not_followers_OTHER(self):
        response = self.c.put(reverse('not_followers', args=[self.mockuuid]))
        self.assertEquals(response.status_code, 405)
    
    '''
        Tests Followers
    '''
    def test_get_followers_none_GET_exists(self):
        response = self.c.get(reverse('followers', args=[self.mockuuid]))
        self.assertEquals(response.status_code, 200)
    
    def test_get_followers_none_GET(self):
        response = self.c.get(reverse('followers', args=[self.mockuuid2]))
        self.assertEquals(response.status_code, 404)

    def test_get_followers_OTHER(self):
        response = self.c.put(reverse('followers', args=[self.mockuuid]))
        self.assertEquals(response.status_code, 405)
    
    def test_followers_page(self):
        response = self.c.put(reverse('followers_url'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'citrus_home/followers.html')
    
    '''
        Tests Edit Followers
    '''
    def test_edit_followers_none_same(self):
        response = self.c.put(reverse('edit_followers', args=[self.mockuuid, self.mockuuid]))
        self.assertEquals(response.status_code, 400)
    
    def test_edit_followers_none_DELETE_author_does_not_exist(self):
        test_uuid = str(uuid.uuid4())
        test_uuid2 = str(uuid.uuid4())
        response = self.c.delete(reverse('edit_followers', args=[test_uuid2, test_uuid]))
        self.assertEquals(response.status_code, 404)

    def test_edit_followers_none_DELETE_none_existing_user(self):
        test_uuid = str(uuid.uuid4())
        response = self.c.delete(reverse('edit_followers', args=[self.mockuuid, test_uuid]))
        self.assertEquals(response.status_code, 304)
    
    def test_edit_followers_none_DELETE(self):
        response = self.c.delete(reverse('edit_followers', args=[self.mockuuid, self.mockuuid2]))
        self.assertEquals(response.status_code, 200)
    
    def test_edit_followers_none_PUT_does_not_exist(self):
        test_uuid = str(uuid.uuid4())
        test_uuid2 = str(uuid.uuid4())
        response = self.c.put(reverse('edit_followers', args=[test_uuid2, test_uuid]))
        self.assertEquals(response.status_code, 404)

    def test_edit_followers_none_PUT(self):
        test_uuid = str(uuid.uuid4())
        response = self.c.put(reverse('edit_followers', args=[self.mockuuid, test_uuid]))
        self.assertEquals(response.status_code, 404)
    
    def test_edit_followers_PUT(self):
        response = self.c.put(reverse('edit_followers', args=[self.mockuuid, self.mockuuid3]))
        self.assertEquals(response.status_code, 200)
        response = self.c.put(reverse('edit_followers', args=[self.mockuuid3, self.mockuuid]))
        self.assertEquals(response.status_code, 200)
    
    def test_edit_followers_PUT_already_follower(self):
        response = self.c.put(reverse('edit_followers', args=[self.mockuuid, self.mockuuid2]))
        self.assertEquals(response.status_code, 304)
    
    def test_edit_followers_GET_not_a_follower(self):
        test_uuid = str(uuid.uuid4())
        response = self.c.get(reverse('edit_followers', args=[self.mockuuid, test_uuid]))
        self.assertEquals(response.status_code, 404)
    
    def test_edit_followers_GET_follower_match(self):
        response = self.c.get(reverse('edit_followers', args=[self.mockuuid, self.mockuuid2]))
        self.assertEquals(response.status_code, 200)
    
    def test_edit_followers_GET_author_has_no_followers(self):
        response = self.c.get(reverse('edit_followers', args=[self.mockuuid3, self.mockuuid2]))
        self.assertEquals(response.status_code, 404)
    
    def test_edit_followers_OTHER_method_not_allowed(self):
        test_uuid = str(uuid.uuid4())
        response = self.c.post(reverse('edit_followers', args=[self.mockuuid, test_uuid]))
        self.assertEquals(response.status_code, 405)
    
    '''
        Tests Friends
    '''
    def test_get_friends_GET(self):
        self.new_friend_object = Friend(uuid=self.nervousTestMan,friends_uuid=self.mockuuid2)
        self.new_friend_object.save()
        response = self.c.get(reverse('get_friends', args=[self.mockuuid]))
        self.assertEquals(response.status_code, 200)
        self.new_friend_object.delete()

    def test_get_friends_GET_empty(self):
        response = self.c.get(reverse('get_friends', args=[self.mockuuid]))
        self.assertEquals(response.status_code, 404)
    
    def test_get_friends_GET_incorrect_id(self):
        test_uuid = str(uuid.uuid4())
        response = self.c.get(reverse('get_friends', args=[test_uuid]))
        self.assertEquals(response.status_code, 404)

    def test_get_friends_OTHER_not_allowed(self):
        response = self.c.delete(reverse('get_friends', args=[self.mockuuid]))
        self.assertEquals(response.status_code, 405)
    
    '''
        Tests Edit Friends
        self.new_friend_object = Friend(uuid=self.nervousTestMan,friends_uuid=self.mockuuid2)
        self.new_friend_object.save()
    '''
    def test_edit_friends_GET_no_friends(self):
        test_uuid = str(uuid.uuid4())
        response = self.c.get(reverse('edit_friends', args=[self.mockuuid, test_uuid]))
        self.assertEquals(response.status_code, 404)
    
    def test_edit_friends_GET_friends(self):
        self.new_friend_object = Friend(uuid=self.nervousTestMan,friends_uuid=self.mockuuid2)
        self.new_friend_object.save()
        response = self.c.get(reverse('edit_friends', args=[self.mockuuid, self.mockuuid2]))
        self.assertEquals(response.status_code, 200)
        self.new_friend_object.delete()
    
    def test_edit_friends_GET_not_friends(self):
        response = self.c.get(reverse('edit_friends', args=[self.mockuuid, self.mockuuid3]))
        self.assertEquals(response.status_code, 404)

    def test_edit_friends_same_id(self):
        response = self.c.put(reverse('edit_friends', args=[self.mockuuid, self.mockuuid]))
        self.assertEquals(response.status_code, 400)
    
    def test_edit_friends_id_does_not_exist(self):
        test_uuid = str(uuid.uuid4())
        test_uuid2 = str(uuid.uuid4())
        response = self.c.put(reverse('edit_friends', args=[test_uuid2, test_uuid]))
        self.assertEquals(response.status_code, 404)

    def test_edit_friends_friend_does_not_exist(self):
        test_uuid = str(uuid.uuid4())
        response = self.c.put(reverse('edit_friends', args=[self.mockuuid, test_uuid]))
        self.assertEquals(response.status_code, 404)
    
    def test_edit_friends_local_citrus_author(self):
        response = self.c.put(reverse('edit_friends', args=[self.mockuuid, self.mockuuid3]))
        self.assertEquals(response.status_code, 405)
    
    def test_edit_friends_none_OTHER(self):
        test_uuid = str(uuid.uuid4())
        response = self.c.post(reverse('edit_friends', args=[self.mockuuid, test_uuid]))
        self.assertEquals(response.status_code, 405)
    
    '''
        Tests Friend Pages
    '''
    def test_render_friends_page(self):
        response = self.c.get(reverse('friends_url'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'citrus_home/friends.html')
    
    def test_render_find_friends_page(self):
        response = self.c.get(reverse('findfriends_url'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'citrus_home/findfriends.html')
    
    def tearDown(self):
        self.nervousTestMan.delete()
        self.nervousTestMan2.delete()
        self.nervousTestMan3.delete()
        self.new_follower_object.delete()

class TestPosts(TestCase):
    def setUp(self):
        self.mockuuid = str(uuid.uuid4())
        user = User.objects.create_user('test', 'man@nervous.com', 'abc@=1234abc', is_active=True)
        self.nervousTestMan = CitrusAuthor.objects.create(type="Author",id= self.mockuuid, user=user,displayName="nervousMan",github="https://github.com/1")
        self.nervousTestMan.save()

        self.mockuuid2 = str(uuid.uuid4())
        user2 = User.objects.create_user('test2', 'man2@nervous.com', '2abc@=1234abc', is_active=True)
        self.nervousTestMan2 = CitrusAuthor.objects.create(type="Author",id= self.mockuuid2, user=user2,displayName="nervousMan2",github="https://github.com/2")
        self.nervousTestMan2.save()

        self.mockuuid3 = str(uuid.uuid4())
        user3 = User.objects.create_user('test3', 'man3@nervous.com', '3abc@=1234abc', is_active=True)
        self.nervousTestMan3 = CitrusAuthor.objects.create(type="Author",id= self.mockuuid3, user=user3,displayName="nervousMan3")
        self.nervousTestMan3.save()

        self.new_follower_object = Follower(uuid = self.nervousTestMan,followers_uuid= self.mockuuid2)
        self.new_follower_object.save()

        self.new_post = str(uuid.uuid4())
        self.post1 = Post.objects.create(id=self.new_post, 
            title='title', 
            description='description', 
            content='content', 
            contentType='contentType', 
            categories='categories', 
            author=self.nervousTestMan, 
            origin='Origin', 
            source='Origin', 
            visibility='visibility', 
            unlisted=False,
            shared_with='shared_with')
        self.post1.save()

        self.nodeTeam3 = Node.objects.create(
            host="https://cmput-404-socialdistribution.herokuapp.com/",
            node_username = "socialdistribution_t18",
            node_password = "c404t18",
            host_username = "CitrusNetwork",
            host_password = "oranges",
            public_posts = "1",
            author_link = "1"
        )
        self.nodeTeam3.save()

        self.nodeTeam18 = Node.objects.create(
            host="https://team3-socialdistribution.herokuapp.com/",
            node_username = "team3",
            node_password = "cmput404",
            host_username = "CitrusNetwork",
            host_password = "oranges",
            public_posts = "1",
            author_link = "1"
        )
        self.nodeTeam18.save()

        self.c = Client()
        self.client_object = self.c.login(username="test", password="abc@=1234abc")
    '''
        Test Posts
    '''
    def test_make_post_GET(self):
        response = self.c.get(reverse('make_post_url'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'citrus_home/makepost.html')
    
    def test_make_post_NOT_SUPPORTED(self):
        response = self.c.delete(reverse('make_post_url'))
        self.assertEquals(response.status_code, 405)
    
    def test_get_author_post(self):
        response = self.c.get(reverse('get_author_post', args=[self.mockuuid, self.new_post]))
        self.assertEquals(response.status_code, 200)

    def test_edit_post_GET(self):
        response = self.c.get(reverse('view_post_url', args=[self.mockuuid, self.new_post]))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'citrus_home/viewpost.html')
    
    def test_make_edit_NOT_SUPPORTED(self):
        test_uuid = str(uuid.uuid4())
        response = self.c.delete(reverse('view_post_url', args=[self.mockuuid, test_uuid]))
        self.assertEquals(response.status_code, 405)
    
    def tearDown(self):
        self.nervousTestMan.delete()
        self.nervousTestMan2.delete()
        self.nervousTestMan3.delete()
        self.post1.delete()
        self.new_follower_object.delete()


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
    def setUp(self) -> None:
        self.username = 'test1'
        self.password = 'abc@=1234abc'
    def test_register_page_url(self):
        c = Client()
        response = c.get(reverse('register_url'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='citrus_home/register.html')
        
    def test_register_POST(self):
        c = Client()
        response = c.post(reverse('register_url'), data={
            'username': self.username,
            'password': self.password,
        })
        # self.client_object = c.login(username="test1", password="abc@=1234abc")
        self.assertEqual(response.status_code, 200)
    

    
class TestAuthenticateNode(TestCase):
    def setUp(self):
        user = User.objects.create_user('test', 'man@nervous.com', 'abc@=1234abc')
        self.nervousTestMan = CitrusAuthor.objects.create(type="Author",id=str(uuid.uuid4()), user=user,displayName="nervousMan")
        self.nervousTestMan.save()
        user2 = User.objects.create_user('test2', 'man2@nervous.com', 'abc@=1234abc1')
        self.nervousTestMan2 = CitrusAuthor.objects.create(type="Author",id=str(uuid.uuid4()), user=user2,displayName="nervousMan2")
        self.nervousTestMan2.save()
        self.nervousTestPost = Post.objects.create(id=str(uuid.uuid4()), 
                                title="Nervous Post", 
                                description="",
                                content="I'm only slightly nervous though!",
                                contentType="text/plain",
                                categories="",
                                author=self.nervousTestMan,
                                origin="https://citrusnetwork.herokuapp.com/",
                                source="https://citrusnetwork.herokuapp.com/",
                                visibility="PUBLIC",
                                shared_with="",
                                unlisted=False)
        self.host_username = "bcd"
        self.host_password = "bcd"
        self.testNode = Node.objects.create(host="https://www.testdomain.com/", node_username="bcd",node_password="bcd",host_username=self.host_username,host_password=self.host_password,public_posts="1",author_link="1")
        self.testNode.save()
    
    def test_unauthenticated_node(self):
        c = Client()
        response = c.get(reverse("authors"))
        self.assertEqual(response.status_code, 401)


    def test_authenticated_node_get_authors(self):
        c = Client()
        response = c.get(reverse("authors"), HTTP_REFERER = "https://www.testdomain.com/", HTTP_AUTHORIZATION = "Basic YmNkOmJjZA==")
        self.assertEqual(response.status_code, 200)

    def test_authenticated_node_get_posts(self):
        c = Client()
        response = c.get(reverse("public_posts"), HTTP_REFERER = "https://www.testdomain.com/", HTTP_AUTHORIZATION = "Basic YmNkOmJjZA==")
        self.assertEqual(response.status_code, 200)

    def test_authenticated_get_author_posts(self):
        c = Client()
        kwargs = {
            "id": self.nervousTestMan.id
        }
        response = c.get(reverse("manage_post", kwargs=kwargs), HTTP_REFERER = "https://www.testdomain.com/", HTTP_AUTHORIZATION = "Basic YmNkOmJjZA==")
        self.assertEqual(response.status_code, 200)

    def test_authenticated_get_author_post(self):
        c = Client()
        kwargs = {
            "id": self.nervousTestMan.id,
            "pid": self.nervousTestPost.id
        }
        response = c.get(reverse("manage_post", kwargs=kwargs), HTTP_REFERER = "https://www.testdomain.com/", HTTP_AUTHORIZATION = "Basic YmNkOmJjZA==")
        self.assertEqual(response.status_code, 200)

    def test_authenticated_get_author_post_likes(self):
        c = Client()
        kwargs = {
            "author_id": self.nervousTestMan.id,
            "post_id": self.nervousTestPost.id
        }
        response = c.get(reverse("post_likes", kwargs=kwargs), HTTP_REFERER = "https://www.testdomain.com/", HTTP_AUTHORIZATION = "Basic YmNkOmJjZA==")
        self.assertEqual(response.status_code, 200)

    def test_authenticated_post_author_post_like(self):
            c = Client()
            request_body = {
                'type': 'Like',
                'summary': 'I like your post!',
                'author' : {
                    'type': self.nervousTestMan2.type,
                    'id': self.nervousTestMan2.id,
                    'displayName': self.nervousTestMan2.displayName,
                    'github': self.nervousTestMan2.github,
                    'host': self.nervousTestMan2.host,
                    'authorID': self.nervousTestMan2.id
                },
                'object': '123',
                'postID': self.nervousTestPost.id
            }
            kwargs = {
                "author_id": self.nervousTestMan.id
            }
            response = c.post(reverse("inbox", kwargs=kwargs), json.dumps(request_body), content_type="application/json", HTTP_REFERER = "https://www.testdomain.com/", HTTP_AUTHORIZATION = "Basic YmNkOmJjZA==")
            self.assertEqual(response.status_code, 201)

    def test_authenticated_get_author_comments(self):
        c = Client()
        kwargs = {
            "id": self.nervousTestMan.id,
            "pid": self.nervousTestPost.id
        }
        response = c.get(reverse("manage_comment", kwargs=kwargs), HTTP_REFERER = "https://www.testdomain.com/", HTTP_AUTHORIZATION = "Basic YmNkOmJjZA==")
        self.assertEqual(response.status_code, 200)

    def test_authenticated_post_author_comment(self):
        c = Client()
        request_body = {
            'comment': 'Hello World!'
        }
        kwargs = {
            "id": self.nervousTestMan2.id,
            "pid": self.nervousTestPost.id
        }
        response = c.post(reverse("manage_comment", kwargs=kwargs), json.dumps(request_body), content_type="application/json", HTTP_REFERER = "https://www.testdomain.com/", HTTP_AUTHORIZATION = "Basic YmNkOmJjZA==")
        self.assertEqual(response.status_code, 200)
    
    def test_authenticated_get_author_followers(self):
        c = Client()
        kwargs = {
            "author_id": self.nervousTestMan.id
        }
        response = c.get(reverse("followers", kwargs=kwargs), HTTP_REFERER = "https://www.testdomain.com/", HTTP_AUTHORIZATION = "Basic YmNkOmJjZA==")
        self.assertEqual(response.status_code, 404)

    def test_authenticated_get_author_friends(self):
        c = Client()
        kwargs = {
            "author_id": self.nervousTestMan.id
        }
        response = c.get(reverse("get_friends", kwargs=kwargs), HTTP_REFERER = "https://www.testdomain.com/", HTTP_AUTHORIZATION = "Basic YmNkOmJjZA==")
        self.assertEqual(response.status_code, 404)


    def tearDown(self):
        self.testNode.delete()

