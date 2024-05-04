from django import forms
from .models import User, Player

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password', 'name', 'surname'] 

class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['date_of_birth', 'weight', 'height']

