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
    path('calendar/', views.calendar, name='calendar'),
    path('employee_hours/', views.employee_hours, name='employee_hours'),
    path('live_chat/', views.live_chat, name='live_chat'),
    path('ticket_request/', views.ticket_request, name='ticket_request'),
]