from django.test import TestCase, RequestFactory
from django.test.client import Client
from django.contrib.auth.models import User, Group, AnonymousUser
from store.models import *
from store.views import *
from store.forms import *
from store.api.views import *
from django.http import HttpResponse, Http404, HttpResponseRedirect
import json
from datetime import datetime, timedelta
import django.utils.timezone as timez
from django.db import IntegrityError
from decimal import Decimal


class DummyObject(object):
    """
    Instant object, just add attributes!
    """
    pass
    
class DummyPost(object):
    def __init__(self, d):
        self.data = d
        
    def getlist(self, key):
        return self.data[key]
        
    def __get_item__(self, key):
        return self.d[key]
        
    def get(self, key, default):
        return self.data.get(key, default)
    
def fake_view(request):
    return "success"

class TestGameModel(TestCase):
    fixtures = ['groups.json', 'users.json']
    
    def setUp(self):
        dev = User.objects.get(pk=4)
        self.g1 = Game(developer=dev, title='t1', tags='fun,game,buy,please')
        self.g2 = Game(developer=dev, title='t2', tags='fun,game,cheap')
        self.g3 = Game(developer=dev, title='t3', tags='a lOt    ,  of    , extra  space\t, like__rEalLy, a_ _lot!!!')
        self.g4 = Game(developer=dev, title='t4', tags='fun,game,cheap')
        self.g5 = Game(developer=dev, title='t5', tags='fun')
        self.g6 = Game(developer=dev, title=" Search Me & be'  happy!, -100% please? ", tags='')
        self.g8 = Game(developer=dev, title='t8', tags='1,2,3,4,9,6,7,8,9,10,9,9,11')
        
    def test_get_tags(self):
        self.assertEqual(self.g1.get_tags(), ['fun', 'game', 'buy', 'please'])
        
    def test_get_tags_unsaved_spaces(self):
        self.assertEqual(self.g3.get_tags(), ['a lOt    ', '  of    ', ' extra  space\t', ' like__rEalLy', ' a_ _lot!!!'])
        
    def test_saved_tags(self):
        self.g3.save()
        self.g8.save()
        # leading and trailing spaces should be removed
        # upperase -> lower case
        # any amount of spaces or underscore should be replaced by one underscore
        # no duplicates (after all modifications listed above)
        # tags sorted alphabetically
        # special chars removed
        self.assertEqual(self.g3.get_tags(), ['a_lot', 'extra_space', 'like_really', 'of'])
        self.assertEqual(self.g8.get_tags(), ['1', '10', '11', '2', '3', '4', '6', '7', '8', '9'])
        
    def test_search_title(self):
        self.g6.save()
        # leading and trailing spaces should be removed
        # extra spaces shortened to max one space
        # upperase -> lower case
        # '&' -> 'and'
        # '%' -> 'percent'
        # other special characters removed
        self.assertEqual(self.g6.search_title, 'search me and be happy 100percent please')
        
    def test_related_games(self):
        
        # don't worry: will save to test DB only (which will be deleted after test suite is done)
        self.g1.save()
        self.g2.save()
        self.g4.save()
        self.g5.save()
        self.g6.save()
        self.assertEqual(self.g2.get_related_games(), [(self.g1, 0.4), (self.g4, 1.0), (self.g5, 1/3)])
        self.assertEqual(self.g6.get_related_games(), [])

class TestHighscoreModel(TestCase):
    """
    Tests model Highscore
    """
    fixtures = ['different_name.json', 'users.json']

    def setUp(self):
        self.player = User.objects.get(pk=3)
        self.game = Game.objects.get(pk=3)
        self.hs1 = Highscore(player=self.player, game=self.game, score=500)

    def test_highscore_unique_player_game_combination(self):
        hs2 = Highscore(player=self.player, game=self.game, score=800)
        self.hs1.save()
        # Should break the uniqueness condition
        with self.assertRaises(IntegrityError):
            hs2.save()

class TestOwnedGameModel(TestCase):
    """
    Tests model OwnedGame
    """
    fixtures = ['different_name.json', 'users.json']

    def setUp(self):
        self.owned = OwnedGame.objects.get(pk=1)
        self.player = self.owned.player
        self.game = self.owned.game

    def test_player_cannot_own_several_copies_of_one_game(self):
        self.assertEqual(self.player.first_name, "John", "First name should be John.")
        self.assertEqual(self.game.title, "Example Game", "Game should be called Example Game.")  
        owned = OwnedGame(player=self.player, game=self.game, game_state="")
        with self.assertRaises(IntegrityError):
            owned.save()

class TestPurchaseModel(TestCase):
    """
    Tests model Purchase
    """
    fixtures = ['different_name.json', 'users.json']

    def setUp(self):
        self.purchase = Purchase.objects.get(pk=1)
        self.player = self.purchase.player
        self.game = self.purchase.game

    def test_player_cannot_buy_free_game_several_times(self):
        purchase_free = Purchase(player=self.player, game=self.game, fee=0.00)
        with self.assertRaises(IntegrityError):
            purchase_free.save()


    def test_player_cannot_buy_game_with_price_several_times(self):
        purchase_cost = Purchase(player=self.player, game=self.game, fee=100)
        with self.assertRaises(IntegrityError):
            purchase_cost.save()


