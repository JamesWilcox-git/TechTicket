from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('employee', 'Employee'),
        ('normal', 'Normal User'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='normal')
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

    def __str__(self):
        return self.username

class Ticket(models.Model):
    CATEGORY_CHOICES = [
        ('repair', 'Repair Request'),
        ('account', 'Account Help'),
        ('tech_support', 'Technical Support'),
        ('account_management', 'Account Management'),
        ('general_inquiry', 'General Inquiry'),
        ('maintenance', 'Maintenance Request'),
        ('security', 'Security Issue'),
        ('customer_service', 'Customer Service'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    status = models.CharField(max_length=50, choices=[
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed'),
    ], default='open')  # Added default value here
    description = models.TextField()
    submitted_at = models.DateTimeField(default=timezone.now)
    assigned_employee = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    time_estimate = models.FloatField(default=0)  # Added default value here
    time_spent = models.FloatField(default=0)  # Added default value here

    def __str__(self):
        return f"{self.get_category_display()} - {self.user.username}"

class WorkHour(models.Model):
    employee = models.CharField(max_length=255)  # Employee name
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee} - {self.date} - {self.start_time} to {self.end_time}"
