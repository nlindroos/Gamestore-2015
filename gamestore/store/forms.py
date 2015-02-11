from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.forms import UserCreationForm
from store.models import Game
from django.forms import ValidationError, Form, ModelForm, EmailField, CharField

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
        
    def __init__(self, user, *args, **kwargs):
        super(GameForm, self).__init__(*args, **kwargs)
        self.tags = args[0].getlist('tags[]') # first arg should be request.POST
        self.user = user
        
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
        
    def save(self):
        g = super(GameForm, self).save(commit=False)
        g.tags = ",".join(self.cleaned_data.get('tags[]', []))
        g.developer = self.user # make sure in views.py that only the same dev can access
        g.save()
        return g
        
        
class ProfileForm(Form):
    """
    Form that lets the user change their email, first name and last name.
    """
    first_name = CharField()
    last_name = CharField()
    email = EmailField()
    
    def __init__(self, user, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.user = user
        
    def save(self):
        self.user.email = self.cleaned_data.get('email')
        self.user.first_name = self.cleaned_data.get('first_name')
        self.user.last_name = self.cleaned_data.get('last_name')
        self.user.save()
        return self.user
    
class PasswordForm(Form):
    """
    Form that lets the user change their password.
    """
    old_password = CharField(min_length=1) # don't give a long minimum length to old passwords
    password1 = CharField(min_length=8)
    password2 = CharField(min_length=8)
    
    def __init__(self, user, *args, **kwargs):
        super(PasswordForm, self).__init__(*args, **kwargs)
        self.user = user
    
    def clean(self):
        super(PasswordForm, self).clean()
        if self.cleaned_data.get('password1') != self.cleaned_data.get('password2'):
            error = ValidationError('Passwords do not match')
            self.add_error('password1', error)
            raise error
        if not self.user.check_password(self.cleaned_data.get('old_password', '')):
            error = ValidationError('Old password is incorrect')
            self.add_error('old_password', error)
            raise error
            
    def save(self):
        self.user.set_password(self.cleaned_data.get('password1'))
        self.user.save()
        return self.user
        