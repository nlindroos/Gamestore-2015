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
        return [x for x in self.tags.split(',')]
    
    def save(self, *args, **kwargs):
        """
        Override save() method.
        Strips tags of all whitespace and sets them to lower case before saving them.
        """
        self.tags = ','.join([x.strip().lower() for x in self.tags.split(',')])
        super(Game, self).save(*args, **kwargs)
        
        
    def get_related_games(self):
        """
        Returns a list of tuples containing:
            [0]: a game object that has at least one tag in common with this game
            [1]: a number (0..1) indicating how well the tags of both games match each other.
        """
        t1 = set(self.get_tags())
        if not t1:
            return []
        games = Game.objects.exclude(pk=self.pk)
        related = []
        for g in games:
            t2 = set(g.get_tags())
            isect = t1 & t2;
            union = t1 | t2;
            if isect:
                related.append((g, len(isect)/len(union)))
        return related
        

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

