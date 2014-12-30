from django.test import TestCase
from store.models import *


class PlayerTestCase(TestCase):
    fixtures = ['different_name.json']

    def test_player_name(self):
        player = Player.objects.get(pk=1)
        self.assertEqual(player.name, "John", "The first player's name is John.")

class GameTestCase(TestCase):
    fixtures = ['different_name.json']

    def test_correct_developer_name(self):
        game = Game.objects.get(pk=2)
        developer = Developer.objects.get(pk=1)
        self.assertEqual(game.developer, developer)

class OwnedGameTestCase(TestCase):
    fixtures = ['different_name.json']

    def test_correct_output(self):
        owned_game = OwnedGame.objects.get(pk=2)
        player = Player.objects.get(pk=1)
        game = Game.objects.get(pk=2)
        self.assertEqual(str(owned_game), "Player {} owns game {}.".format(player.name, game.title))


# Test that Game.price>=0