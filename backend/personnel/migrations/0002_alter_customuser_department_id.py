# Generated by Django 4.2.16 on 2024-10-19 10:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('departments', '0001_initial'),
        ('personnel', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='department_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='departments.departments'),
        ),
    ]
