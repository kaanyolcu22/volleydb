from django import forms
from django import forms

class PlayerForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)
    name = forms.CharField(max_length=100)
    surname = forms.CharField(max_length=100)
    date_of_birth = forms.DateField()
    height = forms.IntegerField()
    weight = forms.IntegerField()

class JuryForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)
    name = forms.CharField(max_length=100)
    surname = forms.CharField(max_length=100)
    nationality = forms.CharField(max_length=50)

class CoachForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)
    name = forms.CharField(max_length=100)
    surname = forms.CharField(max_length=100)
    nationality = forms.CharField(max_length=50)
