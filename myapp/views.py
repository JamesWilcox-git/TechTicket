from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm
from django.contrib import messages
import traceback

# welcome/home screen
def welcome(request):
    return render(request, 'welcome.html')

# login screen
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if user.user_type == 'admin':
                    return redirect('admin_dashboard')
                elif user.user_type == 'employee':
                    return redirect('employee_dashboard')
                else:
                    return redirect('normal_dashboard')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('welcome')

# signup screen
def signup(request):
    user_type = None
    if request.user.is_authenticated:
        user_type = request.user.user_type

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, user=request.user)
        if form.is_valid():
            user = form.save()
            if user.user_type == 'admin':
                    return redirect('admin_dashboard')
            elif user.user_type == 'employee':
                return redirect('employee_dashboard')
            else:
                return redirect('normal_dashboard')
        else:
            print("Form is not valid")
            print(form.errors)
    else:
        form = CustomUserCreationForm(user=request.user)
    
    return render(request, 'signup.html', {'form': form, 'user_type':user_type})

# admin_dashboard home screen
def admin_dashboard(request):
    username = request.user.username
    return render(request, 'admin_dashboard.html', {'username':username})

# employee_dashboard home screen
def employee_dashboard(request):
    username = request.user.username
    return render(request, 'employee_dashboard.html', {'username':username})

# normal_dashboard home screen
def normal_dashboard(request):
    username = request.user.username
    return render(request, 'normal_dashboard.html', {'username':username})

# calendar screen
def calendar(request):
    return render(request, 'calendar.html')

# employee hours screen
def employee_hours(request):
    return render(request, 'employee_hours.html')

# live chat screen
def live_chat(request):
    return render(request, 'live_chat.html')