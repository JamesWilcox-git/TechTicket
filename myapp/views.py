from django.shortcuts import render, redirect
#from django.contrib.auth import login
from .forms import CustomUserCreationForm
import traceback

# welcome/home screen
def welcome(request):
    return render(request, 'welcome.html')

# login screen
def login(request):
    return render(request, 'login.html')

def logout(request):
    return redirect('welcome')

# signup screen
def signup(request):
    if request.method == 'POST':
        print("POST request received")
        try:
            form = CustomUserCreationForm(request.POST)
            if form.is_valid():
                print("Form is valid")
                user = form.save()
                #login(request, user)
                return redirect('login')
            else:
                print("Form is not valid")
                print(form.errors)
        except Exception as e:
            print("An error occurred:")
            traceback.print_exc()  # This will print the full traceback to the console
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

# admin_user home screen
def admin_user(request):
    return render(request, 'admin_user.html')

# calendar screen
def calendar(request):
    return render(request, 'calendar.html')

# employee hours screen
def employee_hours(request):
    return render(request, 'employee_hours.html')

# live chat screen
def live_chat(request):
    return render(request, 'live_chat.html')