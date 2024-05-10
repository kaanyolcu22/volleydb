from django import forms
from django.db import connection
from django.forms import DateInput


def fetch_teams():
    with connection.cursor() as cursor:
        cursor.execute("SELECT team_name FROM Team")
        return [(row[0], str(row[0])) for row in cursor.fetchall()]

def fetch_positions():
    with connection.cursor() as cursor:
        cursor.execute("SELECT position_name FROM Position")
        return [(row[0], str(row[0])) for row in cursor.fetchall()]
        

class PlayerForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)
    name = forms.CharField(max_length=100)
    surname = forms.CharField(max_length=100)
    date_of_birth = forms.DateField(
        widget=DateInput(format='%Y.%m.%d'),
        input_formats=['%Y.%m.%d']
    )
    height = forms.IntegerField()
    weight = forms.IntegerField()
    team = forms.ChoiceField(choices=[])
    position = forms.ChoiceField(choices=[])

    def __init__(self, *args, **kwargs):
        super(PlayerForm, self).__init__(*args, **kwargs)
        self.fields['team'].choices = fetch_teams()
        self.fields['position'].choices = fetch_positions()
        
class MatchSessionForm(forms.Form):
    team_id = forms.IntegerField()
    stadium_id = forms.IntegerField()
    date = forms.DateField(widget=DateInput(attrs={'type': 'date'}))
    time_slot = forms.IntegerField()
    jury_username = forms.CharField(max_length=100) 

    def clean_time_slot(self):
        time_slot = self.cleaned_data['time_slot']
        if not 1 <= time_slot <= 4:
            raise forms.ValidationError('Time slot must be between 1 and 4.')
        return time_slot

class RateSessionForm(forms.Form):
    session_id = forms.IntegerField(label='Session ID', min_value=0)
    rating = forms.FloatField(label='Rating', min_value=1, max_value=5) 



    
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
