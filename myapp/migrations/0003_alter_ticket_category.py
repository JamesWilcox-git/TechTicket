# Generated by Django 5.0.6 on 2024-06-29 22:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_alter_customuser_user_type_ticket'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='category',
            field=models.CharField(choices=[('repair', 'Repair Request'), ('account', 'Account Help'), ('tech_support', 'Technical Support'), ('account_management', 'Account Management'), ('general_inquiry', 'General Inquiry'), ('maintenance', 'Maintenance Request'), ('security', 'Security Issue'), ('customer_service', 'Customer Service'), ('other', 'Other')], max_length=50),
        ),
    ]