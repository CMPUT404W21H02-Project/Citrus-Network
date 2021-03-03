# from django.test import TestCase
# from ..profile_form import ProfileForm

# class ProfileFormsTestCase(TestCase):
#     def setUp(self):
#         pass

#     def tearDown(self):
#         pass

#     def test_profile_form(self):
#         form = ProfileForm(data={
#             'username': 'test',
#             'displayName': 'test2',
#             'github': 'https://github.com/'
#         })
#         self.assertTrue(form.is_valid())
    
#     def test_profile_form_no_data(self):
#         form = ProfileForm(data={})
#         self.assertFalse(form.is_valid())
#         self.assertEquals(len(form.errors), 3)