from django.db import models
from django.contrib.auth.models import User

# NOTE: Django sets variables names from e.g. player to player_id in the db when ForeignKey is used, but we only need to use player to refer to this field.

# Should we combine Highscore OwnedGame and Purchase, since each of these only add one column?
'''
class Player(models.Model):
    def __str__(self):
        return self.name
    name = models.CharField(max_length=40)
    email = models.EmailField(max_length=254)


class Developer(models.Model):
    def __str__(self):
        return self.name
    name = models.CharField(max_length=40)
    email = models.EmailField(max_length=254)
'''

class Game(models.Model):
    def __str__(self):
        return self.title
    developer = models.ForeignKey(User, limit_choices_to={'groups__name': "Developers"})
    title = models.CharField(max_length=60)	# Added title, not defined in the project plan
    url = models.URLField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    tags = models.TextField()
    
    def get_tags(self):
        return self.tags.split(',')

class Highscore(models.Model):
    def __str__(self):
        return "Game: {}, player: {}, score: {}.".format(self.game, self.player, self.score)
    game = models.ForeignKey(Game)
    player = models.ForeignKey(User, limit_choices_to={'groups__name': "Players"})
    score = models.DecimalField(max_digits=11, decimal_places=2)
    date_time = models.DateTimeField(auto_now_add=True)

class OwnedGame(models.Model):
    def __str__(self):
        return "Player {} owns game {}.".format(self.player, self.game)
    player = models.ForeignKey(User, limit_choices_to={'groups__name': "Players"})
    game = models.ForeignKey(Game)
    game_state = models.TextField() # Should this be TextField?


class Purchase(models.Model):
    def __str__(self):
        return "Player {} has purchased the game {} for {}.".format(self.player, self.game, self.fee)
    player = models.ForeignKey(User, limit_choices_to={'groups__name': "Players"})
    game = models.ForeignKey(Game)
    date_time = models.DateTimeField(auto_now_add=True)
    fee = models.DecimalField(max_digits=5, decimal_places=2)