class TestUsers(TestCase):
    fixtures = ['groups.json', 'users.json']
    
    def setUp(self):
        self.admin = User.objects.get(pk=1)
        self.player = User.objects.get(pk=3)
        self.dev = User.objects.get(pk=4)
        self.nogroup = User.objects.get(pk=5)
    
    def test_user_basics(self):
        self.assertEqual(self.player.first_name, "John", "First name should be John.")
        self.assertEqual(self.player.last_name, "Tester", "Last name should be Tester.")

    def test_user_groups(self):        
        self.assertEqual(self.player.groups.filter(name="Players").count(), 1, "User 1 is a player")
        self.assertEqual(self.player.groups.all().count(), 1, "User 1 is only a player")
        
        self.assertEqual(self.dev.groups.filter(name="Developers").count(), 1, "User 2 is a developer")
        self.assertEqual(self.dev.groups.all().count(), 1, "User 2 is only a developer")
        
        # NOTE: Admin is both player and developer, actual users are not allowed to be both
        self.assertEqual(self.admin.groups.filter(name="Players").count(), 1, "User 3 is a player")
        self.assertEqual(self.admin.groups.filter(name="Developers").count(), 1, "User 3 is a developer")
        self.assertEqual(self.admin.groups.all().count(), 2, "User 3 has no more groups besides player and developer")
        
        # NOTE: all actual users should be either players or developers, but this test user is neither
        self.assertEqual(self.nogroup.groups.all().count(), 0, "User 4 has no groups")
        
    def test_is_player(self):
        self.assertEqual(is_player(self.player), True, "player is a player")
        self.assertEqual(is_player(self.admin), True, "admin is a player")
        self.assertEqual(is_player(self.dev), False, "developer is not a player")
        self.assertEqual(is_player(self.nogroup), False, "groupless user is not a player")
        
    def test_is_developer(self):
        self.assertEqual(is_developer(self.player), False, "player is not a developer")
        self.assertEqual(is_developer(self.admin), True, "admin is a developer")
        self.assertEqual(is_developer(self.dev), True, "developer is a developer")
        self.assertEqual(is_developer(self.nogroup), False, "groupless user is not a developer")

class TestDecorators(TestCase):    
    fixtures = ['groups.json', 'users.json']
    
    def setUp(self):
        self.player = User.objects.get(pk=3)
        self.dev = User.objects.get(pk=4)
        self.anon = AnonymousUser()
        self.client = Client()
        self.fake_request = DummyObject()
        
    def test_login_only1(self):
        def dummy(request):
            pass
        pretty_dummy = login_only(dummy)
        self.assertEqual(pretty_dummy.login_only, True, 'decorator should add info about login_only')
    
    def test_login_only2(self):
        self.assertEqual(developer_view.login_only, True, 'checking that this view has login_only (so that next asserts are valid)')
        response = self.client.get('/dev/')
        self.assertEqual(response.status_code, 302, "should redirect")
        self.assertEqual(response.url, 'http://testserver/login?next=/dev/', "Response url should be login")
        
        self.assertEqual(True, self.client.login(username="dev", password="dev"))
        response = self.client.get('/dev/')
        self.assertEqual(response.status_code, 200, "Should have permission")
    
    def test_players_only(self):
        decorated = players_only(fake_view) 
        self.assertEqual(decorated.players_only, True, 'decorator should add info about players_only')
        
        self.fake_request.user = self.player
        response = decorated(self.fake_request)
        self.assertEqual(response, 'success')
        self.fake_request.user = self.dev
        response = decorated(self.fake_request)
        self.assertEqual(response.status_code, 403)
    
    def test_developers_only(self):
        decorated = developers_only(fake_view) 
        self.assertEqual(decorated.developers_only, True, 'decorator should add info about developers_only')
        
        self.fake_request.user = self.dev
        response = decorated(self.fake_request)
        self.assertEqual(response, 'success')
        self.fake_request.user = self.player
        response = decorated(self.fake_request)
        self.assertEqual(response.status_code, 403)
        
class TestPasswordForm(TestCase):
    """
    Tests PasswordForm validation and save.
    This form is used in profile_view()
    """
    fixtures = ['groups.json', 'users.json']
    
    def test_valid_form(self):
        d = {'password1' : 'hello123', 'password2' : 'hello123', 'old_password' : 'player'}
        f = PasswordForm(User.objects.get(username='player'), d)
        v = f.is_valid()
        self.assertEqual(v, True, 'This form should be valid')
        
    def test_invalid_old_pass(self):
        d = {'password1' : 'hello123', 'password2' : 'hello123', 'old_password' : 'oops'}
        f = PasswordForm(User.objects.get(username='player'), d)
        v = f.is_valid()
        self.assertEqual(v, False, 'This form should be invalid')
        
    def test_no_old_pass_given(self):
        d = {'password1' : 'hello123', 'password2' : 'hello123', 'old_password' : ''}
        f = PasswordForm(User.objects.get(username='player'), d)
        v = f.is_valid()
        self.assertEqual(v, False, 'This form should be invalid')
        
    def test_new_password_mismatch(self):
        d = {'password1' : 'hello123', 'password2' : 'goodbye1', 'old_password' : 'player'}
        f = PasswordForm(User.objects.get(username='player'), d)
        v = f.is_valid()
        self.assertEqual(v, False, 'This form should be invalid')
        
    def test_new_password_too_short(self):
        d = {'password1' : 'hello', 'password2' : 'hello', 'old_password' : 'player'}
        f = PasswordForm(User.objects.get(username='player'), d)
        v = f.is_valid()
        self.assertEqual(v, False, 'This form should be invalid')
            
    def test_save(self):
        d = {'password1' : 'hello123', 'password2' : 'hello123', 'old_password' : 'player'}
        f = PasswordForm(User.objects.get(username='player'), d)
        v = f.is_valid()
        self.assertEqual(v, True, 'This form should be valid for the rest of the test to make sense')
        f.save()
        p = User.objects.get(username='player')
        self.assertEqual(True, p.check_password('hello123'))
        
