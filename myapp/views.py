from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm, TicketForm, ChatMessageForm
from django.contrib import messages
from django.http import JsonResponse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .forms import CustomUserCreationForm, TicketForm, WorkHourForm
from .models import CustomUser, Ticket, WorkHour, ChatMessage
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
    return render(request, 'employee_dashboard.html', {'username': request.user.username})

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

def get_available_employee():
    now = timezone.now()  # current date and time (used to make sure we only get future work hours)
    now_datetime = datetime.combine(now.date(), now.time())
    workhour_data = WorkHour.objects.all()
    available_workhours = [
        wh for wh in workhour_data
        if datetime.combine(wh.date, wh.end_time) >= now_datetime]
    
    # order by end time
    available_workhours.sort(key=lambda wh: datetime.combine(wh.date, wh.end_time))
    if not available_workhours:
        return "admintest1"  # no employee available --> assign to admin

    earliest_workhour = available_workhours[0]
    earliest_employee = earliest_workhour.employee
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