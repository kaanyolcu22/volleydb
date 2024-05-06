from django.shortcuts import render, redirect
from django.db import connection
from .forms import JuryForm, PlayerForm, CoachForm

def home(request):
    return 

def login_view(request):
    context = {}
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user_type = get_user_type(username, password)
        if user_type:
            request.session['username'] = username
            request.session['user_type'] = user_type
            
            if user_type == 'DBManager':
                return redirect('manager_dashboard')
            elif user_type in ['Player', 'Jury', 'Coach']:
                return redirect('user_dashboard')
            else:
                context['error'] = 'Invalid user type'
        else:
            context['error'] = 'Invalid login credentials'

    return render(request, 'login.html', context)

def get_user_type(username, password):
    with connection.cursor() as cursor:
        for table in ['DBManager', 'Player', 'Jury', 'Coach']:
            cursor.execute(f"SELECT * FROM {table} WHERE username = %s AND password = %s", [username, password])
            if cursor.fetchone():
                return table
    return None

from django.db import connection

def save_user(data, user_type):
    try:
        with connection.cursor() as cursor:
            if user_type == 'Player':
                sql = """INSERT INTO Player (username, password, name, surname, date_of_birth, height, weight)
                         VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                params = (data['username'], data['password'], data['name'], data['surname'], data['date_of_birth'], data['height'], data['weight'])
            # Add similar blocks for 'Jury' and 'Coach' with appropriate SQL and parameters

            cursor.execute(sql, params)
            connection.commit()
            print("Insert successful")
    except Exception as e:
        print(f"An error occurred during SQL execution: {e}")


def manager_dashboard(request):
    if not request.session.get('user_type') == 'DBManager':
        return redirect('login')  # Security check

    player_form = PlayerForm(request.POST or None)
    jury_form = JuryForm(request.POST or None)
    coach_form = CoachForm(request.POST or None)

    if request.method == 'POST':
        if 'add_player' in request.POST:
            if player_form.is_valid():
                save_user(player_form.cleaned_data, 'Player')
                return redirect('manager_dashboard')  # Refresh or show success
            else:
                print(player_form.errors)  # Log form errors
        elif 'add_jury' in request.POST and jury_form.is_valid():
            save_user(jury_form.cleaned_data, 'Jury')
            return redirect('manager_dashboard')
        elif 'add_coach' in request.POST and coach_form.is_valid():
            save_user(coach_form.cleaned_data, 'Coach')
            return redirect('manager_dashboard')

    context = {
        'player_form': player_form,
        'jury_form': jury_form,
        'coach_form': coach_form
    }
    return render(request, 'manager_dashboard.html', context)

def user_dashboard(request):
    if request.session.get('user_type') not in ['Player', 'Jury', 'Coach']:
        return redirect('login')
    return render(request, 'user_dashboard.html')
