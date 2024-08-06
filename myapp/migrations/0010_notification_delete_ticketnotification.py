# Generated by Django 5.0.6 on 2024-07-27 07:55

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0009_alter_ticketnotification_notified_employee'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_resolved', models.BooleanField(default=False)),
                ('notified_employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('ticket', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='myapp.ticket')),
            ],
        ),
        migrations.DeleteModel(
            name='TicketNotification',
        ),
    ]