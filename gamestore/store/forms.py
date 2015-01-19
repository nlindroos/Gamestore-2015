from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.forms import UserCreationForm
from django.forms.models import modelform_factory
from store.models import Game

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

GameForm = modelform_factory(Game, fields=('title', 'url', 'price', 'description', 'img_url'))
"""
Form for editing games and submitting new games.

The tags field/attribute is excluded because we need to pass tags input as an array
(<input id="tag1" name="tags[]"/> <input id="tag2" name="tags[]"/>), 
which django doesn't like and fails to validate the form. 
Therefore, we need to get that input directly from request.POST (see views.py).
"""