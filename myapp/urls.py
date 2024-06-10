from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('admin_user/', views.admin_user, name='admin_user'),
    path('calendar/', views.calendar, name='calendar'),
    path('employee_hours/', views.employee_hours, name='employee_hours'),
    path('live_chat/', views.live_chat, name='live_chat'),
]