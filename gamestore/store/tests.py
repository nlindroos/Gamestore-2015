from django.test import TestCase, RequestFactory
from django.test.client import Client
from django.contrib.auth.models import User, Group, AnonymousUser
from store.models import *
from store.views import *
from store.forms import *
from django.http import HttpResponse, Http404, HttpResponseRedirect



class DummyObject(object):
    """
    Instant object, just add attributes!
    """
    pass
    
def fake_view(request):
    return "success"

class TestGameModel(TestCase):
    fixtures = ['groups.json', 'users.json']
    
    def setUp(self):
        dev = User.objects.get(pk=4)
        self.g1 = Game(developer=dev, title='t1', tags='fun,game,buy,please')
        self.g2 = Game(developer=dev, title='t2', tags='fun,game,cheap')
        self.g3 = Game(developer=dev, title='t3', tags='a lOt    ,  of    , extra  space\t, like__rEalLy, a_ _lot')
        self.g4 = Game(developer=dev, title='t4', tags='fun,game,cheap')
        self.g5 = Game(developer=dev, title='t5', tags='fun')
        self.g6 = Game(developer=dev, title='t6', tags='')
        self.g8 = Game(developer=dev, title='t8', tags='1,2,3,4,9,6,7,8,9,10,9,9,11')
        
    def test_get_tags(self):
        self.assertEqual(self.g1.get_tags(), ['fun', 'game', 'buy', 'please'])
        
    def test_get_tags_unsaved_spaces(self):
        self.assertEqual(self.g3.get_tags(), ['a lOt    ', '  of    ', ' extra  space\t', ' like__rEalLy', ' a_ _lot'])
        
    def test_saved_tags(self):
        self.g3.save()
        self.g8.save()
        # leading and trailing spaces should be removed
        # upperase -> lower case
        # any amount of spaces or underscore should be replaced by one underscore
        # no duplicates (after all modifications listed above)
        # tags sorted alphabetically
        self.assertEqual(self.g3.get_tags(), ['a_lot', 'extra_space', 'like_really', 'of'])
        self.assertEqual(self.g8.get_tags(), ['1', '10', '11', '2', '3', '4', '6', '7', '8', '9'])
        
    def test_related_games(self):
        
        # don't worry: will save to test DB only (which will be deleted after test suite is done)
        self.g1.save()
        self.g2.save()
        self.g4.save()
        self.g5.save()
        self.g6.save()
        self.assertEqual(self.g2.get_related_games(), [(self.g1, 0.4), (self.g4, 1.0), (self.g5, 1/3)])
        self.assertEqual(self.g6.get_related_games(), [])

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
        self.assertEqual(response.status_code, 200, "Should render logout page")
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
                          
    def test_create_user_ok(self):
        response = self.client.post('/signup', self.new_user_data)
        self.assertEqual(response.status_code, 302, "Should redirect") #because of redirect
        self.assertEqual(response.url, 'http://testserver/signup_success', "Response url should be signup_success")
        user = User.objects.get(username="thebuilder")
        user_groups = [x.name for x in user.groups.all()]
        self.assertEqual(user_groups, ['Developers'])
        
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
        self.assertEqual(response.url, 'http://testserver/loggedin', "Response url should be loggedin")
        
    def test_already_logged_in_POST(self):
        # test to make sure that logged in users can't create new user with POST
        self.assertEqual(True, self.client.login(username="dev", password="dev"))
        response = self.client.post('/signup', self.new_user_data)
        self.assertRaises(User.DoesNotExist, User.objects.get, username='thebuilder')
        self.assertEqual(response.status_code, 302, "Should redirect") #because of redirect
        self.assertEqual(response.url, 'http://testserver/loggedin', "Response url should be loggedin")
        
class TestDevView(TestCase):
    
    def test_decorators(self):
        self.assertEqual(developer_view.login_only, True)
        self.assertEqual(developer_view.developers_only, True)
        