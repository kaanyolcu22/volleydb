# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from .models import DatabaseManager, User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse



def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if isinstance(user, DatabaseManager):
                return redirect('manager_dashboard') 
            return redirect('user_dashboard')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    return render(request, 'login.html')

@login_required
def manager_dashboard(request):
    if not isinstance(request.user, DatabaseManager):
        return HttpResponse("Unauthorized", status=403)
    return render(request, 'manager_dashboard.html')

@login_required
def user_dashboard(request):
    return render(request, 'user_dashboard.html')


def home(request):
    return HttpResponse("Hello, world. You're at the home page.")