class TestProfileForm(TestCase):
    """
    Tests ProfileForm validation and save.
    This form is used in profile_view()
    """
    fixtures = ['groups.json', 'users.json']
    
    def test_valid_form(self):
        d = {'first_name' : 'joe', 'last_name' : 'johnson', 'email' : 'mail@example.com'}
        f = ProfileForm(User.objects.get(username='player'), d)
        v = f.is_valid()
        self.assertEqual(v, True, 'This form should be valid')        

    def test_invalid_email(self):
        d = {'first_name' : 'joe', 'last_name' : 'johnson', 'email' : 'mail.example.com'}
        f = ProfileForm(User.objects.get(username='player'), d)
        v = f.is_valid()
        self.assertEqual(v, False, 'This form should be valid')
        
    def test_no_email(self):
        d = {'first_name' : 'joe', 'last_name' : 'johnson', 'email' : ''}
        f = ProfileForm(User.objects.get(username='player'), d)
        v = f.is_valid()
        self.assertEqual(v, False, 'This form should be valid')
        
    def test_save(self):
        d = {'first_name' : 'joe', 'last_name' : 'johnson', 'email' : 'joe.johnson@example.com'}
        f = ProfileForm(User.objects.get(username='player'), d)
        v = f.is_valid()
        self.assertEqual(v, True, 'This form should be valid for the rest of the test to make sense')
        f.save()
        p = User.objects.get(username='player')
        self.assertEqual('joe.johnson@example.com', p.email)
        self.assertEqual('joe', p.first_name)
        self.assertEqual('johnson', p.last_name)

        
class TestGameForm(TestCase):
    """
    Tests GameForm validation.
    This form is used in /dev edit.  
    """
    fixtures = ['groups.json', 'users.json']

    def test_valid_form(self):
        d = {'title' : 'Cool title bro', 
                          'price' : Decimal(0), 'url' : "http://example.com/", 
                          'description' : 'hello', 'img_url' : 'http://example.com/',
                          'tags[]' : ['fun']}
        post = DummyPost(d)
        f = GameForm(None, post)
        v = f.is_valid()
        self.assertEqual(v, True, 'This form should be valid')
        self.assertEqual(d, f.cleaned_data)
    
    def test_title(self):
        d = {'price' : 0, 'url' : "http://example.com", 'description' : 'hello', 'tags[]' : ['fun']}
        post = DummyPost(d)
        f = GameForm(None, post)
        self.assertEqual(f.is_valid(), False, 'Game must have title')
        
        d = {'title' : '', 'price' : 0, 'url' : "http://example.com", 'description' : 'hello', 'tags[]' : ['fun']}
        post = DummyPost(d)
        f = GameForm(None, post)
        self.assertEqual(f.is_valid(), False, 'Game title cannot be empty')
        
    def test_price(self):
        d = {'title' : 'Cool title bro', 'url' : "http://example.com", 'description' : 'hello', 'tags[]' : ['fun']}
        post = DummyPost(d)
        f = GameForm(None, post)
        self.assertEqual(f.is_valid(), False, 'Game must have price')
        
        d = {'title' : 'Cool title bro', 'price' : -1, 'url' : "http://example.com", 'description' : 'hello', 'tags[]' : ['fun']}
        post = DummyPost(d)
        f = GameForm(None, post)
        self.assertEqual(f.is_valid(), False, 'Game price must be non-negative')
        
    def test_url(self):
        d = {'title' : 'Cool title bro', 'price' : 0, 'description' : 'hello', 'tags[]' : ['fun']}
        post = DummyPost(d)
        f = GameForm(None, post)
        self.assertEqual(f.is_valid(), False, 'Game must have url')
        
        d = {'title' : 'Cool title bro', 'url' : 'invalid_url', 'price' : 0, 'description' : 'hello', 'tags[]' : ['fun']}
        post = DummyPost(d)
        f = GameForm(None, post)
        self.assertEqual(f.is_valid(), False, 'Game url must be valid')
        
    def test_description(self):
        d = {'title' : 'Cool title bro', 'price' : 0, 'url' : "http://example.com", 'tags[]' : ['fun']}
        post = DummyPost(d)
        f = GameForm(None, post)
        self.assertEqual(f.is_valid(), False, 'Game description is required')
        
        d = {'title' : 'Cool title bro', 'price' : 0, 'url' : "http://example.com", 'description' : '', 'tags[]' : ['fun']}
        post = DummyPost(d)
        f = GameForm(None, post)
        self.assertEqual(f.is_valid(), False, 'Game description may not be empty')
        
    def test_img_url(self):
        d = {'title' : 'Cool title bro', 'price' : 0, 'url' : "http://example.com", 'description' : 'hello', 'tags[]' : ['fun']}
        post = DummyPost(d)
        f = GameForm(None, post)
        self.assertEqual(f.is_valid(), True, 'Image url is not required')
        
        d = {'title' : 'Cool title bro', 'price' : 0, 'url' : "http://example.com", 'description' : 'hello', 'img_url' : 'invalid_url', 'tags[]' : ['fun']}
        post = DummyPost(d)
        f = GameForm(None, post)
        self.assertEqual(f.is_valid(), False, 'Image url must be valid')
        
        d = {'title' : 'Cool title bro', 'price' : 0, 'url' : "http://example.com", 'description' : 'hello', 'img_url' : None, 'tags[]' : ['fun']}
        post = DummyPost(d)
        f = GameForm(None, post)
        self.assertEqual(f.is_valid(), True, 'Image url may be None')
        
    def test_tags(self):
        d = {'title' : 'Cool title bro', 
                          'price' : 0, 'url' : "http://example.com", 
                          'description' : 'hello', 'img_url' : 'http://example.com',
                          'tags[]' : []}
        post = DummyPost(d)
        f = GameForm(None, post)
        self.assertEqual(f.is_valid(), False, 'Tags must be given')
        
        d = {'title' : 'Cool title bro', 
                          'price' : 0, 'url' : "http://example.com", 
                          'description' : 'hello', 'img_url' : 'http://example.com',
                          'tags[]' : None}
        post = DummyPost(d)
        f = GameForm(None, post)
        self.assertEqual(f.is_valid(), False, 'Tags must not be None')
        
        d = {'title' : 'Cool title bro', 
                          'price' : 0, 'url' : "http://example.com", 
                          'description' : 'hello', 'img_url' : 'http://example.com',
                          'tags[]' : ['fun', 'or is it']}
        post = DummyPost(d)
        f = GameForm(None, post)
        self.assertEqual(f.is_valid(), False, 'Tags must not contain spaces')
        
        d = {'title' : 'Cool title bro', 
                          'price' : 0, 'url' : "http://example.com", 
                          'description' : 'hello', 'img_url' : 'http://example.com',
                          'tags[]' : ['fun', 'right?']}
        post = DummyPost(d)
        f = GameForm(None, post)
        self.assertEqual(f.is_valid(), False, 'Tags must only contain letters, numbers and underscores')
        
        
    def test_save_new_game(self):
        dev = User.objects.get(pk=4)
        
        # making some test games
        g1 = Game(developer=dev, title='Funny Game', tags='fun,game,buy,please')
        g2 = Game(developer=dev, title='very funny game', tags='fun,game,cheap')
        g1.save()
        g2.save()
        
        l1 = Game.objects.all().count()
        d = {'title' : 'Cool title bro', 
                          'price' : Decimal(0), 'url' : "http://example.com/", 
                          'description' : 'hello', 'img_url' : 'http://example.com/',
                          'tags[]' : ['fun']}
        post = DummyPost(d)
        f = GameForm(dev, post)
        v = f.is_valid()
        self.assertEqual(v, True, 'This form should be valid for the rest of the test to make sense')
        f.save()
        l2 = Game.objects.all().count()
        self.assertEqual(l1 + 1, l2)
        self.assertTrue(Game.objects.filter(title='Cool title bro'))
        
    def test_save_existing_game_edits(self):
        dev = User.objects.get(pk=4)
        
        # making some test games
        g1 = Game(developer=dev, title='Funny Game', tags='fun,game,buy,please')
        g2 = Game(developer=dev, title='very funny game', tags='fun,game,cheap')
        g1.save()
        g2.save()
        
        l1 = Game.objects.all().count()
        d = {'title' : 'Cool title bro', 
                          'price' : Decimal(0), 'url' : "http://example.com/", 
                          'description' : 'hello', 'img_url' : 'http://example.com/',
                          'tags[]' : ['fun']}
        post = DummyPost(d)
        f = GameForm(dev, post, instance=g1)
        v = f.is_valid()
        self.assertEqual(v, True, 'This form should be valid for the rest of the test to make sense')
        f.save()
        l2 = Game.objects.all().count()
        self.assertEqual(l1, l2)
        self.assertTrue(Game.objects.filter(title='Cool title bro'))
        self.assertFalse(Game.objects.filter(title='Funny Game'))
        
        
        
        
