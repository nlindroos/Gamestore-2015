from django.test import TestCase
from django.contrib.auth.models import User, Group
from store.models import *
from store.views import *
from store.forms import *


class TestUsers(TestCase):
    fixtures = ['groups.json', 'users.json']
    
    def test_user_basics(self):
        player = User.objects.get(pk=3)
        self.assertEqual(player.first_name, "John", "First name should be John.")
        self.assertEqual(player.last_name, "Tester", "Last name should be Tester.")

    def test_user_groups(self):
        admin = User.objects.get(pk=1)
        u1 = User.objects.get(pk=3)
        u2 = User.objects.get(pk=4)
        u3 = User.objects.get(pk=5)
        
        self.assertEqual(u1.groups.filter(name="Players").count(), 1, "User 1 is a player")
        self.assertEqual(u1.groups.all().count(), 1, "User 1 is only a player")
        
        self.assertEqual(u2.groups.filter(name="Developers").count(), 1, "User 2 is a developer")
        self.assertEqual(u2.groups.all().count(), 1, "User 2 is only a developer")
        
        # NOTE: Admin is both player and developer, actual users are not allowed to be both
        self.assertEqual(admin.groups.filter(name="Players").count(), 1, "User 3 is a player")
        self.assertEqual(admin.groups.filter(name="Developers").count(), 1, "User 3 is a developer")
        self.assertEqual(admin.groups.all().count(), 2, "User 3 has no more groups besides player and developer")
        
        # NOTE: all actual users should be either players or developers, but this test user is neither
        self.assertEqual(u3.groups.all().count(), 0, "User 3 has no groups")
        
    def test_is_player(self):
        p = User.objects.get(pk=3)
        d = User.objects.get(pk=4)
        self.assertEqual(is_player(p), True, "p is a player")
        self.assertEqual(is_player(d), False, "d is not a player")
        self.assertEqual(is_player(None), None, "None is not a player, and not a developer")
        
    def test_is_developer(self):
        p = User.objects.get(pk=3)
        d = User.objects.get(pk=4)
        self.assertEqual(is_developer(p), False, "p is a not a developer")
        self.assertEqual(is_developer(d), True, "d is a developer")
        self.assertEqual(is_developer(None), None, "None is not a player, and not a developer")
        
class TestGameForm(TestCase):
    """
    Tests GameForm validation.
    This form is used in /dev edit.  
    """
    
    def test_valid_form(self):
        post = {'title' : 'Cool title bro', 'price' : 0, 'url' : "http://example.com", 'description' : 'hello', 'img_url' : 'http://example.com'}
        f = GameForm(post)
        self.assertEqual(f.is_valid(), True, 'This form should be valid')
    
    def test_title(self):
        post = {'price' : 0, 'url' : "http://example.com", 'description' : 'hello'}
        f = GameForm(post)
        self.assertEqual(f.is_valid(), False, 'Game must have title')
        
        post = {'title' : '', 'price' : 0, 'url' : "http://example.com", 'description' : 'hello'}
        f = GameForm(post)
        self.assertEqual(f.is_valid(), False, 'Game title cannot be empty')
        
    def test_price(self):
        post = {'title' : 'Cool title bro', 'url' : "http://example.com", 'description' : 'hello'}
        f = GameForm(post)
        self.assertEqual(f.is_valid(), False, 'Game must have price')
        
        post = {'title' : 'Cool title bro', 'price' : -1, 'url' : "http://example.com", 'description' : 'hello'}
        f = GameForm(post)
        self.assertEqual(f.is_valid(), False, 'Game price must be non-negative')
        
    def test_url(self):
        post = {'title' : 'Cool title bro', 'price' : 0, 'description' : 'hello'}
        f = GameForm(post)
        self.assertEqual(f.is_valid(), False, 'Game must have url')
        
        post = {'title' : 'Cool title bro', 'url' : 'invalid_url', 'price' : 0, 'description' : 'hello'}
        f = GameForm(post)
        self.assertEqual(f.is_valid(), False, 'Game url must be valid')
        
    def test_description(self):
        post = {'title' : 'Cool title bro', 'price' : 0, 'url' : "http://example.com"}
        f = GameForm(post)
        self.assertEqual(f.is_valid(), False, 'Game description is required')
        
        post = {'title' : 'Cool title bro', 'price' : 0, 'url' : "http://example.com", 'description' : ''}
        f = GameForm(post)
        self.assertEqual(f.is_valid(), False, 'Game description may not be empty')
        
    def test_img_url(self):
        post = {'title' : 'Cool title bro', 'price' : 0, 'url' : "http://example.com", 'description' : 'hello'}
        f = GameForm(post)
        self.assertEqual(f.is_valid(), True, 'Image url is not required')
        
        post = {'title' : 'Cool title bro', 'price' : 0, 'url' : "http://example.com", 'description' : 'hello', 'img_url' : 'invalid_url'}
        f = GameForm(post)
        self.assertEqual(f.is_valid(), False, 'Image url must be valid')
        
        post = {'title' : 'Cool title bro', 'price' : 0, 'url' : "http://example.com", 'description' : 'hello', 'img_url' : None}
        f = GameForm(post)
        self.assertEqual(f.is_valid(), True, 'Image url may be None')
        