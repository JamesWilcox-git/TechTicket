from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm, TicketForm, ChatMessageForm
from django.contrib import messages
from django.http import JsonResponse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .forms import CustomUserCreationForm, TicketForm, WorkHourForm, ResetPasswordForm, ForgotPasswordForm
from .models import CustomUser, Ticket, WorkHour, ChatMessage, TicketNotification
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)
from django.http import HttpResponse

# Welcome/home screen
def welcome(request):
    return render(request, 'welcome.html')

# Login screen
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


def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            if not CustomUser.objects.filter(email=email, username=username).exists():
                messages.error(request, "User does not exist. Please try again.")
                return redirect('forgot_password')
            else:
                return redirect(reverse('reset_password', kwargs={'email': email, 'username': username}))
    else:
        form = ForgotPasswordForm()

    return render(request, 'forgot_password.html', {'form': form})

def reset_password(request, email, username):
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            user = CustomUser.objects.get(email=email, username=username)
            user.set_password(new_password)
            user.save()
            print(f"Resetting password for {username} ({email}) to {new_password}")
            return redirect('password_reset_done')
    else:
        form = ResetPasswordForm(initial={'email': email, 'username': username})

    return render(request, 'reset_password.html', {'form': form, 'email': email, 'username': username})

def password_reset_done(request):
    return render(request, 'password_reset_done.html')







# Signup screen
def signup(request):
    user_type = request.user.user_type if request.user.is_authenticated else None

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, user=request.user)
        if form.is_valid():
            user = form.save()
            login(request, user)
            if user.user_type == 'admin':
                return redirect('admin_dashboard')
            elif user.user_type == 'employee':
                return redirect('employee_dashboard')
            else:
                return redirect('normal_dashboard')
        else:
            messages.error(request, "Error creating account. Please try again.")
    else:
        form = CustomUserCreationForm(user=request.user)

    return render(request, 'signup.html', {'form': form, 'user_type': user_type})

@login_required
def admin_dashboard(request):
    if request.user.user_type != 'admin':
        logout(request)
        return redirect('login')
    return render(request, 'admin_dashboard.html', {'username': request.user.username})

@login_required
def employee_dashboard(request):
    if request.user.user_type != 'employee':
        logout(request)
        return redirect('login')
    notifications = TicketNotification.objects.filter(notified_employee=request.user, is_resolved=False)
    print(notifications)
    return render(request, 'employee_dashboard.html', {'username': request.user.username, 'notifications': notifications})

@login_required
def employee_view_tickets(request):
    if request.user.user_type != 'employee':
        logout(request)
        return redirect('login')
    tickets = Ticket.objects.filter(assigned_employee=request.user)
    return render(request, 'employee_view_tickets.html', {'username': request.user.username, 'tickets': tickets})

@login_required
def normal_dashboard(request):
    if request.user.user_type != 'normal':
        logout(request)
        return redirect('login')
    return render(request, 'normal_dashboard.html', {'username': request.user.username})

@login_required # only logged in users should access this
def admin_calendar(request):
    # only admins users can access this view
    user = request.user
    if user.user_type != 'admin':
        logout(request) # log out user since they are redirected to login page
        return redirect('login')
    return render(request, 'admin_calendar.html', {'user': user})

@login_required
def admin_view_tickets(request):
    if request.user.user_type != 'admin':
        logout(request)
        return redirect('login')
    tickets = Ticket.objects.all()
    employees = CustomUser.objects.filter(user_type='employee')
    return render(request, 'admin_view_tickets.html', {'tickets': tickets, 'employees': employees})

@login_required
def employee_hours(request):
    if request.user.user_type != 'employee':
        return redirect('login')
    
    employee_name = request.user.username
    work_hours = WorkHour.objects.filter(employee=employee_name)
    return render(request, 'employee_hours.html', {'work_hours': work_hours, 'user_type': request.user.user_type})

@login_required # only logged in users should access this
# live chat screen
def chat_room(request, room_name):
    user = request.user
    return render(request, 'chat.html', {'room_name': room_name, 'user': user})

# used for auto assignment of tickets to employees
def get_available_employee():
    now_datetime = datetime.now()  # Current date and time
    workhour_data = WorkHour.objects.all()
    # Filter out work hours that are currently open
    available_workhours = [
        wh for wh in workhour_data
        if datetime.combine(wh.date, wh.start_time) <= now_datetime <= datetime.combine(wh.date, wh.end_time)
    ]
    # Sort the available work hours by start time
    sorted_workhours = sorted(available_workhours, key=lambda wh: datetime.combine(wh.date, wh.start_time))
    if sorted_workhours:
        earliest_workhour = sorted_workhours[0]
    else:
        return "admintest1"  # no employee available --> assign to admin


    print("Date for auto assignment: ")
    print()
    print("Available work hours:")
    print(available_workhours)
    print("Sorted work hours:")
    print(sorted_workhours)
    print()
    print("Earliest work hour:")
    print(earliest_workhour)


    # if the employee has 5 or more tickets assigned, assign to admin
    if earliest_workhour.num_tickets_assigned > 5:
        return "admintest1"
    earliest_employee = earliest_workhour.employee
    earliest_workhour.num_tickets_assigned += 1
    return earliest_employee

