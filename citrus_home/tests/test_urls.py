from django.test import TestCase
from django.urls import reverse, resolve
from citrus_home import views

class TestUrls(TestCase):
    def test_login_url_resolved(self):
        url = reverse('login_url')
        self.assertEquals(resolve(url).func, views.login_redirect)

    def test_home_url_redirect(self):
        url = reverse('home_url')
        self.assertEquals(resolve(url).func, views.home_redirect)
    
    def test_register_url_redirect(self):
        url = reverse('register_url')
        self.assertEquals(resolve(url).func, views.register_redirect)
    
    def test_logout_redirect(self):
        url = reverse('logout_url')
        self.assertEquals(resolve(url).func, views.logout_redirect)
    
    # def test_render_profile(self):
    #     url = reverse('profile')
    #     self.assertEquals(resolve(url).func, views.render_profile)