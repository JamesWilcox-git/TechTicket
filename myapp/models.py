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
    ])
    description = models.TextField()
    submitted_at = models.DateTimeField(default=timezone.now)
    assigned_employee = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    time_estimate = models.FloatField()
    time_spent = models.FloatField()

    def __str__(self):
        return f"{self.get_category_display()} - {self.user.username}"

class ChatMessage(models.Model):
    ticket = models.ForeignKey(Ticket, related_name='chat_messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
