from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from store.models import Game
from django.forms import ValidationError

import re

class MyRegistrationForm(UserCreationForm):
    GROUP_CHOICES = (
        ('Players', 'Players'),
        ('Developers', 'Developers'),
    )
    
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    group = forms.ChoiceField(choices=GROUP_CHOICES, required=True)
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'group', 'username', 'password1', 'password2']
        
    def save(self, commit=True):
        user = super(MyRegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        group = self.cleaned_data['group']        
        
        if commit:
            user.save()
            user.groups.add(Group.objects.get(name=group))
    
        return user

class GameForm(ModelForm):
    """
    Form for editing games and submitting new games.

    The tags attribute is an array input
    (<input id="tag1" name="tags[]"/> <input id="tag2" name="tags[]"/>)
    , which needs to be extracted from POST using request.POST.getlist().
    """
    class Meta:
        model = Game
        fields=['title', 'url', 'price', 'description', 'img_url']
        
    def __init__(self, *args, **kwargs):
        super(GameForm, self).__init__(*args, **kwargs)
        self.tags = args[0].getlist('tags[]') # first arg should be request.POST
        
    def clean(self):
        super(GameForm, self).clean()
        if not self.tags or not [x for x in self.tags if x]:
            raise ValidationError('At least one tag is required')
        for t in self.tags:
            if not re.match(r'^[a-zA-Z0-9_]*$', t):
                raise ValidationError('Tags may only contain letters, numbers and underscores')
        cd = self.cleaned_data
        cd['tags[]'] = self.tags
        return cd