class TestAuthView(TestCase):
    fixtures = ['groups.json', 'users.json']
        
    def setUp(self):
        # Every test needs a client.
        self.client = Client()    
        
    def test_player_ok(self):
        response = self.client.post('/auth', {'username' : 'player', 'password' : 'player'})
        self.assertEqual(response.status_code, 302, "Should redirect") #because of redirect
        self.assertEqual(response.url, 'http://testserver/mygames', "Response url should be mygames")
        self.assertEqual(self.client.session['_auth_user_id'], 3, "player (pk=3) should be logged in")
        
    def test_developer_ok(self):
        response = self.client.post('/auth', {'username' : 'dev', 'password' : 'dev'})
        self.assertEqual(response.status_code, 302, "Should redirect") #because of redirect
        self.assertEqual(response.url, 'http://testserver/dev', "Response url should be dev")
        self.assertEqual(self.client.session['_auth_user_id'], 4, "dev (pk=4) should be logged in")
        
    def test_no_group_user(self):
        # testing a user with no groups (NOTE: this kind of user cannot be reated in the service)
        response = self.client.post('/auth', {'username' : 'tester', 'password' : 'tester'})
        self.assertEqual(response.status_code, 302, "Should redirect") #because of redirect
        self.assertEqual(response.url, 'http://testserver/login', "Response url should be login")
        
        # the assert below will fail because our site allows ungrouped users to log in:
        #self.assertEqual(self.client.session.get('_auth_user_id', None), None, "Nobody should be logged in")
        
    def test_invalid_password(self):
        # testing a non-existent user
        response = self.client.post('/auth', {'username' : 'dev', 'password' : 'oops'})
        self.assertEqual(response.status_code, 302, "Should redirect") #because of redirect
        self.assertEqual(response.url, 'http://testserver/login', "Response url should be login")
        self.assertEqual(self.client.session.get('_auth_user_id', None), None, "Nobody should be logged in")
        
        
