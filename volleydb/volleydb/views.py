from django.shortcuts import render, redirect
from .forms import JuryForm, PlayerForm, CoachForm, MatchSessionForm
from django.contrib import messages
from .utils import get_user_type, save_user, update_stadium_name, delete_match, save_match_session, validate_jury,validate_stadium, validate_team,calculate_average_rating,validate_rating,submit_rating,update_jury_statistics
from django.db import connection



def home(request):
    return 

def login_view(request):
    
    global LOGGED_USERNAME
    context = {}
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user_type = get_user_type(username, password)
        if user_type:
            request.session['username'] = username
            request.session['user_type'] = user_type
            if user_type == 'DBManager':
                return redirect('manager')
            elif user_type == 'Player':
                return redirect('player')
            elif user_type == 'Coach':
                return redirect('coach')
            elif user_type == 'Jury':
                return redirect('jury')
            else:
                context['error'] = 'Invalid user type'
        else:
            context['error'] = 'Invalid login credentials'

    return render(request, 'login.html', context)



def stadium_list(request):
    if not request.session.get('user_type') == 'Coach':
        return redirect('login') 

    with connection.cursor() as cursor:
        cursor.execute("SELECT stadium_name, stadium_country FROM Stadium")
        stadiums = cursor.fetchall()

    return render(request, 'stadium_list.html', {'stadiums': stadiums})

def coach(request):
    
    
    coach_username = request.session.get('username')
    if not request.session.get('user_type') == 'Coach':
        return redirect('login')

    match_form = MatchSessionForm(request.POST or None) 
    print("Form initialized")


    if request.method == 'POST':
        print("POST request received")
        if 'delete_match' in request.POST:
            session_id = request.POST.get('delete_match')
            if session_id:
                print("Deleting session ID:", session_id) 
                success, msg = delete_match(session_id)
                if success:
                    messages.success(request, "Match session successfully deleted.")
                else:
                    messages.error(request, msg)
                return redirect('coach') 
            
        elif 'add_match' in request.POST and match_form.is_valid():
            print("Add match condition met")
            stadium_id = match_form.cleaned_data['stadium_id']
            jury_username = match_form.cleaned_data['jury_username']
            team_id = match_form.cleaned_data['team_id']
            print(team_id,coach_username)
            if not validate_stadium(stadium_id) :
                
                messages.error(request, "Invalid stadium.")
                return render(request, 'coach.html', {'match_form': match_form})

            if not validate_jury(jury_username) :
                
                messages.error(request, "Invalid jury.")
                return render(request, 'coach.html', {'match_form': match_form})
            
            if not validate_team(coach_username,team_id) :
                
                messages.error(request, "The team id not match with logged coach.")
                return render(request, 'coach.html', {'match_form': match_form})
            
            success, msg = save_match_session(match_form.cleaned_data)
            if success:
                messages.success(request, "Match session successfully added.")
            else:
                messages.error(request, msg)
            return redirect('coach')
            
            
    return render(request, 'coach.html')
            
def player(request):
    if not request.session.get('user_type') == 'Player':
        return redirect('login')

    username = request.session.get('username')
    if not username:
        return redirect('login')

    try:
        played_with, avg_height = player_query(username)
        context = {
            'played_with': played_with,
            'avg_height': avg_height
        }
        return render(request, 'player.html', context)
    except Exception as e:
        return render(request, 'player.html', {'error': str(e)})
        
        


def jury(request):
    if not request.session.get('user_type') == 'Jury':
        return redirect('login')
    
    username = request.session.get('username')
    if not username:
        return redirect('login')

    if request.method == 'POST':
        session_id = request.POST.get('session_id')
        rating = float(request.POST.get('rating')) 
        if validate_rating(session_id, username, rating):
            submit_rating(session_id, rating)
            messages.success(request, 'Rating successfully submitted.')
            average_rating, total_sessions = update_jury_statistics(username)
            messages.success(request, 'Average Rating and Total Rated Sessions Updated.')
        else:
            messages.error(request, 'Invalid session ID or rating cannot be submitted yet.')


    try:
        average_rating, total_sessions = calculate_average_rating(username)
    except Exception as e:
        return render(request, 'jury.html', {'error': str(e)})

    context = {
        'username': username,
        'average_rating': average_rating,
        'total_sessions': total_sessions
    }
    return render(request, 'jury.html', context)

def manager(request):
    if not request.session.get('user_type') == 'DBManager':
        return redirect('login')

    player_form = PlayerForm(request.POST or None)
    jury_form = JuryForm(request.POST or None)
    coach_form = CoachForm(request.POST or None)

    if request.method == 'POST':
        if 'add_player' in request.POST:
            if player_form.is_valid():
                print("Form Data:", player_form.cleaned_data) 
                save_user(player_form.cleaned_data, 'Player')
                return redirect('manager') 
            else:
                print(player_form.errors)
        elif 'add_jury' in request.POST and jury_form.is_valid():
            save_user(jury_form.cleaned_data, 'Jury')
            return redirect('manager')
        elif 'add_coach' in request.POST and coach_form.is_valid():
            save_user(coach_form.cleaned_data, 'Coach')
            return redirect('manager')
        
        elif 'update_stadium' in request.POST:
            old_name = request.POST.get('old_name')
            new_name = request.POST.get('new_name')
            success, msg = update_stadium_name(old_name, new_name)
            if success:
                return redirect('manager')
            else:
                messages.error(request, msg)
                return redirect('manager')

    context = {
        'player_form': player_form,
        'jury_form': jury_form,
        'coach_form': coach_form
    }
    return render(request, 'manager.html', context)