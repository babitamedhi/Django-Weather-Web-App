# Generated by Django 5.0.7 on 2024-08-09 04:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_userdetail'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='UserDetail',
            new_name='user_details',
        ),
    ]
