# Generated by Django 5.0.7 on 2024-08-05 10:40

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Day',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('category', models.CharField(choices=[('weekend', 'Weekend'), ('public_holiday', 'Public Holiday')], max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='InconvenienceRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request_id', models.CharField(max_length=100, unique=True)),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('submitted', 'Submitted'), ('manager_approval', 'Manager Approval'), ('work_in_review', 'Work in Review'), ('manager_approval_2', '2nd Manager Approval'), ('hr_approval', 'HR Approval'), ('completed', 'Completed')], default='draft', max_length=20)),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='inconvenience_requests', to='user.department')),
                ('department_rep', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='department_representative_requests', to=settings.AUTH_USER_MODEL)),
                ('hr', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='hr_requests', to=settings.AUTH_USER_MODEL)),
                ('line_manager', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='line_manager_requests', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='InconvenienceRequestLine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('job_description', models.CharField()),
                ('staff_id', models.IntegerField()),
                ('no_of_weekend', models.IntegerField()),
                ('no_of_ph', models.IntegerField()),
                ('no_of_days', models.IntegerField()),
                ('amount', models.FloatField()),
                ('response', models.CharField(blank=True, choices=[('accepted', 'Accepted'), ('rejected', 'Rejected')], max_length=20, null=True)),
                ('response_time', models.DateTimeField(blank=True, null=True)),
                ('attendance_status', models.CharField(blank=True, choices=[('present', 'Present'), ('absent', 'Absent')], max_length=20, null=True)),
                ('days', models.ManyToManyField(related_name='inconvenience_request_lines', to='inconvenience_allowance.day')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='inconvenience_request_lines', to=settings.AUTH_USER_MODEL)),
                ('inconvenience_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lines', to='inconvenience_allowance.inconveniencerequest')),
            ],
        ),
    ]