class TestLoginView(TestCase):
    fixtures = ['groups.json', 'users.json']
    
    def setUp(self):
        # Every test needs a client.
        self.client = Client()  
        
    def test_auth_user(self):
        self.assertEqual(True, self.client.login(username="dev", password="dev"))
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 302, "Should redirect")        
        
    def test_not_auth_user(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200, "Should render login page")
        
class TestLogoutView(TestCase):
    fixtures = ['groups.json', 'users.json']
    
    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        
    def test_logged_in_user(self):
        self.assertEqual(True, self.client.login(username="dev", password="dev"))
        self.assertEqual(self.client.session['_auth_user_id'], 4, "dev (pk=4) should be logged in")
        response = self.client.get('/logout')
        self.assertEqual(response.status_code, 302, "Should give 302 Found and redirect to login page")
        self.assertEqual(self.client.session.get('_auth_user_id', None), None, "Nobody should be logged in")
        
class TestSignupView(TestCase):
    fixtures = ['groups.json', 'users.json']
    
    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        self.new_user_data = {'email' : 'test@example.com', 
                              'username' : 'thebuilder', 
                              'first_name' : 'Bob', 
                              'last_name' : 'Builder',
                              'password1' : 'secret',
                              'password2' : 'secret',
                              'group' : 'Developers'
                          }
                          
    def test_GET(self):
        response = self.client.get('/signup')
        self.assertEqual(response.status_code, 200)
        
    """  NOT VALID DUE TO CHANGES

    def test_create_user_ok(self):
        response = self.client.post('/signup', self.new_user_data)
        self.assertEqual(response.status_code, 302, "Should redirect") #because of redirect
        self.assertEqual(response.url, 'http://testserver/signup_success', "Response url should be signup_success")
        user = User.objects.get(username="thebuilder")
        user_groups = [x.name for x in user.groups.all()]
        self.assertEqual(user_groups, ['Developers'])"""
        
    def test_create_user_invalid_1(self):
        # testing if second password doesn't match
        self.new_user_data['password2'] = 'not_the_same'
        response = self.client.post('/signup', self.new_user_data)
        self.assertEqual(response.status_code, 200, "Should reload page")
        self.assertRaises(User.DoesNotExist, User.objects.get, username='thebuilder')
        
    def test_create_user_invalid_2(self):
        # testing if form information is missing
        self.new_user_data.pop('email')
        response = self.client.post('/signup', self.new_user_data)
        self.assertEqual(response.status_code, 200, "Should reload page")
        self.assertRaises(User.DoesNotExist, User.objects.get, username='thebuilder')
        
    def test_create_user_existing(self):
        self.new_user_data['username'] = 'player' # this guy already exists
        response = self.client.post('/signup', self.new_user_data)
        self.assertEqual(response.status_code, 200, "Should reload page")
        self.assertEqual(User.objects.filter(username="player").count(), 1, "No new user should be created") 
        self.assertNotEqual(User.objects.get(username='player').last_name, 'Bob', 'Existing user should not be modified')
    
    def test_already_logged_in_GET(self):
        self.assertEqual(True, self.client.login(username="dev", password="dev"))
        response = self.client.get('/signup')
        self.assertEqual(response.status_code, 302, "Should redirect") #because of redirect
        self.assertEqual(response.url, 'http://testserver/mygames', "Response url should be mygames")
        
    def test_already_logged_in_POST(self):
        # test to make sure that logged in users can't create new user with POST
        self.assertEqual(True, self.client.login(username="dev", password="dev"))
        response = self.client.post('/signup', self.new_user_data)
        self.assertRaises(User.DoesNotExist, User.objects.get, username='thebuilder')
        self.assertEqual(response.status_code, 302, "Should redirect") #because of redirect
        self.assertEqual(response.url, 'http://testserver/mygames', "Response url should be mygames")
        
class TestDevView(TestCase):
    
    def test_decorators(self):
        self.assertEqual(developer_view.login_only, True)
        self.assertEqual(developer_view.developers_only, True)
                
class TestDevDeleteView(TestCase):
    fixtures = ['groups.json', 'users.json']
    
    def setUp(self):
        self.dev = User.objects.get(pk=4)
        self.admin = User.objects.get(pk=1)
        self.client = Client()
        
        # making some test games
        self.g1 = Game(developer=self.dev, title='Funny Game', tags='fun,game,buy,please')
        self.g2 = Game(developer=self.admin, title='very funny game', tags='fun,game,cheap')
        self.g1.save()
        self.g2.save()
    
    def test_decorators(self):
        self.assertEqual(dev_delete_game_view.login_only, True)
        self.assertEqual(dev_delete_game_view.developers_only, True)
        
    def test_delete_other_devs_game(self):
        pk = self.g2.pk
        self.assertEqual(True, self.client.login(username="dev", password="dev"))
        response = self.client.post('http://testserver/dev/deletegame/' + str(pk))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(1, len(Game.objects.filter(pk=pk)))
        
    def test_get_does_nothing(self):
        pk = self.g1.pk
        self.assertEqual(True, self.client.login(username="dev", password="dev"))
        response = self.client.get('http://testserver/dev/deletegame/' + str(pk))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(1, len(Game.objects.filter(pk=pk)))
        
    def test_delete_own_game(self):
        pk = self.g1.pk
        self.assertEqual(True, self.client.login(username="dev", password="dev"))
        response = self.client.post('http://testserver/dev/deletegame/' + str(pk))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(0, len(Game.objects.filter(pk=pk)))


        
