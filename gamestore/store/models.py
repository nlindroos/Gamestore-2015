from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# NOTE: Django sets variables names from e.g. player to player_id in the db when ForeignKey is used, but we only need to use player to refer to this field.

# Should we combine Highscore OwnedGame and Purchase, since each of these only add one column?

def validate_price(price):
    if price < 0:
        raise ValidationError("Price must be non-negative")

class Game(models.Model):
    def __str__(self):
        return self.title
    developer = models.ForeignKey(User, limit_choices_to={'groups__name': "Developers"})
    title = models.CharField(max_length=60, blank=False)
    url = models.URLField(blank=False, null=False, default="http://example.com")
    price = models.DecimalField(max_digits=5, decimal_places=2, null=False, default=0.00, validators=[validate_price])
    tags = models.TextField(null=False, default='', blank=True)
    description = models.TextField(null=False, default='', blank=False)
    img_url = models.URLField(null=True, blank=True, default="store/images/russia.jpeg")
    
    def get_tags(self):
        return [x.strip() for x in self.tags.split(',')] # FIXME: maybe could be better to strip these when saved?
        
    def get_tags_formatted(self):
        """
        Returns a string with each tag on a new line
        """
        return self.tags.replace(',', '\n')

class Highscore(models.Model):
    def __str__(self):
        return "Game: {}, player: {}, score: {}.".format(self.game, self.player, self.score)
    game = models.ForeignKey(Game)
    player = models.ForeignKey(User, limit_choices_to={'groups__name': "Players"})
    score = models.DecimalField(max_digits=11, decimal_places=2)
    date_time = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['game', '-score', 'date_time', 'player']

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
    fee = models.DecimalField(max_digits=5, decimal_places=2, null=False, default=0.00)
    payment_confirmed = models.BooleanField(default=False)

