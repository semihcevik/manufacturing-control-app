# Generated by Django 4.2.16 on 2024-10-19 10:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('personnel', '0002_alter_customuser_department_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='department_id',
            new_name='department',
        ),
    ]