class TestApi(TestCase):
    fixtures = ['groups.json', 'users.json']
    
    def setUp(self):
        dev = User.objects.get(pk=4)
        admin = User.objects.get(pk=1)
        self.client = Client()
        
        # making some test games
        self.g1 = Game(developer=dev, title='Funny Game', tags='fun,game,buy,please')
        self.g2 = Game(developer=admin, title='very funny game', tags='fun,game,cheap')
        self.g3 = Game(developer=dev, title='game X', tags='test,gam$e,tag(\d)hack')
        self.g4 = Game(developer=admin, title='untitled', tags='random_tag,another_tag')
        self.g5 = Game(developer=dev, title='music quiz - funk edition', tags='funk')
        self.g6 = Game(developer=admin, title='notags', tags='')
        self.g7 = Game(developer=dev, title='no meaningful tags', tags='hello,hi,hey')
        self.g1.save()
        self.g2.save()
        self.g3.save()
        self.g4.save()
        self.g5.save()
        self.g6.save()
        self.g7.save()
        self.games = [self.g1, self.g2, self.g3, self.g4, self.g5, self.g6, self.g7]
        
        # making some test purchases
        player = User.objects.get(pk=3)
        player2 = User.objects.get(pk=2)
        p = Purchase(game=self.g1, player=player, fee='10', payment_confirmed=True)
        p.save()
        p = Purchase(game=self.g1, player=player2, fee='5', payment_confirmed=True)
        p.save()
        p = Purchase(game=self.g3, player=player, fee='7', payment_confirmed=True)
        p.save()
        p = Purchase(game=self.g2, player=player, fee='7', payment_confirmed=True)
        p.save()
        # this seems to be the only way to set custom datetimes with auto_now_add enabled:
        # purchase 1 is now the most recent, then 2, then 3
        d = datetime(2014, 1, 1).replace(tzinfo=timez.utc)
        Purchase.objects.filter(pk=2).update(date_time=d)
        d = datetime(2013, 1, 1).replace(tzinfo=timez.utc)
        Purchase.objects.filter(pk=3).update(date_time=d)
    
    def test_wildcard_builder_empty(self):
        query = wildcard_builder('', 'developer__username')
        games = Game.objects.filter(query)
        self.assertEqual(len(games), 0)
        
    def test_wildcard_builder_match_everything(self):
        query = wildcard_builder('*', 'developer__username')
        games = Game.objects.filter(query)
        self.assertEqual(len(games), 7)
        
    def test_wildcard_builder_match_start(self):
        query = wildcard_builder('d*', 'developer__username')
        games = Game.objects.filter(query)
        self.assertEqual(list(games), [self.g1, self.g3, self.g5, self.g7])
        
    def test_wildcard_builder_partial_match(self):
        # make sure there is no match for a partial match without wildcards
        query = wildcard_builder('d', 'developer__username')
        games = Game.objects.filter(query)
        self.assertEqual(len(games), 0)
        
    def test_wildcard_builder_match_end(self):    
        query = wildcard_builder('*min', 'developer__username')
        games = Game.objects.filter(query)
        self.assertEqual(list(games), [self.g2, self.g4, self.g6])
    
    def test_wildcard_builder_match_middle(self):    
        query = wildcard_builder('*fun*', 'title')
        games = Game.objects.filter(query)
        self.assertEqual(list(games), [self.g1, self.g2, self.g5])
        
    def test_wildcard_builder_match_middle_zero_length_wildcard(self):    
        query = wildcard_builder('no*tags', 'title')
        games = Game.objects.filter(query)
        self.assertEqual(list(games), [self.g6, self.g7])
        
    def test_get_game_expand_parameters_empty(self):
        str1 = ''
        self.assertEqual(get_game_expand_parameters(str1), (0, 0))
    
    def test_get_game_expand_parameters_highscore_basic(self):        
        str1 = 'highscores(5)'
        self.assertEqual(get_game_expand_parameters(str1), (5, 0))
        
    def test_get_game_expand_parameters_similars_basic(self):
        str1 = 'similars(4)'
        self.assertEqual(get_game_expand_parameters(str1), (0, 4))
        
    def test_get_game_expand_parameters_highscore_similars_combo(self):    
        str1 = 'highscores(50),similars(7)'
        self.assertEqual(get_game_expand_parameters(str1), (50, 7))
        
    def test_get_game_expand_parameters_ignore_invalid_if_ok_later(self):
        str1 = 'oops,highscores(oops),similars(-3),highscores(8),similars(3)'
        self.assertEqual(get_game_expand_parameters(str1), (8, 3))
        
    def test_get_game_expand_parameters_first_valid_stands(self):
        str1 = 'highscores(1),highscores(2),'
        self.assertEqual(get_game_expand_parameters(str1), (1, 0))
        
    def test_get_game_expand_parameters_empty_params(self):
        str1 = 'oops,,,,,highscores(2),,similars(3),'
        self.assertEqual(get_game_expand_parameters(str1), (2, 3))
        
    def test_get_game_expand_parameters_invalid_params(self):
        str1 = 'highscores(oops),similars(3)'
        self.assertEqual(get_game_expand_parameters(str1), (0, 3))
        str1 = 'highscores(-5),similars(3.9)'
        self.assertEqual(get_game_expand_parameters(str1), (0, 0))
     
     
        
    def test_filter_by_tags_empty(self):        
        tags = []
        self.assertEqual(filter_by_tags(self.games, tags, 'any'), [])
        
    def test_filter_by_tags_match_any_one_matches_all_other_nothing(self):
        tags = ['*', 'nosuchtag']
        self.assertEqual(filter_by_tags(self.games, tags, 'any'), self.games)
        
    def test_filter_by_tags_match_all_one_matches_all_other_nothing(self):
        tags = ['*', 'nosuchtag']
        self.assertEqual(filter_by_tags(self.games, tags, 'all'), [])
        
    def test_filter_by_tags_dont_match_nonexisting(self):
        tags = ['fu']
        self.assertEqual(filter_by_tags(self.games, tags, 'any'), [])
        
    def test_filter_by_tags_any_one_arg(self):
        tags = ['fun']
        self.assertEqual(filter_by_tags(self.games, tags, 'any'), [self.g1, self.g2])
    
    def test_filter_by_tags_all_one_arg(self):
        tags = ['fun']
        self.assertEqual(filter_by_tags(self.games, tags, 'all'), [self.g1, self.g2])
        
    def test_filter_by_tags_any_basic_match_start(self):
        tags = ['fun*']
        self.assertEqual(filter_by_tags(self.games, tags, 'any'), [self.g1, self.g2, self.g5])
        
    def test_filter_by_tags_any_basic_combo(self):
        tags = ['fun','please']
        self.assertEqual(filter_by_tags(self.games, tags, 'any'), [self.g1, self.g2])
        
    def test_filter_by_tags_all_basic_combo(self):
        tags = ['fun','please']
        self.assertEqual(filter_by_tags(self.games, tags, 'all'), [self.g1])
                
    def test_filter_by_tags_match_middle(self):
        tags = ['ga*e']
        self.assertEqual(filter_by_tags(self.games, tags, 'any'), [self.g1, self.g2, self.g3])
        
        
        
    def test_api_games_view_nosuchtitle(self):
        url = 'http://testserver/game_api/v1/games/title/nosuchtitle'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
    def test_api_games_view_nosuchid(self):
        url = 'http://testserver/game_api/v1/games/id/5000'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
    def test_api_games_view_callback(self):
        url = 'http://testserver/game_api/v1/games/title/*?callback=test'
        response = self.client.get(url)
        r_str = response.content.decode('utf-8')
        self.assertEqual(response.get('Content-Type', ''), 'application/javascript')
        self.assertTrue(r_str.startswith('test(') and r_str.endswith(')'))
        
    def test_api_games_view_basic_id(self):
        url = 'http://testserver/game_api/v1/games/id/1'
        response = self.client.get(url)
        jsondata = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(jsondata['games']), 1)
        self.assertEqual(jsondata['games'][0]['title'], "Funny Game")
    
    def test_api_games_view_basic_title(self):
        url = 'http://testserver/game_api/v1/games/title/untitled'
        response = self.client.get(url)
        jsondata = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(jsondata['games']), 1)
        self.assertEqual(jsondata['games'][0]['title'], "untitled")
        
    def test_api_games_view_basic_title_spaces(self):
        url = 'http://testserver/game_api/v1/games/title/funny+game'
        response = self.client.get(url)
        jsondata = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(jsondata['games']), 1)
        self.assertEqual(jsondata['games'][0]['title'], "Funny Game")
        
    def test_api_games_view_two_devs(self):
        # also note that /dev/dev should work, i.e. find a dev named 'dev'
        url = 'http://testserver/game_api/v1/games/dev/dev/dev/admin'
        response = self.client.get(url)
        jsondata = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(jsondata['games']), 7)
        
    def test_api_games_view_basic_tagged(self):
        url = 'http://testserver/game_api/v1/games/tagged/fun/tagged/buy'
        response = self.client.get(url)
        jsondata = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(jsondata['games']), 1)
        self.assertEqual(jsondata['games'][0]['title'], "Funny Game")
        
    def test_api_games_view_expand_highscore(self):
        h = Highscore(game=self.g1, score=10, player=User.objects.get(pk=3))
        h.save()
        url = 'http://testserver/game_api/v1/games/title/*game/dev/d*/tagged/fun/tagged/buy?expand=highscores(5),similars(1)'
        response = self.client.get(url)
        jsondata = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(jsondata['games']), 1)
        self.assertEqual(jsondata['games'][0]['title'], "Funny Game")
        self.assertEqual(jsondata['games'][0]['highscores_top_5'][0]['score'], 10)
        self.assertEqual(jsondata['games'][0]['similars_top_1'], [{'location' : 'https://testserver/game_api/v1/games/2', 'title' : 'very funny game', 'developer' : 'admin', 'match' : 0.4}])
        
    def test_api_sales_view_decorated(self):
        self.assertEqual(api_dev_sales_view.login_only, True)
        self.assertEqual(api_dev_sales_view.developers_only, True)
        
    def test_api_sales_view_all_sales_basic(self):
        self.assertEqual(True, self.client.login(username="dev", password="dev"))
        # this should get all the purchases of dev's games
        url = 'http://testserver/game_api/v1/sales/'
        response = self.client.get(url)
        jsondata = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(jsondata['detailed_stats']), 2)
        self.assertEqual({len(jsondata['detailed_stats'][0]['purchases']), len(jsondata['detailed_stats'][1]['purchases'])}, {2, 1})
        self.assertEqual(jsondata['total_sales'], 22)
        self.assertEqual(jsondata['total_purchases'], 3)
        self.assertEqual({jsondata['detailed_stats'][0]['total_sales'], jsondata['detailed_stats'][1]['total_sales']}, {15, 7})
        
    def test_api_sales_view_all_sales_manual_select_by_id(self):
        self.assertEqual(True, self.client.login(username="dev", password="dev"))
        # this should get all the purchases of dev's games as well, because only games 1 and 3 have been bought
        url = 'http://testserver/game_api/v1/sales/'
        response = self.client.get(url)
        jsondata_1 = json.loads(response.content.decode('utf-8'))
        url = 'http://testserver/game_api/v1/sales/gameid/1/gameid/3'
        response = self.client.get(url)
        jsondata_2 = json.loads(response.content.decode('utf-8'))
        self.assertEqual(jsondata_2, jsondata_1)
        
    def test_api_sales_view_gameid_basic(self):
        self.assertEqual(True, self.client.login(username="dev", password="dev"))
        # this should only get the purchases of game 1
        url = 'http://testserver/game_api/v1/sales/gameid/1'
        response = self.client.get(url)
        jsondata = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(jsondata['detailed_stats']), 1)
        self.assertEqual(len(jsondata['detailed_stats'][0]['purchases']), 2)
        self.assertEqual(jsondata['total_sales'], 15)
        self.assertEqual(jsondata['total_purchases'], 2)
        self.assertEqual(jsondata['detailed_stats'][0]['total_sales'], 15)
        
    def test_api_sales_view_gameid_wrong_dev(self):
        self.assertEqual(True, self.client.login(username="dev", password="dev"))
        # and this should get nothing, as game 2 is by another developer
        url = 'http://testserver/game_api/v1/sales/gameid/2'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404, "dev should not see stats for admin's sales")
    
    def test_api_sales_view_title_nosuchtitle(self):
        self.assertEqual(True, self.client.login(username="dev", password="dev"))
        # check that we can find by title:
        url = 'http://testserver/game_api/v1/sales/title/nosuchtitle'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404, "game with this title does not exist, therefore cannot have been bought")
        
    def test_api_sales_view_title_same_as_id(self):    
        self.assertEqual(True, self.client.login(username="dev", password="dev"))
        url = 'http://testserver/game_api/v1/sales/gameid/1'
        r1 = self.client.get(url)
        url = 'http://testserver/game_api/v1/sales/title/funny+game'
        r2 = self.client.get(url)
        self.assertEqual(json.loads(r1.content.decode('utf-8')), json.loads(r2.content.decode('utf-8')))
        
    def test_api_sales_view_title_wildcard_matches_all(self):    
        self.assertEqual(True, self.client.login(username="dev", password="dev"))
        url = 'http://testserver/game_api/v1/sales/'
        r1 = self.client.get(url)
        url = 'http://testserver/game_api/v1/sales/title/*'
        r2 = self.client.get(url)
        self.assertEqual(json.loads(r1.content.decode('utf-8')), json.loads(r2.content.decode('utf-8')))
        
    def test_api_sales_view_startdate_ok(self):
        self.assertEqual(True, self.client.login(username="dev", password="dev"))
        # this should only get purchases 1 and 2 (game 1)
        url = 'http://testserver/game_api/v1/sales/startdate/2014-01-01'
        r1 = self.client.get(url)
        url = 'http://testserver/game_api/v1/sales/gameid/1/gameid/2'
        r2 = self.client.get(url)
        self.assertEqual(json.loads(r1.content.decode('utf-8')), json.loads(r2.content.decode('utf-8')))
        
    def test_api_sales_view_enddate_ok(self):
        self.assertEqual(True, self.client.login(username="dev", password="dev"))
        # this should only get purchase 3 (game 3)
        url = 'http://testserver/game_api/v1/sales/enddate/2013-05-06'
        r1 = self.client.get(url)
        url = 'http://testserver/game_api/v1/sales/gameid/3'
        r2 = self.client.get(url)
        self.assertEqual(r1.content, r2.content)
        
    def test_api_sales_view_startdate_enddate_combo_find_in_between(self):
        self.assertEqual(True, self.client.login(username="dev", password="dev"))
        # this should only get purchase 2 (game 1)
        url = 'http://testserver/game_api/v1/sales/startdate/2013-07-08/enddate/2014-05-06/'
        response = self.client.get(url)
        jsondata = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(jsondata['detailed_stats']), 1)
        self.assertEqual(len(jsondata['detailed_stats'][0]['purchases']), 1)
        self.assertEqual(jsondata['total_sales'], 5)
        self.assertEqual(jsondata['total_purchases'], 1)
        self.assertEqual(jsondata['detailed_stats'][0]['total_sales'], 5)
        
    def test_api_sales_view_startdate_enddate_combo_find_all(self):
        self.assertEqual(True, self.client.login(username="dev", password="dev"))
        # this should only get purchase 2 (game 1)
        url = 'http://testserver/game_api/v1/sales/startdate/2011-05-06/enddate/2017-07-08'
        r1 = self.client.get(url)
        url = 'http://testserver/game_api/v1/sales/'
        r2 = self.client.get(url)
        self.assertEqual(r1.content, r2.content)
    
    def test_api_sales_view_startdate_enddate_combo_too_narrow(self):    
        self.assertEqual(True, self.client.login(username="dev", password="dev"))
        # this should only get purchase 2 (game 1)
        url = 'http://testserver/game_api/v1/sales/startdate/2014-05-08/enddate/2014-05-06'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
    def test_api_sales_view_bad_startdate(self):
        self.assertEqual(True, self.client.login(username="dev", password="dev"))
        # this should fail due to bad date format:
        url = 'http://testserver/game_api/v1/sales/startdate/201'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400, 'Should be 400 (bad request)')
        
    def test_api_sales_view_bad_enddate(self):
        self.assertEqual(True, self.client.login(username="dev", password="dev"))
        # this should fail due to bad date format:
        url = 'http://testserver/game_api/v1/sales/enddate/2015.12.11'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400, 'Should be 400 (bad request)')
