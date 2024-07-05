from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('employee_dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('normal_dashboard/', views.normal_dashboard, name='normal_dashboard'),
    path('admin_calendar/', views.admin_calendar, name='admin_calendar'),
    path('employee_calendar/', views.employee_calendar, name='employee_calendar'),
    path('chat/<str:room_name>/', views.chat_room, name='chat_room'),
    path('ticket_request/', views.ticket_request, name='ticket_request'),
    path('employee_view_tickets/', views.employee_view_tickets, name='employee_view_tickets'),
    path('view_tickets/', views.view_tickets, name='view_tickets'),
    path('ticket/<int:ticket_id>/', views.achat_ticket, name='achat_ticket'),
    path('save_chat_message/<int:ticket_id>', views.save_chat_message, name='save_chat_message'),
    path('update_ticket_status/<int:ticket_id>/', views.update_ticket_status, name='update_ticket_status'),
    path('update_ticket_time_estimate/<int:ticket_id>/', views.update_ticket_time_estimate, name='update_ticket_time_estimate'),
    path('update_ticket_time_spent/<int:ticket_id>/', views.update_ticket_time_spent, name='update_ticket_time_spent'),
]