@login_required
def ticket_request(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            # auto assignment of ticket to employee
            assigned_employee_username = get_available_employee()
            ticket.assigned_employee_id = get_user(assigned_employee_username).id
            ticket.status = "open"
            ticket.time_estimate = 0
            ticket.time_spent = 0
            ticket.save()
            TicketNotification.objects.create(ticket=ticket, notified_employee=get_user(assigned_employee_username))
            messages.success(request, 'Ticket submitted successfully!')
            return redirect('ticket_request')
        else:
            messages.error(request, 'Error submitting ticket. Please try again.')
    else:
        form = TicketForm()
    return render(request, 'ticket_request.html', {'form': form})

@login_required
def view_tickets(request):
    tickets = Ticket.objects.filter(user=request.user)
    return render(request, 'view_tickets.html', {'tickets': tickets})

@login_required
def achat_ticket(request, ticket_id):
    current_user = request.user
    ticket = Ticket.objects.get(id=ticket_id)
    if current_user.user_type == 'normal' and current_user != ticket.user:
        logout(request)
        return redirect('login')
    elif current_user.user_type == 'employee' and current_user != ticket.assigned_employee:
        logout(request)
        return redirect('login') 
    ticket = Ticket.objects.get(id=ticket_id)
    messages = ChatMessage.objects.filter(ticket_id=ticket_id)
    return render(request, 'achat_ticket.html', {'ticket': ticket, 'current_user': current_user, 'messages': messages})

def get_user(username):
    try:
        return CustomUser.objects.get(username=username)
    except CustomUser.DoesNotExist:
        print("Error: User does not exist")
        return None

def update_ticket_assigned_employee(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    if request.method == 'POST':
        assigned_employee_id = request.POST.get('assigned_employee')
        if assigned_employee_id:
            assigned_employee = get_object_or_404(CustomUser, id=assigned_employee_id)
            ticket.assigned_employee = assigned_employee
            ticket.save()
            return redirect('admin_view_tickets')
    
    return render(request, 'your_template.html', {
        'ticket': ticket,
        'employees': CustomUser.objects.all(),
    })

def update_ticket_status(request, ticket_id):
    if request.method == 'POST':
        status = request.POST.get('status')
        ticket = Ticket.objects.get(id=ticket_id)
        ticket.status = status
        ticket.save()
        return redirect('employee_view_tickets')

def update_ticket_time_estimate(request, ticket_id):
    if request.method == 'POST':
        time_estimate = request.POST.get('time_estimate')
        ticket = Ticket.objects.get(id=ticket_id)
        ticket.time_estimate = float(time_estimate)
        ticket.save()
        notifications = TicketNotification.objects.filter(ticket=ticket)
        notifications.update(is_resolved=True)
        return redirect('employee_view_tickets')
    
def update_ticket_time_spent(request, ticket_id):
    if request.method == 'POST':
        time_spent = request.POST.get('time_spent')
        ticket = Ticket.objects.get(id=ticket_id)
        ticket.time_spent = float(time_spent)
        ticket.save()
        return redirect('employee_view_tickets')

@login_required
@csrf_exempt
def add_work_hour(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            form = WorkHourForm(data)
            if form.is_valid():
                form.save()
                return JsonResponse({'success': 'Work hours saved successfully!'})
            else:
                logger.error("Form errors: %s", form.errors)
                return JsonResponse({'error': 'Invalid data', 'details': form.errors}, status=400)
        except json.JSONDecodeError as e:
            logger.error("JSON decode error: %s", str(e))
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error("Unexpected error: %s", str(e))
            return JsonResponse({'error': 'Unexpected error'}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required
def view_work_hours_json(request, date):
    if request.user.user_type != 'admin':
        logout(request)
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    work_hours = WorkHour.objects.filter(date=date).values('employee', 'start_time', 'end_time')
    return JsonResponse({'work_hours': list(work_hours)})

@csrf_exempt
@login_required
def clear_work_hours(request, date):
    if request.user.user_type != 'admin':
        logout(request)
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    WorkHour.objects.filter(date=date).delete()
    return JsonResponse({'success': 'Work hours cleared'})

@login_required
def view_employee_hours(request):
    if request.user.user_type != 'employee':
        return redirect('login')
    
    employee_name = request.user.username
    work_hours = WorkHour.objects.filter(employee=employee_name)
    return render(request, 'employee_hours.html', {'work_hours': work_hours, 'user_type': request.user.user_type})


    
@login_required
def save_chat_message(request, ticket_id):
    if request.method == 'POST':
        form = ChatMessageForm(request.POST)
        if form.is_valid():
            # Create a new ChatMessage object but don't save it yet
            new_message = form.save(commit=False)
            new_message.sender = request.user
            new_message.ticket_id = ticket_id
            # Optionally do additional processing here
            new_message.save()  # Save the message to the database
            return redirect('achat_ticket', ticket_id=ticket_id)
    else:
        form = ChatMessageForm()
    return HttpResponse(status=400)  # Respond with HTTP 400 Bad Request if form is invalid or method is not POST