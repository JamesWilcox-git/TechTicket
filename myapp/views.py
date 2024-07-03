from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm, TicketForm
from django.contrib import messages
from .models import CustomUser, Ticket

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
            login(request, user)
            if user.user_type == 'admin':
                return redirect('admin_dashboard')
            elif user.user_type == 'employee':
                return redirect('employee_dashboard')
            elif user.user_type == 'normal':
                return redirect('normal_dashboard')
        else:
            messages.error(request, "Error creating account. Please try again.")
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request,error)
    else:
        form = CustomUserCreationForm(user=request.user)

    return render(request, 'signup.html', {'form': form, 'user_type': user_type})

@login_required # only logged in users should access this
def admin_dashboard(request):
     # only admin users can access this view
    if request.user.user_type != 'admin':
        logout(request) # log out user since they are redirected to login page
        return redirect('login')
    username = request.user.username
    return render(request, 'admin_dashboard.html', {'username': username})

@login_required # only logged in users should access this
def employee_dashboard(request):
     # only employee users can access this view
    if request.user.user_type != 'employee':
        logout(request) # log out user since they are redirected to login page
        return redirect('login')
    username = request.user.username
    return render(request, 'employee_dashboard.html', {'username': username})

@login_required # only logged in users should access this
def employee_view_tickets(request):
    # only employee users can access this view
    if request.user.user_type != 'employee':
        logout(request) # log out user since they are redirected to login page
        return redirect('login')
    user = request.user
    tickets = Ticket.objects.filter(assigned_employee_id = user.id)
    username = user.username
    return render(request, 'employee_view_tickets.html', {'username': username, 'tickets': tickets})

@login_required # only logged in users should access this
def normal_dashboard(request):
    # only normal users can access this view
    user = request.user
    if user.user_type != 'normal':
        logout(request) # log out user since they are redirected to login page
        return redirect('login')
    username = user.username
    return render(request, 'normal_dashboard.html', {'username': username})

@login_required # only logged in users should access this
def calendar(request):
    # only admin users can access this view
    if request.user.user_type != 'admin':
        logout(request) # log out user since they are redirected to login page
        return redirect('login')
    return render(request, 'calendar.html')

@login_required # only logged in users should access this
def employee_hours(request):
    # only staff users can access this view
    if request.user.user_type == 'normal':
        logout(request) # log out user since they are redirected to login page
        return redirect('login')
    user_type = request.user.user_type
    return render(request, 'employee_hours.html', {'user_type': user_type})

# live chat screen
def live_chat(request):
    user_type = request.user.user_type
    return render(request, 'live_chat.html', {'user_type': user_type})

@login_required # only logged in users should access this
def ticket_request(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            # !!!
            # change this when we start implementing the auto-assignment stuff
            # this is hard-coded: always assigns tickets to employeetest3
            ticket.assigned_employee_id = get_user("employeetest3").id
            ticket.status = "open"
            ticket.save()
            messages.success(request, 'Ticket submitted successfully!')
            return redirect('ticket_request')  # Redirect to the same page to show the message
        else:
            messages.error(request, 'Error submitting ticket. Please try again.')
    else:
        form = TicketForm()
    return render(request, 'ticket_request.html', {'form': form})

# normal user ticket view screen
@login_required
def view_tickets(request):
    tickets = Ticket.objects.filter(user=request.user)
    return render(request, 'view_tickets.html', {'tickets': tickets})

# ticket info screen
@login_required
def achat_ticket(request, ticket_id):
    # admins can see any ticket, normal/employee users can only see their own tickets
    current_user = request.user
    ticket_user_id = Ticket.objects.get(id=ticket_id).user.id
    ticket_assigned_e_id = Ticket.objects.get(id=ticket_id).assigned_employee.id
    if current_user.user_type == 'normal' and current_user.id != ticket_user_id:
        logout(request) # log out user since they are redirected to login page
        return redirect('login')
    elif current_user.user_type == 'employee' and current_user.id != ticket_assigned_e_id:
        logout(request) # log out user since they are redirected to login page
        return redirect('login') 
    ticket = Ticket.objects.get(id=ticket_id)
    return render(request, 'achat_ticket.html', {'ticket': ticket, 'current_user': current_user})



# helper functions
def get_user(username):
    try:
        user = CustomUser.objects.get(username=username)
        return user
    except:
        print("Error: User does not exist")
        return None
