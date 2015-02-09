from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re

# NOTE: Django sets variables names from e.g. player to player_id in the db when ForeignKey is used, but we
# only need to use player to refer to this field.

def validate_price(price):
    if price < 0:
        raise ValidationError("Price must be non-negative")
                
class Game(models.Model):
    """
    Model representing Game objects.
    
    Attributes:
        title:          a string: name of the game (certain characters are not allowed)
        search_title:   a string: plain version of title to be used in searches (certain characters removed)
        developer:      a User object belonging to group Developers
        url:            a string: URL link to the game
        price:          a Decimal: price of the game (must be non-negative)
        tags:           a string: comma-separated list of tags to categorize the game by (no spaces allowed)
        description:    a string describing the game
        img_url:        a string: URL to an image of the game (optional)    
    """
    developer = models.ForeignKey(User, limit_choices_to={'groups__name': "Developers"})
    title = models.CharField(max_length=60, blank=False)
    search_title = models.CharField(max_length=60, null=False, default='')
    url = models.URLField(blank=False, null=False, default="http://example.com")
    price = models.DecimalField(max_digits=5, decimal_places=2, null=False, default=0.00, validators=[validate_price])
    tags = models.TextField(null=False, default='', blank=True)
    description = models.TextField(null=False, default='', blank=False)
    img_url = models.URLField(null=True, blank=True, default="")
    
    def __str__(self):
        return '<Game object (id: {}, title: {}, developer: {})>'.format(self.pk, self.title, self.developer)
    
    def get_tags(self):
        return [x for x in self.tags.split(',')]
    
    def save(self, *args, **kwargs):
        """
        Override save() method.
        Strips tags of all whitespace and sets them to lower case before saving them.
            - only characcters [a-zA-Z0-9_] are allowed in tags
        
        Sets the value of search_title based on title.
        search_title is a lower case version of title where:
            - leading and trailing spaces are removed
            - series of > 1 spaces are replaced by 1 space
            - the percent sign '%' is replaced by the word 'percent'
            - the ampersand '&' is replaced by the word 'and'
            - all other special characters are removed
        """
        # remove leading and trailing whitespace:
        tags = [x.strip() for x in self.tags.split(',')] 
        # exclude empty tags, convert to lower case and replace whitspace with underscores:
        tags = [re.sub(r'(\s|_)+', '_', x.lower()) for x in tags if x]
        # remove invalid characters and remove duplicates:
        tags = set(re.sub(r'[^a-zA-Z0-9_]', '', x) for x in tags)
        # limit to max 10 tags and rejoin:
        self.tags = ','.join(sorted(tags)[:10])
        
        # set search_title
        s_title = re.sub(r'(\s)+', ' ', self.title.lower().strip())
        s_title = s_title.replace('%', 'percent').replace('&', 'and')
        self.search_title = re.sub(r'[^\w\s]', '', s_title)
        
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
    """
    Model representing highscore objects.
    Each player may have only one highscore per game.
    
    Attributes:
        game:       a Game object
        player:     a User object belonging to group Players
        score:      a Decimal
        date_time:  a datetime object, when the score was set
        
    """
    game = models.ForeignKey(Game)
    player = models.ForeignKey(User, limit_choices_to={'groups__name': "Players"})
    score = models.DecimalField(max_digits=11, decimal_places=2)
    date_time = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['game', '-score', 'date_time', 'player']
        unique_together = (("player", "game"),)
        
    def __str__(self):
        return "<Highscore object (id:{}, game: {}, player: {}, score: {})>".format(self.game, self.player, self.score)

class OwnedGame(models.Model):
    """
    Model representing ownership of a game by a player.
    A player can own each game only once.
    
    Attributes:
        player:     a User object belonging to group Players
        game:       a Game object
        game_state: a game state string (JSON), for loading a saved game
    """
    player = models.ForeignKey(User, limit_choices_to={'groups__name': "Players"})
    game = models.ForeignKey(Game)
    game_state = models.TextField() # Should this be TextField?
    
    class Meta:
        unique_together = (("player","game"),)
        
    def __str__(self):
        return "<OwnedGame object (player: {}, game: {})>".format(self.player, self.game)


class Purchase(models.Model):
    """
    Model representing a purchase of a game by a player.
    A player can purchase each game only once.
    
    Attributes:
        player:             a User object belonging to group Players
        game:               a Game object
        date_time:          a datetime object, when the purchase was made
        fee:                a Decimal, how much was paid
        payment_confirmed:  a Boolean indicating whether the payment was successfully confirmed
        reference_number:   an integer, related to payment security
    """
    player = models.ForeignKey(User, limit_choices_to={'groups__name': "Players"})
    game = models.ForeignKey(Game)
    date_time = models.DateTimeField(auto_now_add=True)
    fee = models.DecimalField(max_digits=5, decimal_places=2, null=False, default=0.00)
    payment_confirmed = models.BooleanField(default=False)
    reference_number = models.IntegerField(default=0)
    
    class Meta:
        unique_together = (("player","game"),)
        
    def __str__(self):
        return "<Purchase object (player: {}, game: {}, fee: {})>".format(self.player, self.game, self.fee)

