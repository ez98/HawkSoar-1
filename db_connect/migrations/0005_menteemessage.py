# Generated by Django 4.2 on 2023-04-19 02:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('db_connect', '0004_rename_mentormeetings_mentormeeting'),
    ]

    operations = [
        migrations.CreateModel(
            name='MenteeMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Message', models.TextField(max_length=1000)),
                ('M_Date', models.DateField(auto_now_add=True)),
                ('A_number', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='db_connect.mentees')),
                ('Mid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Mentor_ID', to='db_connect.mentees')),
            ],
        ),
    ]
